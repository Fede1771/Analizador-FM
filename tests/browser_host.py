"""Isolated browser verification host. All data is synthetic and temporary."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=Path(sys.argv[1]).resolve()
ARTIFACTS.mkdir(parents=True, exist_ok=True)
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from fixtures import dataset
from fm_app.server import create_app_server,Handler
from fm_app.contracts import cache_key
from fm_app.analysis import analyze

temp=TemporaryDirectory(prefix='touchline-ui-')
server=create_app_server(port=0,storage=Path(temp.name)/'imports',config_file=Path(temp.name)/'sync.json',start_watcher=False)
server.watcher.configure(folder=str(Path(temp.name)/'games'),enabled=False)
original=dataset()
server.state.dataset=deepcopy(original)
for style in original['styles']:
    server.state.cache[cache_key(original['id'],style,0)]=analyze(original,style)
server.test_counts={}

class TestHandler(Handler):
    def do_POST(self):
        self.server.test_counts[self.path]=self.server.test_counts.get(self.path,0)+1
        if self.path=='/__test/change':
            if not self.trusted() or self.headers.get('X-FM-App')!='1':
                return self.reply(403,{})
            body=self.body()
            data=deepcopy(original)
            data['id']=body.get('id','new-save')
            if body.get('short'):
                data['players']=data['players'][:10]
            if body.get('empty'):
                data=None
            with server.state.lock:
                server.state.dataset=data
                server.state.cache.clear()
            return self.reply(200,{})
        return super().do_POST()

    def do_GET(self):
        if self.path=='/__test/counts':return self.reply(200,self.server.test_counts)
        return super().do_GET()

server.RequestHandlerClass=TestHandler
server.request_shutdown=server.shutdown
address={'url':f'http://127.0.0.1:{server.server_port}','storage':temp.name}
Path(sys.argv[2]).write_text(json.dumps(address),encoding='utf-8')
print(address['url'],flush=True)
try:
    server.serve_forever()
finally:
    server.watcher.stop();server.state.close();server.server_close();temp.cleanup()
