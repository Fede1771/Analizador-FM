import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from fm_app.analysis import STYLES
from fm_app.server import AppState, ROOT, load_dataset


class ImportTests(unittest.TestCase):
    def snapshot(self, output):
        output.mkdir(parents=True,exist_ok=True)
        report=json.loads((ROOT/'data/output/validation.json').read_text(encoding='utf-8'))
        report['club']['name']='Club de prueba'
        report['managed_clubs'][0]['club_name']='Club de prueba'
        report['managed_clubs'][0]['manager_name']='Entrenador de prueba'
        report['save_sha256']='a'*64
        rows=json.loads((ROOT/'data/output/brighton_full.json').read_text(encoding='utf-8'))
        rows=[p for p in rows if p['team_slot']==0][:12]+[p for p in rows if p['team_slot']!=0][:3]
        for p in rows:
            p['club_name']='Club de prueba'
        (output/'squad_full.json').write_text(json.dumps(rows),encoding='utf-8')
        (output/'loaned_out.json').write_text('[]',encoding='utf-8')
        (output/'validation.json').write_text(json.dumps(report),encoding='utf-8')

    def test_fresh_install_needs_only_uploaded_save_not_brighton_exports(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            state=AppState(Path(tmp))
            self.assertIsNone(state.dataset)
            self.assertEqual(state.cache,{})
            state.executor.shutdown()

    def test_generic_snapshot_has_its_own_club_and_roster(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            output=Path(tmp)/'output'
            self.snapshot(output)
            dataset=load_dataset(output)
            self.assertEqual(dataset['club'],'Club de prueba')
            self.assertEqual(dataset['manager'],'Entrenador de prueba')
            self.assertEqual(len(dataset['players']),15)
            self.assertEqual(len(dataset['loans']),0)
            self.assertIn('slot_labels',dataset)
            self.assertEqual(dataset['slot_labels'][0],'Primer equipo')

    def test_import_computes_all_styles_before_done_and_restores_them(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            storage=Path(tmp)
            state=AppState(storage)
            job='b'*32
            folder=storage/job
            folder.mkdir()
            self.snapshot(folder/'output')
            with patch('fm_app.server.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')):
                state.import_save(job,folder/'save.fm',folder)
            self.assertEqual(state.jobs[job]['status'],'done')
            self.assertEqual(len(state.cache),len(STYLES))
            bundle=json.loads((folder/'output/analysis_bundle.json').read_text(encoding='utf-8'))
            self.assertEqual(set(bundle['styles']),set(STYLES))
            for result in bundle['styles'].values():
                self.assertEqual(len(result['academy']),3)
                self.assertEqual(len(result['profiles']),15)
                self.assertEqual(len(result['tactics']),3)
            restored=AppState(storage)
            self.assertEqual(restored.dataset['club'],'Club de prueba')
            self.assertEqual(len(restored.cache),len(STYLES))
            state.executor.shutdown()
            restored.executor.shutdown()

    def test_failed_import_preserves_current_data(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            state=AppState(Path(tmp))
            previous={'id':'previous','club':'Anterior'}
            state.dataset=previous
            folder=Path(tmp)/('c'*32)
            folder.mkdir()
            with patch('fm_app.server.subprocess.run',return_value=SimpleNamespace(returncode=1,stdout='',stderr='Invalid save')):
                state.import_save('c'*32,folder/'save.fm',folder)
            self.assertIs(state.dataset,previous)
            self.assertEqual(state.jobs['c'*32]['status'],'error')
            self.assertFalse((Path(tmp)/'current.json').exists())
            state.executor.shutdown()

    def test_engine_update_replaces_outdated_explanations(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            storage=Path(tmp); name='d'*32; output=storage/name/'output'
            self.snapshot(output)
            (storage/'current.json').write_text(json.dumps({'folder':name}),encoding='utf-8')
            (output/'analysis_bundle.json').write_text(json.dumps({'engine_version':1,'dataset_id':'a'*16,'styles':{'possession':{'outdated':True}}}),encoding='utf-8')
            state=AppState(storage)
            result=state.cache[('a'*16,'possession',0,())]
            self.assertNotIn('outdated',result)
            self.assertIn('in_possession',next(iter(result['profiles'].values())))
            state.executor.shutdown()

    def test_corrupt_last_snapshot_does_not_prevent_loading_screen(self):
        with TemporaryDirectory(dir=ROOT/'.tmp') as tmp:
            (Path(tmp)/'current.json').write_text('{broken',encoding='utf-8')
            state=AppState(Path(tmp))
            self.assertIsNone(state.dataset)
            self.assertIsNotNone(state.restore_error)
            state.executor.shutdown()


if __name__=='__main__':
    unittest.main()
