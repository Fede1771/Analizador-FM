"""Atomic local persistence. Retention only touches validated import directories."""
from pathlib import Path
import json
import logging
import os
import shutil
import sys
import uuid


def get_base_dir() -> Path:
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass and (Path(meipass) / 'web').is_dir():
            return Path(meipass)
        exe_parent = Path(sys.executable).resolve().parent
        if (exe_parent / 'web').is_dir():
            return exe_parent
        if (exe_parent / '_internal' / 'web').is_dir():
            return exe_parent / '_internal'
        if meipass:
            return Path(meipass)
        return exe_parent
    return Path(__file__).resolve().parents[1]


def get_data_dir() -> Path:
    env = os.environ.get('TOUCHLINE_DATA_DIR')
    if env:
        return Path(env).resolve()
    if getattr(sys, 'frozen', False):
        local_app = os.environ.get('LOCALAPPDATA')
        if local_app:
            return Path(local_app).resolve() / 'Touchline' / 'data'
    return Path(__file__).resolve().parents[1] / 'data'


ROOT = get_base_dir()
DATA_DIR = get_data_dir()
STORAGE = DATA_DIR / 'imports'
logger = logging.getLogger(__name__)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def valid_import_id(value):
    return isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value)


class ImportStorage:
    def __init__(self, root=STORAGE):
        self.root = Path(root).resolve()
        self.policy_path = self.root / 'retention.json'

    def folder(self, name):
        if not valid_import_id(name):
            raise ValueError('Referencia de importación inválida.')
        folder = self.root / name
        if folder.is_symlink() or folder.resolve().parent != self.root:
            raise ValueError('La importación está fuera del almacenamiento.')
        return folder

    def current(self):
        pointer = read_json(self.root / 'current.json')
        if pointer is None and not (self.root/'current.json').exists():
            return None
        if not isinstance(pointer, dict):
            raise ValueError('Referencia de importación dañada.')
        return self.folder(pointer.get('folder'))

    def publish(self, job_id):
        self.folder(job_id)
        atomic_json(self.root / 'current.json', {'folder': job_id})

    def retention(self):
        value = read_json(self.policy_path, {})
        if not isinstance(value, dict):
            value = {}
        copies, size = value.get('max_snapshots', 5), value.get('max_total_mb', 2048)
        return {'max_snapshots': copies if type(copies) is int and 1 <= copies <= 100 else 5,
                'max_total_mb': size if type(size) is int and 400 <= size <= 102400 else 2048}

    def configure_retention(self, value):
        if not isinstance(value, dict) or type(value.get('max_snapshots')) is not int or not 1 <= value['max_snapshots'] <= 100 or type(value.get('max_total_mb')) is not int or not 400 <= value['max_total_mb'] <= 102400:
            raise ValueError('Elegí entre 1 y 100 copias, y entre 400 y 102400 MB.')
        atomic_json(self.policy_path, value)
        return self.retention()

    def prune(self, protected=()):
        current = self.current()
        protected = set(protected) | ({current.name} if current else set())
        policy = self.retention()
        entries = []
        if not self.root.exists():
            return
        for path in self.root.iterdir():
            if not valid_import_id(path.name) or path.is_symlink() or not path.is_dir():
                continue
            folder = self.folder(path.name)
            size = sum(p.stat().st_size for p in folder.rglob('*') if p.is_file() and not p.is_symlink())
            entries.append((folder, size, folder.stat().st_mtime_ns))
        entries.sort(key=lambda item: item[2], reverse=True)
        # Keep protected snapshots first; the current result survives even if it exceeds the limit.
        count = sum(p.name in protected for p, _, _ in entries)
        total = sum(size for p, size, _ in entries if p.name in protected)
        for folder, size, _ in entries:
            if folder.name in protected:
                continue
            if count < policy['max_snapshots'] and total + size <= policy['max_total_mb'] * 1024 * 1024:
                count += 1; total += size
            else:
                checked = self.folder(folder.name)
                if checked.resolve().parent == self.root and not checked.is_symlink():
                    shutil.rmtree(checked)
