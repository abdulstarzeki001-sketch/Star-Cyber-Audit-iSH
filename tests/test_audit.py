import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("star_audit", ROOT / "analyze.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TestAudit(unittest.TestCase):
    def test_waf_is_not_javascript(self):
        html = b'<html><meta content="HuaweiCloudWAF"><script>function x(){}</script></html>'
        self.assertEqual(audit.classify(html), "WAF_HTML_NOT_JS")

    def test_js_routes_and_flags(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "fixture.js"
            p.write_text(
                "import './module.js'; const endpoint='local_form/read_doc_company'; "
                "console.debug('auth token:',user.token);",
                encoding="utf-8"
            )
            result = audit.analyze_one(p, "test")
            self.assertEqual(result["classification"], "JS_SOURCE")
            self.assertIn("local_form/read_doc_company", result["api_paths"])
            self.assertTrue(any("TOKEN_DEBUG" in f for f in result["flags"]))

    def test_html_not_js(self):
        self.assertEqual(audit.classify(b"<!doctype html><html></html>"), "HTML_NOT_JS")


if __name__ == "__main__":
    unittest.main()
