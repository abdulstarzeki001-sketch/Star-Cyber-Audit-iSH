import importlib.util
import json
import threading
import tempfile
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / 'app.py'
spec = importlib.util.spec_from_file_location('star_companion', APP_PATH)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class MockGateway(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path in ('/health', '/lab-health'):
            data = b'{"ok":true}'
            self.send_response(200)
        else:
            data = b'not found'
            self.send_response(404)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.server.received_auth = self.headers.get('Authorization')
        length = int(self.headers.get('Content-Length', '0'))
        self.server.received_body = json.loads(self.rfile.read(length))
        if self.server.redirect:
            self.send_response(302)
            self.send_header('Location', '/leak')
            self.end_headers()
            return
        data = json.dumps({'choices': [{'message': {'content': 'رد اختبار حقيقي من الخدمة الوهمية'}}]}, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class CompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gateway = ThreadingHTTPServer(('127.0.0.1', 0), MockGateway)
        cls.gateway.redirect = False
        threading.Thread(target=cls.gateway.serve_forever, daemon=True).start()
        gateway = 'http://127.0.0.1:' + str(cls.gateway.server_port)
        cls.config = {'port': 0, 'goclaw_url': gateway, 'lab_url': gateway + '/lab-health',
                      'agent': 'default', 'token': 'example-secret', 'csrf': 'test-session',
                      'report_path': Path('/nonexistent/star-audit-test.json')}
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), app.make_handler(cls.config))
        cls.config['port'] = cls.server.server_port
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.gateway.shutdown()
        cls.server.server_close()
        cls.gateway.server_close()

    def request(self, path, body=None, headers=None):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        req = urllib.request.Request(self.base + path, data=data, headers=headers or {}, method='GET' if body is None else 'POST')
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                return res.status, json.loads(res.read().decode())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode())

    def test_status_checks_real_responses_and_never_returns_secret(self):
        code, data = self.request('/api/status')
        self.assertEqual(code, 200)
        self.assertEqual(data['lab']['state'], 'online')
        self.assertEqual(data['goclaw']['state'], 'online')
        self.assertNotIn('example-secret', json.dumps(data))
        _, session = self.request('/api/session')
        self.assertNotIn('example-secret', json.dumps(session))

    def test_lab_is_not_assumed_when_no_health_url_is_configured(self):
        before = self.config['lab_url']
        self.config['lab_url'] = None
        try:
            code, data = self.request('/api/status')
            self.assertEqual(code, 200)
            self.assertEqual(data['lab']['state'], 'not_configured')
        finally:
            self.config['lab_url'] = before

    def test_local_report_produces_counts_without_disclosing_filenames(self):
        before = self.config['report_path']
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / 'analysis.json'
            report.write_text(json.dumps({'files': [
                {'name': 'private-filename.js', 'classification': 'JS_SOURCE',
                 'api_paths': ['/one', '/one'], 'flags': ['heuristic']},
                {'classification': 'JS_SOURCE', 'api_paths': ['/one', '/two'], 'flags': []},
            ]}), encoding='utf-8')
            self.config['report_path'] = report
            try:
                code, data = self.request('/api/status')
                self.assertEqual(code, 200)
                self.assertEqual(data['report'], {'state': 'available', 'files': 2, 'api_paths': 2, 'flags': 1})
                self.assertNotIn('private-filename.js', json.dumps(data))
            finally:
                self.config['report_path'] = before

    def test_valid_chat_is_forwarded_and_response_is_visible(self):
        headers = {'Content-Type': 'application/json', 'X-Star-CSRF': 'test-session', 'Origin': self.base}
        code, data = self.request('/api/chat', {'messages': [{'role': 'user', 'content': 'مرحبا'}]}, headers)
        self.assertEqual(code, 200)
        self.assertIn('رد اختبار', data['reply'])
        self.assertEqual(self.gateway.received_auth, 'Bearer example-secret')
        self.assertEqual(self.gateway.received_body['model'], 'goclaw:default')
        self.assertEqual(self.gateway.received_body['messages'][0]['content'], 'مرحبا')

    def test_chat_requires_session_and_same_origin(self):
        body = {'messages': [{'role': 'user', 'content': 'hello'}]}
        self.assertEqual(self.request('/api/chat', body, {'Content-Type': 'application/json'})[0], 403)
        headers = {'Content-Type': 'application/json', 'X-Star-CSRF': 'test-session', 'Origin': 'http://evil.example'}
        self.assertEqual(self.request('/api/chat', body, headers)[0], 403)

    def test_private_files_are_not_served(self):
        self.assertEqual(self.request('/.env')[0], 404)
        self.assertEqual(self.request('/app.py')[0], 404)

    def test_only_loopback_destinations_are_accepted(self):
        for url in ('http://evil.example', 'http://127.0.0.1.evil.example', 'http://localhost@evil.example',
                    'file:///etc/passwd', 'http://localhost:1234/?token=hidden'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                app.local_url(url)
        self.assertEqual(app.local_url('http://127.0.0.1:8000/health'), 'http://127.0.0.1:8000/health')

    def test_gateway_redirect_is_not_followed(self):
        self.gateway.redirect = True
        try:
            headers = {'Content-Type': 'application/json', 'X-Star-CSRF': 'test-session', 'Origin': self.base}
            code, data = self.request('/api/chat', {'messages': [{'role': 'user', 'content': 'hello'}]}, headers)
            self.assertEqual(code, 502)
            self.assertNotIn('example-secret', json.dumps(data))
        finally:
            self.gateway.redirect = False


if __name__ == '__main__':
    unittest.main()
