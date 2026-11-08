"""Synthetic regression tests for the fourth user JS review batch."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/ish/uploaded_js_batch4_review.py"
spec = importlib.util.spec_from_file_location("uploaded_js_batch4_review", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Batch4Tests(unittest.TestCase):
    def test_three_reviewed_sources(self):
        self.assertEqual(len(audit.SHA256), 3)
        self.assertEqual(len(audit.PATTERNS), 3)

    def test_unique_named_indicators(self):
        ids = [ident for rules in audit.PATTERNS.values() for ident, _, _ in rules]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 26)

    def test_all_rules_detected_on_synthetic_source(self):
        for name, rules in audit.PATTERNS.items():
            with self.subTest(name=name):
                source = ";".join(fragment for _, fragment, _ in rules)
                self.assertEqual(
                    {x["id"] for x in audit.inspect_source(name, source)},
                    {x[0] for x in rules},
                )

    def test_unrelated_patterns_not_matched(self):
        checks = audit.inspect_source("IndexPage-cUNA67sR.js", 'console.log("hello")')
        self.assertEqual(checks, [])

    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):
            audit.inspect_source("unknown.js", "")

    def test_html_binary_and_empty_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "source.js"
            for raw in (b"", b"<!DOCTYPE html><html></html>", b"<head>WAF</head>",
                        b"abc\x00def"):
                p.write_bytes(raw)
                with self.subTest(raw=raw[:20]):
                    with self.assertRaises(ValueError):
                        audit.read_js(p)

    def test_all_three_files_generate_hashes_without_network(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for name in audit.SHA256:
                (root / name).write_bytes(b"//synthetic-source\n")
            result = audit.inspect_directory(root)
            self.assertEqual(len(result["files"]), 3)
            self.assertTrue(all(not x["matches_reviewed_source"] for x in result["files"]))
            self.assertEqual(result["indicator_count"], 0)
            self.assertTrue(all(len(x["sha256"]) == 64 for x in result["files"]))

    def test_main_bundle_indicators_on_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for name in audit.SHA256:
                (root / name).write_bytes(b"//test")
            main = root / "index-gleMzSil.js"
            main.write_text(";".join(fragment for _, fragment, _ in audit.MAIN_BUNDLE))
            result = audit.inspect_directory(root, main)
            self.assertEqual(
                {x["id"] for x in result["main_bundle_indicators"]},
                {x[0] for x in audit.MAIN_BUNDLE},
            )

    def test_report_does_not_emit_raw_script_contents(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for name in audit.SHA256:
                (root / name).write_bytes(b"var SECRET_MARKER = 'not-real';")
            result = audit.inspect_directory(root)
            self.assertNotIn("SECRET_MARKER", str(result))

    def test_hash_stability(self):
        payload = b"hello synthetic js"
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         hashlib.sha256(payload).hexdigest())


def install_indicator_test(name, rule):
    ident, fragment, desc = rule
    def test(self):
        actual = audit.inspect_source(name, "/*fixture*/" + fragment)
        self.assertIn(ident, {x["id"] for x in actual}, desc)
    setattr(Batch4Tests, "test_indicator_" + ident.lower().replace("-", "_"), test)


for filename, rules in audit.PATTERNS.items():
    for rule in rules:
        install_indicator_test(filename, rule)


if __name__ == "__main__":
    unittest.main()
