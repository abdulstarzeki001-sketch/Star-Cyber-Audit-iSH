"""Synthetic, offline regression coverage for both customs gate views."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "ish" / "gate_views_review.py"
spec = importlib.util.spec_from_file_location("gate_views_review", MODULE)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

class GateViewReviewTest(unittest.TestCase):
    def test_rule_counts_and_unique_ids(self):
        expected = {"entrance": 18, "exit": 9}
        for kind, count in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(len(review.RULES[kind]), count)
                ids = [row[0] for row in review.RULES[kind]]
                self.assertEqual(len(set(ids)), count)

    def test_all_indicators_can_match_synthetic_source(self):
        for kind, rules in review.RULES.items():
            with self.subTest(kind=kind):
                synthetic = review.MARKERS[kind] + ";" + ";".join(
                    token for _, _, tokens in rules for token in tokens
                )
                ids = {record["id"] for record in review.scan_source(synthetic, kind)}
                self.assertEqual(ids, {record[0] for record in rules})

    def test_refuse_mismatched_component(self):
        with self.assertRaises(ValueError):
            review.scan_source(review.MARKERS["exit"], "entrance")
        with self.assertRaises(ValueError):
            review.scan_source(review.MARKERS["entrance"], "exit")

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            review.scan_source("anything", "other")

    def test_camera_policy_distinction(self):
        entrance = review.MARKERS["entrance"] + '!x.startsWith("http")||!x.startsWith("https://")'
        exit_source = review.MARKERS["exit"] + '!a.startsWith("http://")&&!a.startsWith("https://")'
        self.assertIn("EG-12", {x["id"] for x in review.scan_source(entrance, "entrance")})
        self.assertIn("XG-05", {x["id"] for x in review.scan_source(exit_source, "exit")})
        self.assertNotIn("EG-13", {x["id"] for x in review.scan_source(entrance, "entrance")})

    def test_html_or_binary_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "artifact.js"
            for data in (b"<html>WAF challenge</html>", b"<!doctype html>",
                         b"\x00binary", b""):
                path.write_bytes(data)
                with self.subTest(data=data[:16]):
                    with self.assertRaises(ValueError):
                        review.read_local_js(path)

    def test_file_hash_and_no_network(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fixture.js"
            path.write_text(review.MARKERS["exit"] + ";navigator.mediaDevices.getUserMedia(",
                            encoding="utf-8")
            result = review.scan_file(path, "exit")
            self.assertEqual(result["bytes"], path.stat().st_size)
            self.assertFalse(result["matches_reviewed_version"])
            self.assertEqual([x["id"] for x in result["findings"]], ["XG-01", "XG-04"])
            self.assertEqual(len(result["sha256"]), 64)

def bind_rule_test(kind, rule):
    ident, title, fragments = rule
    def test(self):
        synthetic = review.MARKERS[kind] + ";" + ";".join(fragments)
        ids = {item["id"] for item in review.scan_source(synthetic, kind)}
        self.assertIn(ident, ids, title)
    setattr(GateViewReviewTest,
            "test_indicator_" + ident.lower().replace("-", "_"), test)

for _kind, _rules in review.RULES.items():
    for _rule in _rules:
        bind_rule_test(_kind, _rule)

if __name__ == "__main__":
    unittest.main()
