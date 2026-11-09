"""Offline tests for QR/UBOOR batch-5 source integrity and documented contracts."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ish" / "qr_batch5_integrity.py"
spec = importlib.util.spec_from_file_location("qr_batch5_integrity", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class QRBatch5Tests(unittest.TestCase):
    def test_manifest_has_seven_uploaded_sources(self):
        data = json.loads((ROOT / audit.REPORT_DIR / "manifest.json").read_text("utf-8"))
        self.assertEqual(len(data["files"]), 7)
        self.assertEqual(sum(row["status"] == "new" for row in data["files"]), 2)
        self.assertEqual(sum(row["status"] == "duplicate" for row in data["files"]), 5)

    def test_two_new_sources_and_five_reused_sources(self):
        data = json.loads((ROOT / audit.REPORT_DIR / "manifest.json").read_text("utf-8"))
        new = [row for row in data["files"] if row["status"] == "new"]
        self.assertEqual({row["canonical_name"] for row in new},
                         {"AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5.js",
                          "BaseModal-DjCaQzje.js"})

    def test_all_sources_verify_against_exact_raw_bytes(self):
        result = audit.scan(ROOT)
        self.assertEqual(result["verified_sources"], 7)
        self.assertTrue(result["all_valid"], result)

    def test_sixty_anchor_positions_verify(self):
        result = audit.scan(ROOT)
        self.assertEqual(sum(x["total"] for x in result["anchors"]), 60)
        self.assertEqual(sum(x["matched"] for x in result["anchors"]), 60)

    def test_valid_git_blob_sha1_calculation(self):
        content = b"example\n"
        expected = hashlib.sha1(b"blob 8\0" + content).hexdigest()
        self.assertEqual(audit.git_blob_sha(content), expected)

    def test_utf16_offset_supports_non_bmp_unicode(self):
        self.assertEqual(audit.utf16_length("hello"), 5)
        self.assertEqual(audit.utf16_length("a\U0001f4e6b"), 4)

    def test_source_entry_path_reuses_existing_archives(self):
        data = json.loads((ROOT / audit.REPORT_DIR / "manifest.json").read_text("utf-8"))
        for row in data["files"]:
            with self.subTest(name=row["canonical_name"]):
                self.assertTrue((ROOT / row["repository_path"]).is_file())

    def test_distinguishes_root_page_count_from_total_pages_prop(self):
        s = (ROOT / "research/user-supplied/2026-11-09/"
             "AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5.js").read_text("utf-8")
        self.assertIn('Math.max(1,Math.ceil(e.total/(e.itemsPerPage||1)))', s)
        self.assertIn('totalPages:{type:Number', s)
        self.assertIn('n("per-page-changed",{page:1,per_page:r})', s)
        self.assertIn('n("page-changed",{page:c,per_page:e.perPage})', s)

    def test_modal_scroll_lock_resets_inline_styles(self):
        s = (ROOT / "research/user-supplied/2026-11-09/"
             "BaseModal-DjCaQzje.js").read_text("utf-8")
        for token in ('document.body.style.overflow="hidden"',
                      'document.body.style.overflow=""',
                      'document.body.style.paddingRight=""',
                      'role:"dialog"', '"aria-modal":"true"'):
            self.assertIn(token, s)

    def test_missing_archive_is_reported_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / audit.REPORT_DIR
            base.mkdir(parents=True)
            for filename in ("manifest.json", "SOURCE_ANCHORS.json"):
                (base / filename).write_bytes((ROOT / audit.REPORT_DIR / filename).read_bytes())
            result = audit.scan(Path(tmp))
            self.assertEqual(result["verified_sources"], 0)
            self.assertFalse(result["all_valid"])

    def test_report_does_not_expose_source_content(self):
        text = str(audit.scan(ROOT))
        self.assertNotIn("function n(o)", text)
        self.assertNotIn("Authorization:", text)


if __name__ == "__main__":
    unittest.main()
