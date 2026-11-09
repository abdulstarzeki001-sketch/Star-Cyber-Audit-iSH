"""Regression checks for private UBOOR historical screenshot transcription."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/ish/uboor_73_integrity.py"
spec = importlib.util.spec_from_file_location("uboor_73_integrity", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Uboor73IntegrityTests(unittest.TestCase):
    def test_original_and_index_match_each_line(self):
        r = audit.verify(ROOT)
        self.assertTrue(r["every_source_line_matches_index"] if "every_source_line_matches_index" in r else r["checks"]["every_source_line_matches_index"])
        self.assertEqual(r["indexed_rows"], 2291)
        self.assertTrue(r["all_valid"], r)

    def test_file_size_and_original_blob_match(self):
        raw = (ROOT / audit.SOURCE).read_bytes()
        self.assertEqual(len(raw), audit.EXPECTED_BYTES)
        self.assertEqual(audit.git_blob_sha1(raw), audit.EXPECTED_GIT_BLOB_SHA1)

    def test_73_entries_65_images_are_descriptors(self):
        raw = (ROOT / audit.SOURCE).read_text("utf-8")
        self.assertIn("73 مدخلاً تحليلياً / 65 صورة أصلية", raw)
        self.assertIn("لا تمثل سجلات حيّة", raw)

    def test_distinct_lookup_identifiers(self):
        raw = (ROOT / audit.SOURCE).read_text("utf-8")
        for key in ("company_hash_code", "parent_hash_id", "hash_id"):
            self.assertIn(key, raw)

    def test_primary_method_claims_have_graph_entries(self):
        graph = json.loads((ROOT / audit.REPORT / "EVIDENCE_GRAPH.json").read_text("utf-8"))
        byid = {v["id"]: v for v in graph["entities"]}
        self.assertEqual(byid["search"]["method"], "POST")
        self.assertEqual(byid["items"]["method"], "GET")
        self.assertEqual(byid["company_document"]["method"], "POST")

    def test_response_body_of_company_doc_is_not_claimed(self):
        graph = json.loads((ROOT / audit.REPORT / "EVIDENCE_GRAPH.json").read_text("utf-8"))
        doc = next(v for v in graph["entities"] if v["id"] == "company_document")
        self.assertFalse(doc["response_observed"])
        self.assertTrue(doc["unknown_response_content"])

    def test_ocr_quality_limitation_persists(self):
        text = (ROOT / audit.SOURCE).read_text("utf-8")
        self.assertIn("[قراءة مرجحة]", text)
        self.assertIn("[مقتطع]", text)
        self.assertIn("ليست HAR أو JSON أصلياً", text)

    def test_offline_tool_does_not_log_sensitive_values(self):
        output = json.dumps(audit.verify(ROOT), ensure_ascii=False)
        self.assertNotIn("company_phone_number:", output)
        self.assertNotIn("Authorization: Bearer", output)
        self.assertNotIn("company_hash_code=", output)

    def test_git_blob_hash_uses_header_length(self):
        raw = b"hello"
        expected = hashlib.sha1(b"blob 5\x00" + raw).hexdigest()
        self.assertEqual(audit.git_blob_sha1(raw), expected)

    def test_short_source_not_a_valid_complete_evidence_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / audit.SOURCE
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic fixture; not an original")
            (Path(tmp) / audit.REPORT).mkdir(parents=True)
            with self.assertRaises(OSError):
                audit.verify(Path(tmp))


if __name__ == "__main__":
    unittest.main()
