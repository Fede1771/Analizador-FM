"""Save monitoring with acknowledged completion and bounded retries."""
from datetime import datetime, timezone
import logging
from pathlib import Path
import threading
import time

from fm_app.contracts import ACTIVE_STATES
from fm_app.storage import atomic_json, read_json, valid_import_id

logger = logging.getLogger(__name__)
DEFAULT_GAMES_DIR = Path.home()/'Documents'/'Sports Interactive'/'Football Manager 26'/'games'


class SaveWatcher:
    def __init__(self, app_state, config_file=None):
        self.state = app_state
        self.config_path = Path(config_file) if config_file else app_state.storage.parent/'sync_config.json'
        self._lock = threading.RLock()
        self._config_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        defaults = {'enabled': True, 'watch_folder': str(DEFAULT_GAMES_DIR), 'target_save': None, 'poll_interval': 2.0}
        saved = read_json(self.config_path, {})
        self.config = {**defaults, **saved} if isinstance(saved, dict) else defaults
        try:
            self._validate_config(self.config)
        except ValueError:
            self.config = defaults
        self.last_imported_sig = None
        self.last_imported_name = None
        self.last_sync_time = None
        self.last_sync_save = None
        self.last_error = None
        self.pending = None
        self.retry_at = 0
        self.failures = 0
        self.failed_signature = None
        self._init_current_signature()

    @staticmethod
    def _filename(value):
        if not isinstance(value, str) or not value.strip() or Path(value).name != value or any(c in value for c in ('/','\\',':')) or not value.lower().endswith('.fm'):
            raise ValueError('Elegí el nombre de una partida .fm dentro de la carpeta configurada.')
        return value

    @classmethod
    def _validate_config(cls, cfg):
        if type(cfg.get('enabled')) is not bool or not isinstance(cfg.get('watch_folder'), str) or not cfg['watch_folder'].strip():
            raise ValueError('Configuración de sincronización inválida.')
        if not Path(cfg['watch_folder']).is_absolute():
            raise ValueError('La carpeta debe tener una ruta absoluta.')
        if cfg.get('target_save') is not None:
            cls._filename(cfg['target_save'])
        interval = cfg.get('poll_interval', 2)
        if type(interval) not in (int, float) or not 1 <= interval <= 60:
            raise ValueError('Intervalo inválido.')

    def _init_current_signature(self):
        try:
            folder = self.state.store.current()
            if folder:
                meta = read_json(folder/'import.json', {})
                self.last_imported_sig = meta.get('source_signature')
                # Older imports lack a signature. Only trust the current file after
                # checking its full content against the validated snapshot hash.
                source = meta.get('source_path')
                if self.last_imported_sig is None and isinstance(source, str):
                    path = Path(source)
                    if path.is_file():
                        import hashlib
                        before = self.state.signature(path)
                        with path.open('rb') as stream:
                            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                        report = read_json(folder/'output/validation.json', {})
                        if digest == report.get('save_sha256') and before == self.state.signature(path):
                            self.last_imported_sig = before
                self.last_imported_name = self.last_sync_save = meta.get('filename')
                self.last_sync_time = meta.get('completed_at') or meta.get('imported_at')
        except (ValueError, OSError):
            pass

    @property
    def watch_folder(self):
        with self._lock:
            return Path(self.config['watch_folder'])

    @property
    def is_syncing(self):
        with self._lock:
            return self.pending is not None

    def configure(self, folder=None, target_save=None, enabled=None):
        # File writes and state snapshots never nest the watcher/state locks.
        with self._config_lock:
            with self._lock:
                cfg = dict(self.config)
            if folder is not None:
                if not isinstance(folder, str):
                    raise ValueError('Ruta inválida.')
                cfg['watch_folder'] = folder.strip()
            if target_save is not None:
                cfg['target_save'] = None if target_save == 'auto' else target_save
            if enabled is not None:
                cfg['enabled'] = enabled
            self._validate_config(cfg)
            atomic_json(self.config_path, cfg)
            with self._lock:
                self.config = cfg
                self.retry_at = 0
        return self.get_status()

    def list_saves(self):
        folder = self.watch_folder
        result = []
        try:
            for path in folder.glob('*.fm'):
                try:
                    if not path.is_file() or path.is_symlink():
                        continue
                    st = path.stat()
                    result.append({'filename': path.name, 'path': str(path), 'size_bytes': st.st_size,
                        'size_mb': round(st.st_size/1024**2, 1), 'mtime': st.st_mtime,
                        'modified_at': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                        'date_label': datetime.fromtimestamp(st.st_mtime).strftime('%d/%m/%Y %H:%M:%S')})
                except OSError:
                    continue
        except OSError:
            pass
        return sorted(result, key=lambda s: s['mtime'], reverse=True)

    def get_active_save_path(self):
        with self._lock:
            folder, target = Path(self.config['watch_folder']), self.config.get('target_save')
        if target:
            path = folder/self._filename(target)
            return path if path.is_file() and not path.is_symlink() else None
        saves = self.list_saves()
        return Path(saves[0]['path']) if saves else None

    def _refresh_pending(self):
        with self._lock:
            pending = dict(self.pending) if self.pending else None
        if pending is None:
            return
        with self.state.lock:
            job = dict(self.state.jobs.get(pending['job_id'], {}))
        if not job or job.get('status') in ACTIVE_STATES:
            return
        metadata = read_json(self.state.store.folder(pending['job_id'])/'import.json', {}) if job['status'] == 'done' else {}
        with self._lock:
            if not self.pending or self.pending['job_id'] != pending['job_id']:
                return
            if job['status'] == 'done':
                self.last_imported_sig = metadata.get('source_signature', pending['signature'])
                self.last_imported_name = self.last_sync_save = pending['filename']
                self.last_sync_time = job['finished_at']
                self.last_error, self.failures, self.retry_at = None, 0, 0
            else:
                self.last_error = job.get('message', 'No se pudo actualizar la partida.')
                self.failures += 1
                self.failed_signature = pending['signature']
                self.retry_at = time.monotonic() + min(60, 2**min(self.failures, 6))
            self.pending = None

    def get_status(self):
        self._refresh_pending()
        saves = self.list_saves()
        with self._lock:
            cfg, pending, error = dict(self.config), self.pending, self.last_error
            last_time, last_save = self.last_sync_time, self.last_sync_save
        folder_exists = Path(cfg['watch_folder']).is_dir()
        active = next((s for s in saves if s['filename'] == cfg['target_save']), None) if cfg['target_save'] else next(iter(saves), None)
        status = 'paused' if not cfg['enabled'] else 'folder_not_found' if not folder_exists else 'syncing' if pending else 'error' if error else 'watching' if active else 'idle'
        return {**cfg, 'folder_exists': folder_exists, 'state': status,
                'active_file': active['filename'] if active else None,
                'active_file_size_mb': active['size_mb'] if active else None,
                'available_saves': saves, 'last_sync_time': last_time, 'last_sync_save': last_save,
                'last_error': error, 'job_id': pending['job_id'] if pending else None}

    def trigger_sync(self, filename=None):
        self._refresh_pending()
        folder = self.watch_folder
        path = folder/self._filename(filename) if filename else self.get_active_save_path()
        if path is None or not path.is_file() or path.is_symlink():
            raise ValueError('No se encontró la partida en la carpeta configurada.')
        with self._lock:
            if self.pending:
                raise ValueError('Ya hay una sincronización en curso.')
            # Reserve locally before submitting; never acquire AppState.lock under this lock.
            self.pending = {'job_id': None, 'filename': path.name, 'signature': self.state.signature(path)}
        try:
            signature = self.state.signature(path)
            job_id = self.state.import_local_save(path)
            if job_id is None:
                raise ValueError('Ya hay una importación en curso.')
            with self._lock:
                self.pending = {'job_id': job_id, 'filename': path.name, 'signature': signature}
                self.last_error = None
            return job_id
        except Exception:
            with self._lock:
                self.pending = None
            raise

    def _check_and_sync(self):
        self._refresh_pending()
        with self._lock:
            if not self.config['enabled'] or self.pending or time.monotonic() < self.retry_at:
                return
            previous = self.last_imported_sig
        if self.state.busy():
            return
        path = self.get_active_save_path()
        if path is None:
            return
        try:
            signature = self.state.signature(path)
            if signature == previous:
                return
            if self._stop.wait(1.5) or signature != self.state.signature(path):
                return
            self.state._validate_save(path)
            self.trigger_sync(path.name)
        except (ValueError, OSError) as error:
            with self._lock:
                self.last_error = str(error)
                self.retry_at = time.monotonic() + 5

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run_loop, name='SaveWatcher', daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=3)

    def _run_loop(self):
        while not self._stop.is_set():
            try:
                self._check_and_sync()
            except Exception as error:
                logger.exception('Falló el monitor')
                with self._lock:
                    self.last_error = str(error)
            with self._lock:
                interval = self.config['poll_interval']
            self._stop.wait(interval)
