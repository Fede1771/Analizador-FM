"""End-to-end API test for server endpoints, static files, and sync APIs."""
import json
from pathlib import Path
import threading
import time
import unittest
import urllib.request
import urllib.error

from fm_app.server import create_app_server, ROOT


class ServerEndpointsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8789
        cls.server = create_app_server(port=cls.port, enable_watcher=True)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls.server, 'watcher') and cls.server.watcher:
            cls.server.watcher.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.server.state.executor.shutdown(wait=False)

    def get(self, path):
        req = urllib.request.Request(
            f'http://127.0.0.1:{self.port}{path}',
            headers={'Host': f'127.0.0.1:{self.port}'}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status, resp.headers.get('Content-Type'), resp.read()

    def post(self, path, payload):
        raw = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f'http://127.0.0.1:{self.port}{path}',
            data=raw,
            headers={
                'Host': f'127.0.0.1:{self.port}',
                'Content-Type': 'application/json',
                'X-FM-App': '1'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))

    def test_static_files_served(self):
        status, ctype, body = self.get('/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', ctype)
        self.assertIn(b'Touchline', body)

        status, ctype, body = self.get('/app.js')
        self.assertEqual(status, 200)
        self.assertIn('javascript', ctype)

        status, ctype, body = self.get('/style.css')
        self.assertEqual(status, 200)
        self.assertIn('text/css', ctype)

        status, ctype, body = self.get('/favicon.ico')
        self.assertEqual(status, 200)
        self.assertTrue(len(body) > 100)

    def test_api_status_includes_sync(self):
        status, ctype, body = self.get('/api/status')
        self.assertEqual(status, 200)
        data = json.loads(body.decode('utf-8'))
        self.assertIn('has_dataset', data)
        self.assertIn('sync', data)
        self.assertIsNotNone(data['sync'])
        self.assertIn('watch_folder', data['sync'])
        self.assertIn('state', data['sync'])

    def test_api_sync_endpoints(self):
        status, ctype, body = self.get('/api/sync/status')
        self.assertEqual(status, 200)
        data = json.loads(body.decode('utf-8'))
        self.assertIn('enabled', data)
        self.assertIn('watch_folder', data)

        # Update sync config
        status, res = self.post('/api/sync/config', {
            'enabled': True,
            'target_save': 'auto'
        })
        self.assertEqual(status, 200)
        self.assertTrue(res['enabled'])
        self.assertIsNone(res['target_save'])


if __name__ == '__main__':
    unittest.main()
