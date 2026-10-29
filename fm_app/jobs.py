"""Import coordination, lifecycle and bounded analysis cache."""
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import logging
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import uuid

from fm_app.analysis import STYLES, analyze
from fm_app.contracts import ACTIVE_STATES, MAX_SAVE, cache_key
from fm_app.dataset import load_dataset
from fm_app.fm26 import ENGINE_VERSION
from fm_app.storage import ROOT, STORAGE, ImportStorage, atomic_json, read_json

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self, storage=STORAGE):
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='TouchlineImport')
        self.jobs, self.cache = OrderedDict(), OrderedDict()
        self.store = ImportStorage(storage)
        self.storage = self.store.root
        self.dataset, self.restore_error = None, None
        self.closing = threading.Event()
        self.process = None
        self._restore()

    def _restore(self):
        try:
            folder = self.store.current()
            if folder is None:
                return
            data = load_dataset(folder/'output')
            bundle = read_json(folder/'output/analysis_bundle.json', {})
            if not isinstance(bundle, dict):
                bundle = {}
            styles = bundle.get('styles', {}) if bundle.get('engine_version') == ENGINE_VERSION and bundle.get('dataset_id') == data['id'] else {}
            if not isinstance(styles, dict):
                styles = {}
            for style in STYLES:
                result = styles.get(style)
                if not isinstance(result, dict) or not all(k in result for k in ('profiles','tactics','evaluated_formations')) or not isinstance(result.get('profiles'), dict) or not isinstance(result.get('tactics'), list) or result.get('style') != style:
                    result = analyze(data, style, data['default_primary_slot'])
                result['profiles'] = {int(uid): p for uid, p in result['profiles'].items()}
                # JSON object keys become strings, including maps nested in proposals.
                for entry in [result, *result.get('tactics', []), result.get('requested_tactic')]:
                    if isinstance(entry, dict) and isinstance(entry.get('surplus_players'), dict):
                        entry['surplus_players'] = {int(uid): p for uid, p in entry['surplus_players'].items()}
                self.cache[cache_key(data['id'], style, data['default_primary_slot'])] = result
            self.dataset = data
        except (ValueError, KeyError, TypeError, OSError) as error:
            self.cache.clear()
            self.restore_error = f'No se pudo restaurar la última partida: {error}. Podés cargarla nuevamente.'

    def busy(self):
        with self.lock:
            return any(j['status'] in ACTIVE_STATES for j in self.jobs.values())

    def reserve(self, status, message):
        with self.lock:
            if self.closing.is_set():
                raise ValueError('La aplicación se está cerrando.')
            if self.busy():
                return None
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {'status': status, 'message': message, 'progress': 0,
                                 'started_at': datetime.now(timezone.utc).isoformat()}
            while len(self.jobs) > 128:
                self.jobs.popitem(last=False)
            return job_id

    def progress(self, job_id, status, message, percent=None):
        with self.lock:
            self.jobs.setdefault(job_id, {}).update(status=status, message=message, progress=percent)
            if status in ('done','error','cancelled'):
                self.jobs[job_id]['finished_at'] = datetime.now(timezone.utc).isoformat()

    def import_local_save(self, save_path):
        path = Path(save_path).resolve()
        self._validate_save(path)
        job_id = self.reserve('copying', f'Copiando {path.name}…')
        if job_id:
            try:
                self.executor.submit(self._copy_and_import, job_id, path)
            except Exception as error:
                self.progress(job_id, 'error', str(error))
                raise
        return job_id

    def reimport_current(self, dataset_id):
        """Upgrade the current snapshot without depending on the watch folder or FM saving again."""
        with self.lock:
            if not self.dataset or self.dataset['id'] != dataset_id:
                raise ValueError('La partida cambió. Volvé a cargar la táctica.')
            current = self.store.current()
            if current is None or not (current/'save.fm').is_file():
                raise ValueError('Esta importación no conserva la copia .fm. Volvé a importar tu partida.')
            metadata = read_json(current/'import.json', {})
            job_id = self.reserve('copying', 'Actualizando la lectura táctica de tu partida…')
            if job_id:
                try:
                    self.executor.submit(self._reimport_snapshot, job_id, current/'save.fm', metadata)
                except Exception as error:
                    self.progress(job_id, 'error', str(error))
                    raise
            return job_id

    def _reimport_snapshot(self, job_id, source, metadata):
        try:
            folder = self.store.folder(job_id)
            folder.mkdir(parents=True)
            target = folder/'save.fm'
            shutil.copy2(source, target)
            self._validate_save(target)
            atomic_json(folder/'import.json', {**metadata, 'imported_at':datetime.now(timezone.utc).isoformat()})
            self.import_save(job_id, target, folder)
        except Exception as error:
            self.progress(job_id, 'error', str(error))
            logger.exception('Falló la actualización de lectura táctica')

    @staticmethod
    def signature(path):
        st = path.stat()
        return [str(path.resolve()).casefold(), st.st_mtime_ns, st.st_size]

    @staticmethod
    def _validate_save(path):
        if not path.is_file() or path.suffix.lower() != '.fm':
            raise ValueError('Elegí un archivo de partida .fm.')
        if not 1000 <= path.stat().st_size <= MAX_SAVE:
            raise ValueError('La partida debe tener entre 1000 bytes y 400 MB.')
        with path.open('rb') as stream:
            if stream.read(6) != b'\x02\x01fmf.':
                raise ValueError('Cabecera de partida FM incompatible.')

    def _copy_and_import(self, job_id, path):
        try:
            before = self.signature(path)
            folder = self.store.folder(job_id)
            folder.mkdir(parents=True)
            target = folder/'save.fm'
            shutil.copy2(path, target)
            if before != self.signature(path):
                raise ValueError('La partida cambió durante la copia. Esperá a que FM termine de guardar.')
            self._validate_save(target)
            atomic_json(folder/'import.json', {'filename': path.name, 'source_path': str(path),
                'source_signature': before, 'imported_at': datetime.now(timezone.utc).isoformat(), 'auto_synced': True})
            self.import_save(job_id, target, folder)
        except Exception as error:
            self.progress(job_id, 'error', str(error))
            logger.exception('Falló la copia de la partida')

    def _extract(self, source, folder):
        with (folder/'extraction.log').open('w', encoding='utf-8') as log:
            with self.lock:
                if self.closing.is_set():
                    raise InterruptedError('Importación cancelada al cerrar.')
                if getattr(sys, 'frozen', False):
                    cmd = [sys.executable, '--extract-save', str(source), '--output', str(folder/'output')]
                else:
                    executable = str(Path(sys.executable).with_name('python.exe')) if sys.platform == 'win32' and Path(sys.executable).name.lower() == 'pythonw.exe' else sys.executable
                    cmd = [executable, '-B', '-m', 'fm_app.extraction', str(source), '--output', str(folder/'output')]
                self.process = subprocess.Popen(cmd,
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                process = self.process
            try:
                code = process.wait(timeout=300)
                if self.closing.is_set():
                    raise InterruptedError('Importación cancelada al cerrar.')
                if code:
                    raise ValueError('No se pudo extraer la plantilla. Verificá FM26 y un único club gestionado. Se conserva el análisis anterior.')
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
                raise ValueError('La lectura superó los cinco minutos. Se conserva el análisis anterior.')
            finally:
                with self.lock:
                    self.process = None

    def import_save(self, job_id, source, folder):
        try:
            self.progress(job_id, 'reading', 'Leyendo primer equipo, inferiores y cedidos…', 20)
            self._extract(source, folder)
            if self.closing.is_set():
                raise InterruptedError('Importación cancelada al cerrar.')
            data = load_dataset(folder/'output')
            styles = {}
            for index, style in enumerate(STYLES):
                if self.closing.is_set():
                    raise InterruptedError('Importación cancelada al cerrar.')
                self.progress(job_id, 'analyzing', f"Evaluando diez esquemas: {STYLES[style]['name']} ({index+1}/{len(STYLES)})…", 60 + index*9)
                styles[style] = analyze(data, style, data['default_primary_slot'])
            metadata = read_json(folder/'import.json', {})
            metadata['completed_at'] = datetime.now(timezone.utc).isoformat()
            atomic_json(folder/'import.json', metadata)
            atomic_json(folder/'output/analysis_bundle.json', {'engine_version': ENGINE_VERSION, 'dataset_id': data['id'], 'styles': styles})
            with self.lock:
                if self.closing.is_set():
                    raise InterruptedError('Importación cancelada al cerrar.')
                self.store.publish(job_id)
                self.dataset, self.restore_error = data, None
                self.cache.clear()
                self.cache.update({cache_key(data['id'], style, data['default_primary_slot']): result for style, result in styles.items()})
                self.progress(job_id, 'done', f"Análisis listo: {data['club']}.", 100)
            try:
                self.store.prune(protected=[job_id])
            except Exception:
                logger.exception('No se pudo completar la retención de copias')
        except InterruptedError as error:
            self.progress(job_id, 'cancelled', str(error))
        except Exception as error:
            self.progress(job_id, 'error', str(error))
            logger.exception('Falló la importación')

    def close(self):
        self.closing.set()
        with self.lock:
            process = self.process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            except OSError:
                pass
        self.executor.shutdown(wait=True, cancel_futures=True)
        with self.lock:
            for job_id, job in self.jobs.items():
                if job['status'] in ACTIVE_STATES:
                    self.progress(job_id, 'cancelled', 'Importación cancelada al cerrar.')
