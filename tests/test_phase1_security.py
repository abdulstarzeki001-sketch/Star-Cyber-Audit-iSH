"""Regression tests for the Phase 1 security foundation. No target network calls."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.security import core, rule_engine, secret_scan, compare_reports

ROOT = Path(__file__).resolve().parents[1]


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "research").mkdir()
        (self.root / "config").mkdir()
        (self.root / "config/security_rules.json").write_text(
            (ROOT / "config/security_rules.json").read_text(encoding="utf-8"),
            encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_findings_have_line_and_no_source_excerpts(self):
        (self.root / "src/demo.js").write_text(
            "const a = 1;\nconst b = eval(userInput);\n"
            "el.innerHTML = content;\n", encoding="utf-8")
        result = rule_engine.scan(self.root, self.root / "config/security_rules.json")
        ids = {f["rule_id"] for f in result["findings"]}
        self.assertTrue({"SC-EVAL", "SC-HTML"} <= ids)
        self.assertTrue(any(f["line"] == 2 and f["path"] == "src/demo.js"
                            for f in result["findings"]))
        self.assertNotIn("userInput", json.dumps(result))
        self.assertEqual(result["proven_vulnerabilities"], 0)

    def test_archive_exclusion_and_opt_in(self):
        (self.root / "research/archived.js").write_text(
            "eval('research-only');", encoding="utf-8")
        offline = rule_engine.scan(self.root, self.root / "config/security_rules.json")
        self.assertFalse(offline["findings"])
        selected = rule_engine.scan(self.root, self.root / "config/security_rules.json",
                                    include_evidence=True)
        self.assertTrue(selected["findings"])

    def test_untrusted_rules_fail_validation(self):
        config = self.root / "config/security_rules.json"
        config.write_text(json.dumps({"schema_version": 1, "rules": [
            {"id": "SC-INVALID", "title": "Invalid", "severity": "high",
             "recommendation": "none", "extensions": [".js"], "pattern": "("}
        ]}), encoding="utf-8")
        with self.assertRaises(Exception):
            rule_engine.load_rules(config)

    def test_symlink_is_not_followed(self):
        (self.root / "src/example.js").symlink_to(self.root / "research/target.js")
        self.assertNotIn("example.js",
                         {p.name for p in core.project_files(self.root)})

    def test_no_network_during_scan(self):
        (self.root / "src/demo.py").write_text("verify=False\n", encoding="utf-8")
        with patch("socket.socket", side_effect=AssertionError("network attempt")):
            result = rule_engine.scan(self.root, self.root / "config/security_rules.json")
        self.assertGreater(result["files_scanned"], 0)


class TestSecretScan(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_high_confidence_secrets_are_redacted(self):
        # Assemble fixture strings to avoid leaving literal secret-shaped tokens
        # in the repository source code.
        token = "sk-" + "proj-" + ("A" * 30)
        github = "ghp_" + ("B" * 36)
        content = "const a='" + token + "';\nconst b='" + github + "';\n"
        (self.root / "example.js").write_text(content, encoding="utf-8")
        result = secret_scan.scan(self.root)
        self.assertEqual(len(result["findings"]), 2)
        self.assertEqual({f["kind"] for f in result["findings"]},
                         {"OPENAI_API_KEY", "GITHUB_TOKEN"})
        self.assertNotIn(token, json.dumps(result))
        self.assertNotIn(github, json.dumps(result))
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            status = secret_scan.main(["--root", str(self.root), "--fail-on-secrets"])
        self.assertEqual(status, 2)
        self.assertNotIn(token, captured.getvalue())

    def test_no_secret_returns_success(self):
        (self.root / "code.py").write_text("print('hello world')\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            status = secret_scan.main(["--root", str(self.root), "--fail-on-secrets"])
        self.assertEqual(status, 0)

    def test_evidence_dir_is_excluded_by_default(self):
        (self.root / "research").mkdir()
        (self.root / "research/secret.js").write_text(
            "const x='" + "sk-" + ("Q" * 40) + "';", encoding="utf-8")
        self.assertEqual(secret_scan.scan(self.root)["findings"], [])
        self.assertEqual(len(secret_scan.scan(self.root, include_evidence=True)["findings"]), 1)

    def test_oversized_file_is_skipped(self):
        (self.root / "large.js").write_text("X" * (core.MAX_BYTES + 1), encoding="utf-8")
        self.assertEqual(secret_scan.scan(self.root)["files_scanned"], 0)


class TestReportDiff(unittest.TestCase):
    def test_added_and_resolved_indicators(self):
        before = {"a.js": {"sha256": "one", "flags": {"F1"},
                           "api_paths": {"GET /old"}}}
        after = {
            "a.js": {"sha256": "two", "flags": {"F2"}, "api_paths": {"GET /old", "GET /new"}},
            "b.js": {"sha256": "new", "flags": set(), "api_paths": set()}
        }
        result = compare_reports.compare(before, after)
        s = result["summary"]
        self.assertEqual(s["files_added"], 1)
        self.assertEqual(s["files_modified"], 1)
        self.assertEqual(s["indicators_added"], 1)
        self.assertEqual(s["indicators_resolved"], 1)
        self.assertEqual(s["api_references_added"], 1)
        self.assertIn("not proven vulnerabilities", compare_reports.markdown_summary(result))

    def test_real_analysis_format_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "sample.json"
            report.write_text(json.dumps({"files": [
                {"relative_path": "src/a.js", "sha256": "abc",
                 "flags": ["REVIEW"], "api_paths": ["/api/verify/"]}
            ]}), encoding="utf-8")
            parsed = compare_reports.load_snapshot(report)
            self.assertEqual(parsed["src/a.js"]["api_paths"], {"/api/verify/"})

    def test_reject_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "duplicate.json"
            report.write_text(json.dumps({"files": [
                {"relative_path": "a.js"}, {"relative_path": "a.js"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                compare_reports.load_snapshot(report)


if __name__ == "__main__":
    unittest.main()
