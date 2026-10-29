from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from fm_app.jobs import AppState
from fm_app.contracts import cache_key
from fm_app.fm26 import ENGINE_VERSION
from fm_app.tactics import STYLES
from fixtures import write_snapshot, fake_save


class ImportTests(unittest.TestCase):
    def state(self,temp):
        state=AppState(Path(temp)/'imports');self.addCleanup(state.close);return state

    def test_fresh_install_needs_no_existing_exports(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp)
            self.assertIsNone(state.dataset);self.assertEqual(state.cache,{})

    def test_generic_snapshot_and_stable_career_identity(self):
        with TemporaryDirectory() as tmp:
            a=write_snapshot(Path(tmp)/'a');b=write_snapshot(Path(tmp)/'b','b'*64)
            self.assertEqual(a['club'],'Club de prueba')
            self.assertNotEqual(a['id'],b['id']);self.assertEqual(a['career_id'],b['career_id'])

    def test_import_precomputes_and_restores_the_exact_cache_keys(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);job='b'*32;folder=state.store.folder(job)
            write_snapshot(folder/'output')
            with patch.object(state,'_extract'):
                state.import_save(job,folder/'save.fm',folder)
            self.assertEqual(state.jobs[job]['status'],'done')
            self.assertEqual(len(state.cache),len(STYLES))
            for style in STYLES:
                result=state.cache[cache_key(state.dataset['id'],style,0)]
                self.assertEqual(result['evaluated_formations'],10)
            restored=AppState(state.storage);self.addCleanup(restored.close)
            self.assertEqual(restored.cache,state.cache)

    def test_failed_import_preserves_current_data(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);previous={'id':'previous','club':'Anterior'};state.dataset=previous
            folder=state.store.folder('c'*32);folder.mkdir(parents=True)
            with patch.object(state,'_extract',side_effect=ValueError('incompatible')):
                state.import_save('c'*32,folder/'save.fm',folder)
            self.assertIs(state.dataset,previous);self.assertEqual(state.jobs['c'*32]['status'],'error')
            self.assertFalse((state.storage/'current.json').exists())

    def test_tactic_upgrade_reuses_current_snapshot_and_preserves_original_import(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'imports';old=root/('f'*32)
            write_snapshot(old/'output');fake_save(old/'save.fm')
            (old/'import.json').write_text(json.dumps({'filename':'Mi club.fm','source_path':'original/Mi club.fm'}))
            (root/'current.json').write_text(json.dumps({'folder':'f'*32}))
            original=(old/'save.fm').read_bytes()
            state=self.state(tmp)
            def extract(source, folder):
                self.assertNotEqual(source, old/'save.fm')
                write_snapshot(folder/'output')
                (folder/'output/tactics.json').write_text(json.dumps({'schema_version':2,'available':True,'records':[]}))
            with patch.object(state,'_extract',side_effect=extract):
                job=state.reimport_current(state.dataset['id'])
                state.executor.submit(lambda:None).result(timeout=30)
            self.assertEqual(state.jobs[job]['status'],'done')
            self.assertEqual(state.dataset['stored_tactics']['schema_version'],2)
            self.assertEqual(state.dataset['source']['filename'],'Mi club.fm')
            self.assertEqual((old/'save.fm').read_bytes(),original)
            self.assertEqual(state.store.current(),state.store.folder(job))

    def test_tactic_upgrade_submission_failure_does_not_leave_app_busy(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'imports';old=root/('f'*32)
            write_snapshot(old/'output');fake_save(old/'save.fm')
            (root/'current.json').write_text(json.dumps({'folder':'f'*32}))
            state=self.state(tmp)
            with patch.object(state.executor,'submit',side_effect=RuntimeError('closed')):
                with self.assertRaisesRegex(RuntimeError,'closed'):
                    state.reimport_current(state.dataset['id'])
            self.assertFalse(state.busy())

    def test_engine_update_replaces_outdated_explanations(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'imports';output=root/('d'*32)/'output';write_snapshot(output)
            root.joinpath('current.json').write_text(json.dumps({'folder':'d'*32}))
            (output/'analysis_bundle.json').write_text(json.dumps({'engine_version':1,'dataset_id':'a'*16,'styles':{'possession':{'outdated':True}}}))
            state=AppState(root);self.addCleanup(state.close)
            self.assertNotIn('outdated',state.cache[cache_key('a'*16,'possession',0)])

    def test_corrupt_snapshot_keeps_loading_available(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'current.json').write_text('{broken')
            state=AppState(root);self.addCleanup(state.close)
            self.assertIsNone(state.dataset);self.assertIsNotNone(state.restore_error)

    def test_copy_failure_ends_job_and_allows_retry(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);save=fake_save(Path(tmp)/'games/test.fm')
            with patch('fm_app.jobs.shutil.copy2',side_effect=PermissionError('copy failed')):
                job=state.import_local_save(save)
                state.executor.submit(lambda:None).result(timeout=5)
            self.assertEqual(state.jobs[job]['status'],'error');self.assertFalse(state.busy())
            with patch.object(state,'import_save',side_effect=lambda j,*args:state.progress(j,'done','ok',100)):
                retry=state.import_local_save(save);state.executor.submit(lambda:None).result(timeout=5)
            self.assertEqual(state.jobs[retry]['status'],'done')

    def test_mutating_save_is_not_published(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);save=fake_save(Path(tmp)/'test.fm')
            with patch.object(state,'signature',side_effect=[['file',1,2006],['file',2,2006]]):
                job=state.import_local_save(save);state.executor.submit(lambda:None).result(timeout=5)
            self.assertEqual(state.jobs[job]['status'],'error');self.assertIsNone(state.dataset)

    def test_shutdown_cancels_active_work(self):
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);job=state.reserve('reading','test')
            state.close();self.assertEqual(state.jobs[job]['status'],'cancelled')
            with self.assertRaises(ValueError):state.reserve('reading','test')

    def test_shutdown_terminates_the_extraction_child(self):
        import subprocess
        import sys
        with TemporaryDirectory() as tmp:
            state=self.state(tmp);job=state.reserve('reading','active child')
            process=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(60)'],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            state.process=process
            state.close()
            self.assertIsNotNone(process.poll())
            self.assertEqual(state.jobs[job]['status'],'cancelled')

    def test_invalid_bundle_shape_is_rebuilt(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'imports';output=root/('e'*32)/'output';write_snapshot(output)
            root.joinpath('current.json').write_text(json.dumps({'folder':'e'*32}))
            (output/'analysis_bundle.json').write_text('[]')
            state=AppState(root);self.addCleanup(state.close)
            self.assertIsNotNone(state.dataset)
            self.assertEqual(len(state.cache),4)
