"""Offline checks for January/November UBOOR owner-portal JS.

No network calls. Original bundles are only read.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAN = ROOT / "research/private-evidence/2026-11-09/jan-2026-bundle"
NOV = ROOT / "research/private-evidence/2026-11-09/nov-2026-bundle"
OLD = ROOT / "research/user-supplied/2026-11-08"
NOV_VIEW = ROOT / "research/raw-uploads/2026-11-07/company-owner-vite"
TEXT = ROOT / "research/private-evidence/2026-11-09/UBOOR_ALL_73_IMAGES_COMPLETE_TEXT_2026-11-09 2.txt"


class OwnerEightQuestionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jan_main_file = JAN / "index-d1j-jb9c(3).js"
        cls.jan_view_file = JAN / "companyownerview-dwbcwxr4.js"
        cls.nov_main_file = NOV / "index-ccmhdhtn.js"
        cls.nov_view_file = NOV_VIEW / "companyownerview-cjdszkn6.js"
        cls.old_view_file = OLD / "CompanyOwnerView-CIdFF3LL.js"
        cls.main = cls.jan_main_file.read_text("utf-8")
        cls.view = cls.jan_view_file.read_text("utf-8")
        cls.newview = cls.nov_view_file.read_text("utf-8")
        cls.novmain = cls.nov_main_file.read_text("utf-8")
        cls.old = cls.old_view_file.read_text("utf-8")
        cls.history = TEXT.read_text("utf-8")

    def test_original_file_sizes(self):
        self.assertEqual(self.jan_main_file.stat().st_size, 1378888)
        self.assertEqual(self.jan_view_file.stat().st_size, 38636)
        self.assertEqual(self.nov_main_file.stat().st_size, 1380214)

    def test_january_entrypoint_import_map(self):
        self.assertIn("CompanyOwnerView-DWbcwxR4.js", self.main)

    def test_owner_verification_is_an_api_call(self):
        self.assertIn("local_form/company_verify_login", self.main)
        self.assertIn("company_phone_number:t", self.main)
        self.assertIn("local_form/company_verification", self.main)
        self.assertIn("companyOwnerToken=n.data.access_token", self.main)

    def test_owner_token_is_client_storage_not_backend_proof(self):
        self.assertIn('localStorage.setItem("company_owner_token"', self.main)
        self.assertIn('localStorage.getItem("is_authenticated_owner")', self.main)
        self.assertIn('localStorage.getItem("company_user_info_owner")', self.main)

    def test_three_primary_request_methods(self):
        self.assertIn('bt.post("local_form/search_iraqi_company"', self.main)
        self.assertIn('local_form/get_company_items/', self.main)
        self.assertIn('bt.post(n,null,{headers:{Authorization:', self.main)
        self.assertIn('local_form/return_company_doc/', self.main)

    def test_return_doc_checks_nested_json_doc_id(self):
        self.assertIn('const i=s.data.data;return i&&i.doc_id?', self.main)
        self.assertIn('s.status===200||s.status===201', self.main)
        self.assertNotIn('pdf_base64', self.main)

    def test_owner_document_uses_html_print_and_qr_field(self):
        self.assertIn('m.doc?.qr_code||m.doc?.response?.qr_code', self.view)
        self.assertIn('window.print()', self.view)
        self.assertIn('quickchart.io/qr?text=', self.view)
        self.assertIn('@page { size: A4;', self.view)
        self.assertNotIn('crypto.subtle.sign', self.view)
        self.assertNotIn('crypto.subtle.verify', self.view)

    def test_owner_ur_redirect_id(self):
        self.assertIn('client_id=261', self.view)
        self.assertIn('verify-auth', self.view)

    def test_company_item_reduce_is_separate_document_path(self):
        self.assertIn('companyItemsReduce', self.view)
        self.assertIn('vihcle_info', self.view)
        self.assertIn('production_capacity', self.view)
        self.assertIn('local_form/company_item_reduce', self.main)

    def test_vite_owner_component_body_is_identical_across_builds(self):
        self.assertNotEqual(self.view.split("\n", 1)[0], self.newview.split("\n", 1)[0])
        self.assertEqual(
            self.view.split("\n", 1)[1].rstrip("\n"),
            self.newview.split("\n", 1)[1].rstrip("\n"),
        )

    def test_older_build_imports_separate_shipment_doc(self):
        self.assertIn('ShipmentDoc-Dx885_fz.js', self.old)
        self.assertIn('CompanyOwnerCeoLoads', self.old)

    def test_cors_text_is_historical_not_http_header_pair_proof(self):
        self.assertIn('Access-Control-Allow-Origin: http://localhost:5173', self.history)
        self.assertIn('Access-Control-Allow-Origin: *', self.history)
        self.assertIn('تداخل عرض', self.history)


if __name__ == "__main__":
    unittest.main()
