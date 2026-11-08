"""Offline synthetic coverage for ShipmentDoc review indicators."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "ish" / "shipment_doc_review.py"
spec = importlib.util.spec_from_file_location("shipment_doc_review", MODULE)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
MARKER = '__name:"ShipmentDoc"'

class TestShipmentDocReview(unittest.TestCase):
    def test_rules_are_unique(self):
        ids = [x[0] for x in review.RULES]
        self.assertEqual(len(ids), 26)
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_rules_in_synthetic_bundle(self):
        source = MARKER + ";".join(fragment for _, _, fragments, _ in review.RULES for fragment in fragments)
        findings = review.inspect(source)
        self.assertEqual({item["id"] for item in findings},
                         {item[0] for item in review.RULES})

    def test_missing_shipment_doc_rejected(self):
        with self.assertRaises(ValueError):
            review.inspect('__name:"CompanyOwnerLayout"')

    def test_data_image_not_confused_with_robot(self):
        findings = review.inspect(MARKER + ';r.startsWith("data:image")')
        ids = {item["id"] for item in findings}
        self.assertIn("SD-06", ids)
        self.assertNotIn("SD-07", ids)
        self.assertNotIn("SD-08", ids)

    def test_vehicle_fallback_is_not_signature_verification(self):
        findings = review.inspect(MARKER + ';i?.license_approval_number||i?.vehicle_number||i?.driver_name||""')
        self.assertIn("SD-11", [item["id"] for item in findings])
        self.assertNotIn("SD-05", [item["id"] for item in findings])

    def test_reject_html_waf_binary_or_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.js"
            for content in (b"<!DOCTYPE html><html></html>", b"<html>WAF</html>",
                            b"abc\x00def", b""):
                path.write_bytes(content)
                with self.subTest(content=content[:15]):
                    with self.assertRaises(ValueError):
                        review.read_js(path)

    def test_analyze_local_synthetic_source_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.js"
            path.write_text(MARKER + ';Q.toDataURL(n,{width:200,margin:1})', encoding="utf-8")
            result = review.analyze_path(path)
            self.assertEqual(result["source_filename"], "synthetic.js")
            self.assertFalse(result["matches_reviewed_version"])
            self.assertEqual([x["id"] for x in result["indicators"]], ["SD-02", "SD-12"])
            self.assertEqual(len(result["sha256"]), 64)

def add_rule_test(rule):
    ident, description, fragments, area = rule
    def test(self):
        source = MARKER + ";" + ";".join(fragments)
        matched = {finding["id"] for finding in review.inspect(source)}
        self.assertIn(ident, matched, msg=description)
    setattr(TestShipmentDocReview, "test_indicator_" + ident.lower().replace("-", "_"), test)

for _rule in review.RULES:
    add_rule_test(_rule)

if __name__ == "__main__":
    unittest.main()
