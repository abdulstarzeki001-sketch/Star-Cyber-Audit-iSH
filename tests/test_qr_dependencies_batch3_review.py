"""Synthetic offline tests for the third QR/UBOOR JS dependency batch."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = (Path(__file__).resolve().parents[1] / "tools" /
          "ish" / "qr_dependencies_batch3_review.py")
spec = importlib.util.spec_from_file_location("batch3_check", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Batch3ReviewTests(unittest.TestCase):
    def test_manifest_has_ten_unique_sources(self):
        self.assertEqual(len(audit.EXPECTED_SHA256), 10)
        self.assertEqual(len(set(audit.EXPECTED_SHA256)), 10)

    def test_all_sha256_expected_digest_shapes(self):
        for digest in audit.EXPECTED_SHA256.values():
            self.assertEqual(len(digest), 64)
            self.assertTrue(all(ch in "0123456789abcdef" for ch in digest))

    def test_mismatched_source_does_not_count_as_reviewed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in audit.EXPECTED_SHA256:
                (root / name).write_bytes(b"//synthetic module")
            inventory, _ = audit.inspect_batch(root)
            self.assertEqual(len(inventory), 10)
            self.assertTrue(all(not item["matches_reviewed_version"]
                                for item in inventory))

    def test_missing_bundle_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                audit.inspect_batch(Path(tmp))

    def test_html_waf_and_binary_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.js"
            for raw in (b"<html>WAF</html>", b"<!doctype html>", b"abc\x00def",
                        b""):
                p.write_bytes(raw)
                with self.subTest(raw=raw):
                    with self.assertRaises(ValueError):
                        audit.safe_read(p)

    def test_attachment_gap_detected(self):
        parent = '"attachments-register":a,onDownloadFile:x'
        child = ('emits:["close","download-file"];'
                 'attachmentsEntrance:[],attachmentsSonography:[]')
        downloader = ('i.get("carrier_register/download_file", {'
                      'responseType:"blob"})')
        r = audit.inspect_attachment_contract(parent, child, downloader)
        self.assertTrue(r["registration_paths_not_rendered"])
        self.assertTrue(r["child_emits_download_file"])
        self.assertTrue(r["downloader_uses_download_file_api"])

    def test_registration_prop_closes_gap(self):
        parent = '"attachments-register":a'
        child = 'attachmentsRegister:[],attachmentsEntrance:[],attachmentsSonography:[]'
        r = audit.inspect_attachment_contract(parent, child, "")
        self.assertFalse(r["registration_paths_not_rendered"])

    def test_no_parent_registration_no_gap(self):
        child = 'attachmentsEntrance:[],attachmentsSonography:[]'
        r = audit.inspect_attachment_contract("", child, "")
        self.assertFalse(r["registration_paths_not_rendered"])

    def test_downloader_only_does_not_prove_server_authorization(self):
        r = audit.inspect_attachment_contract("", "", 'carrier_register/download_file')
        self.assertFalse(r["downloader_uses_download_file_api"])
        self.assertNotIn("backend_authorized", r)

    def test_library_roles_positive_and_negative(self):
        source = {
            "jsQR-CKtgBSaS.js": "binaryData,location:",
            "browser-3Qg8aFGH.js": "z.toDataURL=",
            "index-BKvq_4_A.js": "export{Ut as t};await fetch(t,e)",
        }
        r = audit.inspect_renderers(source)
        self.assertTrue(all(r.values()))
        source["browser-3Qg8aFGH.js"] = "jsQR.decode"
        self.assertFalse(audit.inspect_renderers(source)["qr_generator_to_data_url_present"])

    def test_source_content_is_not_returned_from_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in audit.EXPECTED_SHA256:
                (Path(tmp) / name).write_bytes(b"//private-token=example")
            inventory, _ = audit.inspect_batch(Path(tmp))
            self.assertNotIn("private-token", repr(inventory))
            self.assertTrue(all("sha256" in item for item in inventory))

    def test_sha256_calculation_stable(self):
        fixture = b"//synthetic JS content"
        self.assertEqual(hashlib.sha256(fixture).hexdigest(),
                         hashlib.sha256(fixture).hexdigest())


if __name__ == "__main__":
    unittest.main()
