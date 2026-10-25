import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch
from fm_app.server import create_app_server
from fm_app.contracts import cache_key
from fixtures import dataset, fake_save


class ServerEndpointsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=TemporaryDirectory();root=Path(cls.temp.name)
        cls.server=create_app_server(port=0,storage=root/'imports',config_file=root/'sync.json',start_watcher=False)
        cls.server.state.dataset=dataset();cls.data=cls.server.state.dataset
        cls.server.watcher.configure(folder=str(root/'games'),enabled=False)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.watcher.stop();cls.server.shutdown();cls.server.state.close();cls.server.server_close();cls.thread.join(3);cls.temp.cleanup()

    def request(self,path,body=None,headers=None,method=None):
        raw=None if body is None else json.dumps(body).encode()
        req=urllib.request.Request(self.base+path,data=raw,headers={'Content-Type':'application/json','X-FM-App':'1',**(headers or {})},method=method)
        try:
            with urllib.request.urlopen(req,timeout=30) as response:
                result=response.read();return response.status,result,response.headers
        except urllib.error.HTTPError as error:
            try:
                return error.code,error.read(),error.headers
            finally:
                error.close()

    def payload(self,**kwargs):return {'dataset_id':self.data['id'],**kwargs}

    def test_static_modules_served_and_paths_contained(self):
        for path in ('/','/app.js','/api.js','/views.js','/session.js','/style.css','/favicon.ico'):
            with self.subTest(path=path):self.assertEqual(self.request(path)[0],200)
        self.assertEqual(self.request('/%2e%2e/fm_app/server.py')[0],404)

    def test_status_reports_identity_and_sync(self):
        status,body,_=self.request('/api/status');body=json.loads(body)
        self.assertEqual(status,200);self.assertEqual(body['application'],'Touchline')
        self.assertEqual(body['sync']['state'],'paused')

    def test_activation_is_local_and_invokes_window_callback(self):
        from unittest.mock import Mock
        activate=Mock();self.server.request_activate=activate
        try:
            self.assertTrue(json.loads(self.request('/api/activate',{})[1])['activated'])
            activate.assert_called_once()
            self.assertEqual(self.request('/api/activate',{},headers={'X-FM-App':'0'})[0],403)
        finally:self.server.request_activate=None

    def test_current_tactic_requires_current_dataset_and_confirmed_plan(self):
        self.assertEqual(self.request('/api/current-tactic',{'dataset_id':'old'})[0],409)
        self.assertEqual(self.request('/api/current-tactic',self.payload())[0],400)

    def test_analysis_uses_precomputed_cache(self):
        marker={'style':'possession','cached':True}
        self.server.state.cache[cache_key(self.data['id'],'possession',0)]=marker
        with patch('fm_app.server.analyze',side_effect=AssertionError('must use cache')):
            status,body,_=self.request('/api/analyze',self.payload())
        self.assertEqual(status,200);self.assertTrue(json.loads(body)['cached'])
        self.server.state.cache.clear()

    def test_simulates_catalog_and_rejects_unknown_input(self):
        status,body,_=self.request('/api/simulate',self.payload(formation='352'))
        self.assertEqual(status,200);self.assertEqual(len(json.loads(body)['lineup']),11)
        for values in ({'formation':'bad'},{'style':'bad'},{'prompt':{}},{'excluded':[999999]},{'primary_slot':True},{'overrides':{'tempo':'invalid'}}):
            with self.subTest(values=values):self.assertEqual(self.request('/api/simulate',self.payload(**values))[0],400)
        self.assertEqual(self.request('/api/analyze',[])[0],400)
        self.assertEqual(self.request('/api/analyze',{'dataset_id':'old'})[0],409)

    def test_origin_and_application_header_are_enforced(self):
        self.assertEqual(self.request('/api/status',headers={'Origin':'https://other.example'})[0],403)
        self.assertEqual(self.request('/api/analyze',self.payload(),headers={'X-FM-App':'0'})[0],403)

    def test_preferences_and_retention_persist_in_temporary_storage(self):
        prefs={'career_id':self.data['career_id'],'primary_slot':0,'style':'wide','excluded':[],'labels':{'0':'Titulares'},'formation':'352'}
        self.assertEqual(self.request('/api/preferences',prefs)[0],200)
        self.assertEqual(json.loads(self.request('/api/preferences')[1])['style'],'wide')
        self.assertEqual(self.request('/api/retention',{'max_snapshots':3,'max_total_mb':1024})[0],200)
        self.assertEqual(self.request('/api/retention',{'max_snapshots':0,'max_total_mb':1})[0],400)

    def test_parallel_status_and_configuration_do_not_deadlock(self):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures=[executor.submit(self.request,'/api/status') if i%2 else executor.submit(self.request,'/api/sync/config',{'enabled':False,'target_save':'auto'}) for i in range(12)]
            self.assertTrue(all(f.result(timeout=10)[0]==200 for f in futures))

    def test_invalid_upload_ends_job_and_preserves_dataset(self):
        req=urllib.request.Request(self.base+'/api/import',data=b'bad'*1000,headers={'X-FM-App':'1','X-FM-Filename':'test.fm'},method='PUT')
        with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(req,timeout=5)
        self.assertEqual(caught.exception.code,400);caught.exception.close()
        self.assertFalse(self.server.state.busy());self.assertIs(self.server.state.dataset,self.data)
