"""Standalone Windows Desktop Application for Touchline Analizador FM26."""
import argparse
import logging
import os
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

# Set Windows AppUserModelID so taskbar displays custom icon instead of generic Python icon
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('touchline.analizador.fm26.desktop')
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from fm_app.server import create_app_server, STORAGE

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('fm_desktop')


def is_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def find_free_port(start_port=8765, max_attempts=20):
    for p in range(start_port, start_port + max_attempts):
        if not is_port_in_use(p):
            return p
    return start_port


def check_existing_instance(port):
    """Check if an instance of Analizador FM is already running on this port."""
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{port}/api/status', headers={'User-Agent': 'FMAppDesktop/1.0'})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description='Touchline Analizador FM26 Desktop')
    parser.add_argument('--port', type=int, default=8765, help='Puerto HTTP local (defecto: 8765)')
    parser.add_argument('--browser-only', action='store_true', help='Abrir directamente en navegador')
    args = parser.parse_args()

    port = args.port

    # If port 8765 is already running our application, we can just open it
    if is_port_in_use(port) and check_existing_instance(port):
        logger.info("Instancia de Analizador FM ya está en ejecución en http://127.0.0.1:%d", port)
        webbrowser.open(f'http://127.0.0.1:{port}')
        return

    # If port is occupied by something else, find a free port
    if is_port_in_use(port):
        port = find_free_port(start_port=port + 1)

    logger.info("Iniciando servidor local en http://127.0.0.1:%d...", port)
    server = create_app_server(port=port, enable_watcher=True)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True, name='HttpServerThread')
    server_thread.start()

    app_url = f'http://127.0.0.1:{port}/'
    icon_path = str(ROOT / 'web' / 'touchline.ico')
    if not os.path.exists(icon_path):
        icon_path = str(ROOT / 'web' / 'app_icon.ico')

    def cleanup():
        logger.info("Cerrando servidor y servicios en segundo plano...")
        try:
            if hasattr(server, 'watcher') and server.watcher:
                server.watcher.stop()
        except Exception:
            pass
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass
        try:
            server.state.executor.shutdown(wait=False)
        except Exception:
            pass
        logger.info("Touchline cerrado correctamente.")
        os._exit(0)

    if args.browser_only:
        webbrowser.open(app_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            cleanup()
        return

    # Try native WebView window
    try:
        import webview

        logger.info("Abriendo ventana de escritorio nativa WebView...")
        window = webview.create_window(
            title='Touchline · Analizador FM26',
            url=app_url,
            width=1340,
            height=880,
            min_size=(980, 680),
            text_select=True,
            confirm_close=False
        )
        window.events.closed += cleanup
        
        # Start webview; this call blocks until the user closes the window
        webview.start(icon=icon_path if os.path.exists(icon_path) else None)
    except Exception as e:
        logger.warning("No se pudo iniciar ventana webview nativa (%s). Abriendo en navegador por defecto...", e)
        webbrowser.open(app_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    finally:
        cleanup()


if __name__ == '__main__':
    main()
