from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from fm_app.jobs import AppState
from fm_app.watcher import SaveWatcher
from fixtures import fake_save


class SyncTests(unittest.TestCase):
    def setup_monitor(self,tmp):
        root=Path(tmp);state=AppState(root/'imports');self.addCleanup(state.close)
        games=root/'games';games.mkdir()
        watcher=SaveWatcher(state,root/'sync.json');watcher.configure(folder=str(games))
        return state,watcher,games

    def test_status_and_configuration_are_isolated(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp)
            self.assertEqual(watcher.get_status()['state'],'idle')
            fake_save(games/'Career.fm')
            self.assertEqual(watcher.get_status()['active_file'],'Career.fm')
            watcher.configure(target_save='Career.fm',enabled=False)
            self.assertEqual(watcher.get_status()['state'],'paused')
            watcher.configure(target_save='auto');self.assertIsNone(watcher.config['target_save'])

    def test_sync_is_acknowledged_only_after_success(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp);fake_save(games/'Career.fm')
            with patch.object(state,'_copy_and_import'):
                job=watcher.trigger_sync();state.executor.submit(lambda:None).result(timeout=5)
            self.assertIsNone(watcher.last_imported_sig);self.assertIsNone(watcher.last_sync_time)
            self.assertEqual(watcher.get_status()['state'],'syncing')
            state.progress(job,'done','ok',100)
            self.assertEqual(watcher.get_status()['state'],'watching')
            self.assertIsNotNone(watcher.last_imported_sig);self.assertIsNotNone(watcher.last_sync_time)

    def test_failed_extraction_can_be_retried(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp);fake_save(games/'Career.fm')
            with patch.object(state,'_copy_and_import'):
                job=watcher.trigger_sync();state.executor.submit(lambda:None).result(timeout=5)
            state.progress(job,'error','incompatible')
            self.assertEqual(watcher.get_status()['state'],'error')
            self.assertIsNone(watcher.last_imported_sig)
            with patch.object(state,'_copy_and_import'):
                retry=watcher.trigger_sync();state.executor.submit(lambda:None).result(timeout=5)
            self.assertNotEqual(job,retry)

    def test_busy_trigger_returns_an_error_without_sticking(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp);fake_save(games/'Career.fm')
            job=state.reserve('reading','busy')
            with self.assertRaises(ValueError):watcher.trigger_sync()
            self.assertFalse(watcher.is_syncing)
            state.progress(job,'error','done')

    def test_rejects_path_escape_and_invalid_configuration(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp)
            for name in ('../other.fm','C:\\other.fm','other.txt'):
                with self.subTest(name=name),self.assertRaises(ValueError):watcher.trigger_sync(name)
            for kwargs in ({'folder':'relative/path'},{'enabled':'false'},{'target_save':'../other.fm'}):
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):watcher.configure(**kwargs)

    def test_restore_uses_saved_signature_instead_of_current_file_stat(self):
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp);save=fake_save(games/'Career.fm')
            from fm_app.storage import atomic_json
            folder=state.store.folder('a'*32);folder.mkdir(parents=True)
            old=['old-path',1,2006]
            atomic_json(folder/'import.json',{'filename':save.name,'source_path':str(save),'source_signature':old,'imported_at':'2026-10-23T12:00:00Z'})
            state.store.publish('a'*32)
            restored=SaveWatcher(state,Path(tmp)/'sync.json')
            self.assertEqual(restored.last_imported_sig,old)
            self.assertNotEqual(restored.last_imported_sig,state.signature(save))

    def test_legacy_import_reuses_signature_only_when_full_hash_matches(self):
        import hashlib
        from fm_app.storage import atomic_json
        with TemporaryDirectory() as tmp:
            state,watcher,games=self.setup_monitor(tmp);save=fake_save(games/'Legacy.fm')
            folder=state.store.folder('b'*32);(folder/'output').mkdir(parents=True)
            digest=hashlib.sha256(save.read_bytes()).hexdigest()
            atomic_json(folder/'import.json',{'filename':save.name,'source_path':str(save)})
            atomic_json(folder/'output/validation.json',{'save_sha256':digest})
            state.store.publish('b'*32)
            restored=SaveWatcher(state,Path(tmp)/'sync.json')
            self.assertEqual(restored.last_imported_sig,state.signature(save))
            save.write_bytes(save.read_bytes()+b'changed')
            changed=SaveWatcher(state,Path(tmp)/'sync.json')
            self.assertIsNone(changed.last_imported_sig)
