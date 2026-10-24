"""Read-only installation diagnostics; never starts the server or save watcher."""
import importlib.metadata
import importlib.util
from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    print('Python:', sys.version.split()[0])
    success = sys.version_info >= (3,12)
    for distribution, module in [('fmsave','fmsave'), ('pywebview','webview')]:
        if distribution == 'pywebview' and sys.platform != 'win32':
            continue
        try:
            print(distribution + ':', importlib.metadata.version(distribution))
            success = success and importlib.util.find_spec(module) is not None
        except importlib.metadata.PackageNotFoundError:
            print(distribution + ': FALTA')
            success = False
    for name in ('web/index.html','web/app.js','fm_app/data/fm26_catalog.json','fm_app/data/fm26_es419.json'):
        exists = (root/name).is_file()
        print(name + ':', 'OK' if exists else 'FALTA')
        success = success and exists
    print('Las partidas y la configuración no se modificaron.')
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
