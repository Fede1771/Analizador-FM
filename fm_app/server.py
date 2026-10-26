"""Loopback HTTP transport; domain logic lives in validated services."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import mimetypes
from pathlib import Path
import threading
from urllib.parse import unquote
import webbrowser

from fm_app.analysis import STYLES, analyze
from fm_app.recommendations import simulate_formation
from fm_app.current_tactic import audit_tactic
from fm_app.contracts import ACTIVE_STATES, MAX_SAVE, analysis_parameters, cache_key, validate_preferences
from fm_app.dataset import load_dataset
from fm_app.jobs import AppState
from fm_app.storage import ROOT, STORAGE, atomic_json, read_json
from fm_app.watcher import SaveWatcher

STATIC = ROOT/'web'
logger = logging.getLogger(__name__)


class Handler(BaseHTTPRequestHandler):
    server_version = 'Touchline/2.0'

    def reply(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def trusted(self):
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        return self.headers.get('Host', '') in allowed and self.headers.get('Origin') in ({None} | {f'http://{h}' for h in allowed})

    def body(self):
        size = int(self.headers.get('Content-Length', '0'))
        if not 2 <= size <= 65536:
            raise ValueError('Solicitud inválida o demasiado grande.')
        self.connection.settimeout(10)
        value = json.loads(self.rfile.read(size))
        if not isinstance(value, dict):
            raise ValueError('La solicitud debe ser un objeto.')
        return value

    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

    def do_GET(self):
        if not self.trusted():
            return self.reply(403, {'error': 'Origen no permitido.'})
        path = self.path.split('?')[0]
        state = self.server.state
        if path == '/api/data':
            with state.lock:
                data = state.dataset
            return self.reply(200, data)
        if path == '/api/status':
            with state.lock:
                data = state.dataset
                active = next((dict(j, job_id=k) for k,j in state.jobs.items() if j['status'] in ACTIVE_STATES), None)
                latest = dict(next(reversed(state.jobs.values()))) if state.jobs else None
                latest_id = next(reversed(state.jobs)) if state.jobs else None
                ready = [s for s in STYLES if data and cache_key(data['id'], s, data['default_primary_slot']) in state.cache]
                restore_error = state.restore_error
            sync = self.server.watcher.get_status() if self.server.watcher else None
            return self.reply(200, {'application': 'Touchline', 'has_dataset': data is not None,
                'dataset_id': data['id'] if data else None, 'club': data['club'] if data else None,
                'game_date': data['date'] if data else None, 'ready_styles': ready, 'active_job': active,
                'last_job': dict(latest, job_id=latest_id) if latest else None, 'restore_error': restore_error, 'sync': sync})
        if path == '/api/sync/status':
            return self.reply(200, self.server.watcher.get_status() if self.server.watcher else {})
        if path == '/api/sync/saves':
            return self.reply(200, self.server.watcher.list_saves() if self.server.watcher else [])
        if path == '/api/retention':
            return self.reply(200, state.store.retention())
        if path == '/api/preferences':
            with state.lock:
                data = state.dataset
            saved = read_json(state.storage/'preferences.json', {})
            return self.reply(200, saved.get(data['career_id']) if data else None)
        if path.startswith('/api/jobs/'):
            with state.lock:
                job = state.jobs.get(path.rsplit('/',1)[1])
                job = dict(job) if job else None
            return self.reply(200 if job else 404, job or {'error': 'Importación no encontrada.'})
        aliases = {'/': 'index.html', '/favicon.ico': 'touchline.ico', '/app_icon.ico': 'touchline.ico'}
        relative = aliases.get(path, unquote(path).lstrip('/'))
        file = (STATIC/relative).resolve()
        if not file.is_relative_to(STATIC.resolve()) or file.suffix not in ('.html','.js','.css','.ico','.png') or not file.is_file():
            return self.reply(404, {'error': 'No encontrado.'})
        raw = file.read_bytes()
        self.send_response(200)
        mime = mimetypes.guess_type(file)[0] or 'application/octet-stream'
        self.send_header('Content-Type', mime + ('; charset=utf-8' if file.suffix in ('.html','.js','.css') else ''))
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        if not self.trusted() or self.headers.get('X-FM-App') != '1':
            return self.reply(403, {'error': 'Origen no permitido.'})
        try:
            params, state = self.body(), self.server.state
            if self.path == '/api/activate':
                activated = self.server.request_activate is not None
                if activated:
                    self.server.request_activate()
                return self.reply(200, {'activated': activated})
            if self.path == '/api/shutdown':
                self.reply(200, {'status': 'closing'})
                threading.Thread(target=self.server.request_shutdown, daemon=True).start()
                return
            if self.path == '/api/sync/config':
                if not self.server.watcher:
                    return self.reply(503, {'error': 'Sincronizador no inicializado.'})
                return self.reply(200, self.server.watcher.configure(folder=params.get('watch_folder'), target_save=params.get('target_save'), enabled=params.get('enabled')))
            if self.path == '/api/sync/trigger':
                if not self.server.watcher:
                    return self.reply(503, {'error': 'Sincronizador no inicializado.'})
                job_id = self.server.watcher.trigger_sync(params.get('filename'))
                return self.reply(202, {'job_id': job_id})
            if self.path == '/api/retention':
                return self.reply(200, state.store.configure_retention(params))
            with state.lock:
                data = state.dataset
            if data is None:
                return self.reply(409, {'error': 'Cargá una partida .fm para continuar.'})
            if self.path == '/api/preferences':
                if params.get('career_id') != data['career_id']:
                    return self.reply(409, {'error': 'La carrera cambió.'})
                value = validate_preferences(params, data)
                with state.lock:
                    saved = read_json(state.storage/'preferences.json', {})
                    saved[data['career_id']] = value
                    atomic_json(state.storage/'preferences.json', saved)
                return self.reply(200, value)
            if self.path == '/api/current-tactic':
                if params.get('dataset_id') != data['id']:
                    return self.reply(409, {'error':'La partida cambió. Revisá y confirmá tu táctica nuevamente.'})
                return self.reply(200, audit_tactic(data, params))
            if self.path not in ('/api/analyze','/api/simulate'):
                return self.reply(404, {'error': 'No encontrado.'})
            if params.get('dataset_id') != data['id']:
                return self.reply(409, {'error': 'La partida cambió. Actualizá el análisis.'})
            kwargs = analysis_parameters(params, data, simulate=self.path == '/api/simulate')
            key = cache_key(data['id'], **kwargs)
            with state.lock:
                result = state.cache.get(key)
                if result is not None:
                    state.cache.move_to_end(key)
            if result is None:
                result = (simulate_formation if self.path == '/api/simulate' else analyze)(data, **kwargs)
                result = dict(result, dataset_id=data['id'])
                with state.lock:
                    if state.dataset is data:
                        state.cache[key] = result
                        while len(state.cache) > 64:
                            state.cache.popitem(last=False)
            return self.reply(200, dict(result, dataset_id=data['id']))
        except (ValueError, TypeError, KeyError, OSError) as error:
            return self.reply(400, {'error': str(error)})

    def do_PUT(self):
        if not self.trusted() or self.headers.get('X-FM-App') != '1':
            return self.reply(403, {'error': 'Origen no permitido.'})
        if self.path != '/api/import':
            return self.reply(404, {'error': 'No encontrado.'})
        state, job_id = self.server.state, None
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 1000 <= length <= MAX_SAVE:
                return self.reply(413, {'error': 'Elegí una partida .fm de hasta 400 MB.'})
            filename = unquote(self.headers.get('X-FM-Filename', 'Partida.fm')).replace('\\','/').rsplit('/',1)[-1][:200]
            if not filename.lower().endswith('.fm'):
                raise ValueError('Elegí una partida .fm.')
            job_id = state.reserve('uploading', 'Recibiendo archivo…')
            if job_id is None:
                return self.reply(409, {'error': 'Ya hay una importación en curso.'})
            folder = state.store.folder(job_id)
            folder.mkdir(parents=True)
            source = folder/'save.fm'
            self.connection.settimeout(90)
            with source.open('wb') as stream:
                remaining = length
                while remaining:
                    chunk = self.rfile.read(min(1024*1024, remaining))
                    if not chunk:
                        raise ValueError('La carga se interrumpió.')
                    stream.write(chunk); remaining -= len(chunk)
            state._validate_save(source)
            from datetime import datetime, timezone
            atomic_json(folder/'import.json', {'filename': filename, 'imported_at': datetime.now(timezone.utc).isoformat()})
            state.executor.submit(state.import_save, job_id, source, folder)
            return self.reply(202, {'job_id': job_id})
        except (ValueError, OSError, RuntimeError) as error:
            if job_id:
                state.progress(job_id, 'error', str(error))
            return self.reply(400, {'error': str(error)})


def create_app_server(port=8765, enable_watcher=True, storage=STORAGE, config_file=None, start_watcher=True):
    state = AppState(storage)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except Exception:
        state.close()
        raise
    server.daemon_threads = True
    server.state = state
    server.request_shutdown = server.shutdown
    server.request_activate = None
    server.watcher = SaveWatcher(state, config_file) if enable_watcher else None
    if server.watcher and start_watcher:
        server.watcher.start()
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--no-sync', action='store_true')
    args = parser.parse_args()
    server = create_app_server(args.port, not args.no_sync)
    print(f'Touchline: http://127.0.0.1:{server.server_port}', flush=True)
    if args.open:
        threading.Timer(.7, lambda: webbrowser.open(f'http://127.0.0.1:{server.server_port}/')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if server.watcher:
            server.watcher.stop()
        server.state.close()
        server.server_close()


if __name__ == '__main__':
    main()
