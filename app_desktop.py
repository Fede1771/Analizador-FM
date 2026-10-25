"""Touchline desktop lifecycle, diagnostics and local HTTP host."""
import argparse
import ctypes
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import socket
import sys
import threading
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
from fm_app.server import create_app_server


def configure_logging():
    folder = ROOT/'data/logs'
    folder.mkdir(parents=True, exist_ok=True)
    handlers = [RotatingFileHandler(folder/'touchline.log', maxBytes=2*1024*1024, backupCount=3, encoding='utf-8')]
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', handlers=handlers)


def is_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(.3)
        return connection.connect_ex((host, port)) == 0


def check_existing_instance(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status', timeout=1) as response:
            return json.load(response).get('application') == 'Touchline'
    except (OSError, ValueError):
        return False


def activate_existing_instance(port):
    request = urllib.request.Request(f'http://127.0.0.1:{port}/api/activate', data=b'{}',
        headers={'Content-Type': 'application/json', 'X-FM-App': '1'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.load(response).get('activated', False)
    except (OSError, ValueError):
        return False


def find_free_port(start_port=8765, max_attempts=20):
    for port in range(start_port, start_port+max_attempts):
        if not is_port_in_use(port):
            return port
    raise OSError('No se encontró un puerto local disponible.')


def main():
    configure_logging()
    logger = logging.getLogger('touchline.desktop')
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('touchline.analizador.fm26.desktop')
    parser = argparse.ArgumentParser(description='Touchline · Analizador FM26')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--browser-only', action='store_true')
    parser.add_argument('--no-sync', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Puerto inválido.')
    if check_existing_instance(args.port):
        activate_existing_instance(args.port)
        return
    instance_mutex = None
    if sys.platform == 'win32':
        import time
        kernel = ctypes.windll.kernel32
        kernel.CreateMutexW.restype = ctypes.c_void_p
        instance_mutex = kernel.CreateMutexW(None, False, f'Local\\TouchlineDesktop-{args.port}')
        kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        if kernel.WaitForSingleObject(instance_mutex, 0) not in (0, 0x80):
            for _ in range(50):
                if check_existing_instance(args.port):
                    activate_existing_instance(args.port)
                    return
                time.sleep(.1)
            return
        if check_existing_instance(args.port):
            activate_existing_instance(args.port)
            return
    port = find_free_port(args.port)
    server = create_app_server(port, not args.no_sync)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name='TouchlineHTTP')
    thread.start()
    quit_requested = threading.Event()
    closed = threading.Event()
    cleanup_lock = threading.Lock()
    url = f'http://127.0.0.1:{server.server_port}/'

    def cleanup(*_):
        with cleanup_lock:
            if closed.is_set():
                return
            closed.set()
            quit_requested.set()
            logger.info('Cerrando monitor, extracción y servidor.')
            if server.watcher:
                server.watcher.stop()
            server.state.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            logger.info('Touchline cerrado.')

    server.request_shutdown = quit_requested.set
    try:
        if args.browser_only:
            webbrowser.open(url)
            quit_requested.wait()
        else:
            import webview
            window = webview.create_window('Touchline · Analizador FM26', url=url, width=1360, height=920,
                min_size=(720,600), text_select=True, confirm_close=False)
            window.events.closed += cleanup
            server.request_shutdown = window.destroy
            def activate():
                window.restore()
                window.show()
            server.request_activate = activate
            webview.start(icon=str(ROOT/'web/touchline.ico'), private_mode=False, storage_path=str(ROOT/'data/webview'))
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        logging.getLogger('touchline.desktop').exception('No se pudo iniciar Touchline')
        if sys.platform == 'win32':
            ctypes.windll.user32.MessageBoxW(None, f'No se pudo iniciar Touchline: {error}\nRevisá data/logs/touchline.log o ejecutá scripts/diagnostico.py.', 'Touchline', 16)
        else:
            raise
