"""Check the packaged 1.0.5-based app using only an isolated synthetic career."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from fixtures import write_snapshot
from fm_app.storage import atomic_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('executable',type=Path);args=parser.parse_args()
    executable=args.executable.resolve()
    if not executable.is_file():raise SystemExit('No existe el ejecutable.')
    temp_root=ROOT/'.tmp';temp_root.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='packaged-smoke-',dir=temp_root) as temp:
        folder=Path(temp).resolve()
        if not folder.is_relative_to(temp_root.resolve()):raise SystemExit('Temporal fuera del proyecto.')
        imports=folder/'imports';import_id='a'*32
        data=write_snapshot(imports/import_id/'output')
        atomic_json(imports/'current.json',{'folder':import_id})
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        process=subprocess.Popen([str(executable),'--no-sync','--port',str(port)],cwd=ROOT,
            env={**os.environ,'TOUCHLINE_DATA_DIR':str(folder)},
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        base=f'http://127.0.0.1:{port}'
        def request(path,body=None,raw=False):
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,
                headers={'Content-Type':'application/json','X-FM-App':'1'})
            with urllib.request.urlopen(req,timeout=30) as response:return response.read() if raw else json.load(response)
        try:
            deadline=time.monotonic()+60
            while True:
                try:status=request('/api/status');break
                except OSError:
                    if process.poll() is not None or time.monotonic()>deadline:raise
                    time.sleep(.2)
            assert status['dataset_id']==data['id']
            body={'dataset_id':data['id'],'style':'possession','primary_slot':0}
            assert len(request('/api/analyze',body)['tactics'])==3
            assert len(request('/api/simulate',{**body,'formation':'433'})['lineup'])==11
            for name in ('index.html','menu.css','app.js'):
                raw=request('/'+name,raw=True)
                assert hashlib.sha256(raw).digest()==hashlib.sha256((ROOT/'web'/name).read_bytes()).digest(),name
            assert request('/api/data')['id']==data['id']
            # Wait for WebView to install its shutdown callback before closing the test window.
            time.sleep(3)
            request('/api/shutdown',{})
            process.wait(timeout=20)
            assert process.returncode==0
            print('PACKAGED SMOKE OK: restore, analysis, eleven-player simulation, menu resources, unchanged active data, clean shutdown.')
        finally:
            if process.poll() is None:process.terminate();process.wait(timeout=10)


if __name__=='__main__':main()
