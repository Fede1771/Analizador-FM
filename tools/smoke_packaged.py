"""Exercise the compiled app using only a disposable synthetic career."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'tests')]
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
        env={**os.environ,'TOUCHLINE_DATA_DIR':str(folder)}
        process=subprocess.Popen([str(executable),'--server-only','--no-sync','--port',str(port)],cwd=ROOT,env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        base=f'http://127.0.0.1:{port}'
        def request(path,body=None):
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,
                headers={'Content-Type':'application/json','X-FM-App':'1'})
            with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
        try:
            deadline=time.monotonic()+45
            while True:
                try:status=request('/api/status');break
                except OSError:
                    if process.poll() is not None or time.monotonic()>deadline:raise
                    time.sleep(.2)
            assert status['dataset_id']==data['id']
            body={'dataset_id':data['id']}
            assert request('/api/insights',body)['player_count']==22
            assert request('/api/players/compare',{**body,'left_uid':10,'right_uid':11})['left']['uid']==10
            assert len(request('/api/history/player',{**body,'uid':10})['points'])==1
            csv=request('/api/table/template')['csv']
            preview=request('/api/table/preview',{'text':csv,'club':'Prueba empaquetada','manager':'Prueba',
                'date':'2026-11-04','stats_scope':'overall_club','stats_period':'2026/27'})
            assert preview['count']==1
            assert request('/api/data')['id']==data['id']
            request('/api/shutdown',{})
            process.wait(timeout=15)
            assert process.returncode==0
            print('PACKAGED SMOKE OK: restore, insights, comparison, history, CSV preview, unchanged active data and clean shutdown.')
        finally:
            if process.poll() is None:
                process.terminate();process.wait(timeout=10)


if __name__=='__main__':main()
