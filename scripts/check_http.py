"""Check the running app, optionally including a real save upload."""
import argparse
import http.client
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8765')
parser.add_argument('--import-save',type=Path)
args=parser.parse_args()

def request(path,body=None,method=None,headers=None):
    req=urllib.request.Request(args.url+path,data=body,method=method,headers=headers or {})
    with urllib.request.urlopen(req,timeout=30) as response:
        return response.status,json.load(response)

_,data=request('/api/data')
assert data is not None,'First upload an FM26 save in the app.'
assert len(data['players'])>0
assert data['fm26_reference']['localization']['locale']=='es-419'
assert all('ability' not in p and 'personality' not in p for p in data['players'])
assert 'slot_labels' in data
assert str(data['slots'][0]) in data['slot_labels'] or data['slots'][0] in data['slot_labels']
params={'dataset_id':data['id'],'style':'press','primary_slot':data['slots'][0],'excluded':[]}
_,result=request('/api/analyze',json.dumps(params).encode(),headers={'X-FM-App':'1','Content-Type':'application/json'})
assert len(result['tactics'])==3
assert all(len({p['uid'] for p in t['lineup']})==11 for t in result['tactics'])
for prof in result['profiles'].values():
    for phase in ('in_possession','out_of_possession'):
        role=prof[phase]
        assert role['localization']['resource_verified']
        assert role['name']==role['localization']['text']
        assert role['localization']['locale']=='es-419'
        for item in role['instructions']:
            assert item['value']==item['localization']['value']['text']
print('HTTP: data and tactical analysis OK',flush=True)
try:
    request('/api/analyze',b'{}',headers={'X-FM-App':'1','Content-Type':'application/json','Origin':'https://example.org'})
    raise AssertionError('Foreign origin was accepted')
except urllib.error.HTTPError as error:
    assert error.code==403
try:
    request('/api/import',b'x'*1000,method='PUT',headers={'X-FM-App':'1'})
    raise AssertionError('Invalid save was accepted')
except urllib.error.HTTPError as error:
    assert error.code==400
assert request('/api/data')[1]['id']==data['id']
print('HTTP: invalid upload rejected, previous dataset preserved, foreign origin rejected',flush=True)
if args.import_save:
    parsed=urllib.parse.urlparse(args.url)
    conn=http.client.HTTPConnection(parsed.hostname,parsed.port,timeout=60)
    conn.putrequest('PUT','/api/import')
    conn.putheader('Content-Length',str(args.import_save.stat().st_size))
    conn.putheader('X-FM-App','1')
    conn.putheader('X-FM-Filename',urllib.parse.quote(args.import_save.name))
    conn.endheaders()
    with args.import_save.open('rb') as stream:
        while chunk:=stream.read(1024*1024):
            conn.send(chunk)
    response=conn.getresponse()
    body=json.loads(response.read())
    assert response.status==202,body
    conn.close()
    print('HTTP: real save received; waiting for extraction...',flush=True)
    deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        _,job=request('/api/jobs/'+body['job_id'])
        if job['status']=='error':
            raise AssertionError(job)
        if job['status']=='done':
            break
        time.sleep(1)
    else:
        raise TimeoutError('Import did not finish')
    _,updated=request('/api/data')
    assert updated['id']==data['id']
    assert len(updated['players'])==len(data['players'])
    assert len(updated['loans'])==len(data['loans'])
    assert set(request('/api/status')[1]['ready_styles'])==set(updated['styles'])
    print('HTTP: real save imported successfully; counts and identity match',flush=True)
