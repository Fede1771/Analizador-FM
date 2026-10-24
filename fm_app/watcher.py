"""Background watcher for Football Manager 26 save files with auto-sync."""
import json
import logging
import os
from pathlib import Path
import shutil
import threading
import time
from datetime import datetime, timezone

logger = logging.getLogger('fm_app.watcher')

DEFAULT_GAMES_DIR = Path.home() / 'Documents' / 'Sports Interactive' / 'Football Manager 26' / 'games'
# Specific known path if default differs
CUSTOM_GAMES_DIR = Path(r"C:\Users\feder\Documents\Sports Interactive\Football Manager 26\games")


class SaveWatcher:
    def __init__(self, app_state, config_file=None):
        self.state = app_state
        self.root = getattr(app_state, 'storage', Path('data/imports')).resolve().parents[1]
        self.config_path = Path(config_file) if config_file else self.root / 'data' / 'sync_config.json'
        
        # Load or init config
        self.config = self._load_config()
        self._lock = threading.RLock()
        self._thread = None
        self._running = False
        
        self.last_imported_sig = None  # (mtime, size)
        self.last_imported_name = None
        self.last_sync_time = None
        self.last_sync_save = None
        self.last_error = None
        self.is_syncing = False

        # If current imported save exists, register its signature if possible
        self._init_current_signature()

    def _init_current_signature(self):
        try:
            pointer = self.state.storage / 'current.json'
            if pointer.exists():
                folder_name = json.loads(pointer.read_text(encoding='utf-8')).get('folder')
                if folder_name:
                    meta_path = self.state.storage / folder_name / 'import.json'
                    if meta_path.exists():
                        meta = json.loads(meta_path.read_text(encoding='utf-8'))
                        self.last_imported_name = meta.get('filename')
                        self.last_sync_save = meta.get('filename')
                        self.last_sync_time = meta.get('imported_at')
                        source_path = meta.get('source_path')
                        if source_path and Path(source_path).exists():
                            st = Path(source_path).stat()
                            self.last_imported_sig = (st.st_mtime, st.st_size)
        except Exception as e:
            logger.debug("Could not determine current save signature: %s", e)

    def _load_config(self):
        default_folder = CUSTOM_GAMES_DIR if CUSTOM_GAMES_DIR.exists() else DEFAULT_GAMES_DIR
        cfg = {
            'enabled': True,
            'watch_folder': str(default_folder),
            'target_save': None,  # None means auto-detect newest .fm file
            'poll_interval': 2.0
        }
        if self.config_path.exists():
            try:
                saved = json.loads(self.config_path.read_text(encoding='utf-8'))
                if isinstance(saved, dict):
                    cfg.update(saved)
            except Exception as e:
                logger.warning("Error reading sync config, using defaults: %s", e)
        return cfg

    def _save_config(self):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            logger.error("Error saving sync config: %s", e)

    def configure(self, folder=None, target_save=None, enabled=None):
        with self._lock:
            if folder is not None:
                self.config['watch_folder'] = str(folder).strip()
            if target_save is not None:
                self.config['target_save'] = target_save.strip() if target_save and target_save.strip() != 'auto' else None
            if enabled is not None:
                self.config['enabled'] = bool(enabled)
            self._save_config()
            return self.get_status()

    @property
    def watch_folder(self):
        return Path(self.config.get('watch_folder', str(DEFAULT_GAMES_DIR)))

    def list_saves(self):
        folder = self.watch_folder
        if not folder.exists() or not folder.is_dir():
            return []
        saves = []
        try:
            for p in folder.glob('*.fm'):
                try:
                    st = p.stat()
                    saves.append({
                        'filename': p.name,
                        'path': str(p),
                        'size_bytes': st.st_size,
                        'size_mb': round(st.st_size / (1024 * 1024), 1),
                        'mtime': st.st_mtime,
                        'date_label': datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
                    })
                except OSError:
                    continue
        except OSError as e:
            logger.warning("Error listing saves: %s", e)
        saves.sort(key=lambda s: s['mtime'], reverse=True)
        return saves

    def get_active_save_path(self):
        """Returns the Path to the save file that should be tracked, or None."""
        folder = self.watch_folder
        if not folder.exists():
            return None
        target = self.config.get('target_save')
        if target:
            cand = folder / target
            return cand if cand.exists() and cand.is_file() else None
        
        saves = self.list_saves()
        return Path(saves[0]['path']) if saves else None

    def get_status(self):
        with self._lock:
            folder = self.watch_folder
            folder_exists = folder.exists() and folder.is_dir()
            active_path = self.get_active_save_path() if folder_exists else None
            
            # Determine state
            if not self.config.get('enabled', True):
                state_str = 'paused'
            elif not folder_exists:
                state_str = 'folder_not_found'
            elif self.is_syncing:
                state_str = 'syncing'
            elif active_path:
                state_str = 'watching'
            else:
                state_str = 'idle'

            return {
                'enabled': self.config.get('enabled', True),
                'watch_folder': str(folder),
                'folder_exists': folder_exists,
                'target_save': self.config.get('target_save'),
                'active_file': active_path.name if active_path else None,
                'active_file_size_mb': round(active_path.stat().st_size / (1024*1024), 1) if active_path and active_path.exists() else None,
                'available_saves': self.list_saves() if folder_exists else [],
                'last_sync_time': self.last_sync_time,
                'last_sync_save': self.last_sync_save,
                'last_error': self.last_error,
                'state': state_str
            }

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, name='SaveWatcherThread', daemon=True)
            self._thread.start()
            logger.info("SaveWatcher started on %s", self.watch_folder)

    def stop(self):
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            logger.info("SaveWatcher stopped")

    def _is_app_busy(self):
        with self.state.lock:
            return any(j['status'] in ('uploading', 'reading', 'analyzing') for j in self.state.jobs.values())

    def trigger_sync(self, filename=None):
        """Forces immediate import of specified filename or newest save."""
        with self._lock:
            folder = self.watch_folder
            if not folder.exists():
                raise FileNotFoundError(f"Carpeta no encontrada: {folder}")
            if filename:
                cand = folder / filename
                if not cand.exists():
                    raise FileNotFoundError(f"Partida no encontrada: {cand}")
            else:
                cand = self.get_active_save_path()
                if not cand:
                    raise FileNotFoundError("No se encontraron partidas .fm en la carpeta.")
            
            st = cand.stat()
            return self._perform_import(cand, (st.st_mtime, st.st_size))

    def _perform_import(self, save_path, signature):
        self.is_syncing = True
        self.last_error = None
        try:
            job_id = self.state.import_local_save(save_path)
            if job_id:
                self.last_imported_sig = signature
                self.last_imported_name = save_path.name
                self.last_sync_save = save_path.name
                self.last_sync_time = datetime.now(timezone.utc).isoformat()
            return job_id
        except Exception as e:
            self.last_error = str(e)
            logger.exception("Error triggering local save import: %s", e)
            raise
        finally:
            self.is_syncing = False

    def _check_and_sync(self):
        if not self.config.get('enabled', True):
            return
        if self._is_app_busy() or self.is_syncing:
            return

        cand = self.get_active_save_path()
        if not cand or not cand.exists():
            return

        try:
            st = cand.stat()
            mtime, size = st.st_mtime, st.st_size
        except OSError:
            return

        # Must have reasonable size
        if size < 1000:
            return

        current_sig = (mtime, size)
        if current_sig == self.last_imported_sig:
            return

        # Stabilization check: wait 1.5 seconds and verify size and mtime are unchanged
        time.sleep(1.5)
        try:
            st2 = cand.stat()
            if st2.st_mtime != mtime or st2.st_size != size:
                # File is actively being written by FM26; wait for next cycle
                return
            
            # Verify file can be read and check header
            with cand.open('rb') as stream:
                head = stream.read(6)
                if head != b'\x02\x01fmf.':
                    return
        except (PermissionError, OSError):
            # FM26 holds exclusive write lock; wait for completion
            return

        # Verify not busy before starting
        if self._is_app_busy():
            return

        logger.info("New or modified FM26 save detected: %s (%d bytes). Triggering auto-sync.", cand.name, size)
        self._perform_import(cand, current_sig)

    def _run_loop(self):
        interval = float(self.config.get('poll_interval', 2.0))
        while self._running:
            try:
                self._check_and_sync()
            except Exception as e:
                self.last_error = str(e)
                logger.error("Error in watcher loop: %s", e)
            
            # Sleep in small increments for responsive shutdown
            slept = 0.0
            step = 0.25
            while slept < interval and self._running:
                time.sleep(step)
                slept += step
