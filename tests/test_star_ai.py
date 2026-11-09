"""Unit tests for the optional Star AI project-specific assistant (offline by default)."""
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'ish' / 'star_ai.py'
spec = importlib.util.spec_from_file_location('star_ai', MODULE)
ai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai)


class AssistantSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'research').mkdir()
        (self.root / 'README.md').write_text('Star Cyber Audit offline static analysis.\n', encoding='utf-8')
        (self.root / 'docs' / 'guide.md').write_text('QR metadata is not proof of backend authorization.\n', encoding='utf-8')
        (self.root / 'research' / 'secret.txt').write_text('QR backend secret hidden\n', encoding='utf-8')
        (self.root / '.env').write_text('OPENAI_API_KEY=fake', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_knowledge_allowlist(self):
        files = {p.relative_to(self.root).as_posix() for p in ai.allowed_files(self.root)}
        self.assertEqual(files, {'README.md', 'docs/guide.md'})

    def test_knowledge_no_symlink(self):
        outside = self.root.parent / 'outside_secrets.txt'
        (self.root / 'docs' / 'link.md').symlink_to(outside)
        paths = [p.name for p in ai.allowed_files(self.root)]
        self.assertNotIn('link.md', paths)

    def test_offline_search_has_file_line(self):
        rows = ai.search(self.root, 'QR authorization')
        self.assertTrue(rows)
        self.assertIn('docs/guide.md:1-', ai.evidence_block(rows))
        self.assertNotIn('secret hidden', ai.evidence_block(rows))

    def test_redaction(self):
        raw = 'Authorization: Bearer abc.123.xYz\nEmail user@example.org\nsk-proj-AABBCCDDEEFF0011223344\nCookie: id=abc'
        cleaned = ai.redact(raw)
        self.assertNotIn('abc.123', cleaned)
        self.assertNotIn('user@example.org', cleaned)
        self.assertNotIn('AABBCC', cleaned)
        self.assertNotIn('id=abc', cleaned)

    def test_explicit_cloud_consent_required(self):
        buf = io.StringIO()
        with patch.object(ai.urllib.request, 'urlopen', side_effect=AssertionError('network called')):
            with contextlib.redirect_stderr(buf):
                rc = ai.main(['--root', str(self.root), 'ask', 'QR', '--cloud'])
        self.assertEqual(rc, 2)
        self.assertIn('blocked', buf.getvalue())

    def test_local_works_with_network_disabled(self):
        with patch.object(ai.urllib.request, 'urlopen', side_effect=AssertionError('network called')):
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ai.main(['--root', str(self.root), 'ask', 'QR'])
        self.assertEqual(rc, 0)

    def test_cloud_response_parsing(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def read(self, *args):
                return b'{"output":[{"type":"message","content":[{"type":"output_text","text":"Citation docs/guide.md:1"}]}]}'

        with patch.object(ai.urllib.request, 'urlopen', return_value=FakeResponse()) as urlopen:
            result = ai.cloud_answer('QR?', [(10, 'docs/guide.md', 1, 1, 'Safe evidence')], 'example-model', 'fake-key')
        self.assertIn('Citation', result)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, 'https://api.openai.com/v1/responses')
        self.assertIn('"store": false', request.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
