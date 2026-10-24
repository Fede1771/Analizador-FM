"""Tests for live save watcher, local imports and sync configuration."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch, MagicMock

from fm_app.server import AppState, ROOT, load_dataset
from fm_app.watcher import SaveWatcher


class SyncTests(unittest.TestCase):
    def fake_save(self, path, club_name="Club Test"):
        path.parent.mkdir(parents=True, exist_ok=True)
        # FM header b'\x02\x01fmf.' followed by padding
        path.write_bytes(b'\x02\x01fmf.' + b'\x00' * 2000)

    def test_watcher_status_and_configure(self):
        with TemporaryDirectory(dir=ROOT / '.tmp') as tmp:
            tmp_path = Path(tmp)
            storage = tmp_path / 'storage'
            games = tmp_path / 'games'
            cfg_file = tmp_path / 'sync_config.json'
            games.mkdir()

            state = AppState(storage=storage)
            watcher = SaveWatcher(state, config_file=cfg_file)
            
            # Configure to point to our test folder
            status = watcher.configure(folder=str(games), enabled=True, target_save='auto')
            self.assertTrue(status['enabled'])
            self.assertEqual(status['watch_folder'], str(games))
            self.assertTrue(status['folder_exists'])
            self.assertIsNone(status['target_save'])
            self.assertEqual(status['available_saves'], [])
            self.assertEqual(status['state'], 'idle')

            # Create two fake saves
            save1 = games / 'Career_1.fm'
            self.fake_save(save1)
            time.sleep(0.05)
            save2 = games / 'Career_2.fm'
            self.fake_save(save2)

            saves = watcher.list_saves()
            self.assertEqual(len(saves), 2)
            self.assertEqual(saves[0]['filename'], 'Career_2.fm')  # Newest first

            status2 = watcher.get_status()
            self.assertEqual(status2['active_file'], 'Career_2.fm')
            self.assertEqual(status2['state'], 'watching')

            # Configure specific target save
            watcher.configure(target_save='Career_1.fm')
            self.assertEqual(watcher.get_active_save_path().name, 'Career_1.fm')

            # Pause watcher
            watcher.configure(enabled=False)
            self.assertEqual(watcher.get_status()['state'], 'paused')

            state.executor.shutdown()

    def test_import_local_save_dispatches_pipeline(self):
        with TemporaryDirectory(dir=ROOT / '.tmp') as tmp:
            tmp_path = Path(tmp)
            storage = tmp_path / 'storage'
            games = tmp_path / 'games'
            games.mkdir()
            save_file = games / 'MyClub.fm'
            self.fake_save(save_file)

            state = AppState(storage=storage)
            
            with patch.object(state, 'import_save') as mock_import:
                job_id = state.import_local_save(save_file)
                self.assertIsNotNone(job_id)
                self.assertIn(job_id, state.jobs)
                self.assertEqual(state.jobs[job_id]['status'], 'reading')
                
                # Check imported folder
                folder = storage / job_id
                self.assertTrue((folder / 'save.fm').exists())
                meta = json.loads((folder / 'import.json').read_text(encoding='utf-8'))
                self.assertEqual(meta['filename'], 'MyClub.fm')
                self.assertTrue(meta['auto_synced'])

            state.executor.shutdown()


if __name__ == '__main__':
    unittest.main()
