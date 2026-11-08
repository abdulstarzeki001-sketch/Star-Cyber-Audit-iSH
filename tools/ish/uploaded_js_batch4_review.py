#!/usr/bin/env python3
"""Offline audit of user-supplied minified UBOOR frontend assets.

Only reads local JS files and emits hashes, named indicator IDs, and counts.
Does not execute JS, access a government API, verify a QR signature, or
print document values or credentials.
"""
import argparse
import hashlib
import json
from pathlib import Path

SHA256 = {
    "IndexPage-cUNA67sR.js": "05da0739f9e5ea3ea5b3f22d80ab4f63d29197b9250577ca95e2072f231b7f42",
    "CompanyOwnerCeoLoadsView-Coghn9Xh.js": "fcc33ae6957649ab3a6881196b231e1891dd7ec0d1a440b376ab45bcffefcacd",
    "useFormControl-XQpg82Ny.js": "dc0ca24e3e96bdba6e574672096fdc1f93186559ba74a2db2bc5fcaf28657b2b",
}
PATTERNS = {
    "IndexPage-cUNA67sR.js": (
        ("IDX-01", 'ge("dashboard"', "Pinia dashboard store"),
        ("IDX-02", 'q.post("metrics/kpi"', "Overview metrics API"),
        ("IDX-03", 'q.post("metrics/kpi/processing_times_by_employee"', "Employee metrics API"),
        ("IDX-04", 'q.post("metrics/kpi/vehicle_stay_duration"', "Vehicle metrics API"),
        ("IDX-05", 'toISOString().split("T")[0]', "UTC day conversion"),
        ("IDX-06", "300*1e3", "Five-minute refresh timer"),
        ("IDX-07", "criticalVehicles:t=>", "Computed vehicle array assumption"),
        ("IDX-08", "user_privileges", "Client-visible privileges"),
        ("IDX-09", "user_permissions", "Client-visible permissions"),
        ("IDX-10", '__name:"IndexPage"', "Dashboard component"),
        ("IDX-11", '__name:"DateRangeFilter"', "Date filtering component"),
        ("IDX-12", 'await Promise.all([this.fetchKpiOverview()', "Parallel overview queries"),
    ),
    "CompanyOwnerCeoLoadsView-Coghn9Xh.js": (
        ("CEO-01", '__name:"CompanyOwnerCeoLoadsView"', "Company owner load view"),
        ("CEO-02", '__name:"CompanyOwnerCeoLoads"', "Paged company load list"),
        ("CEO-03", '__name:"CompanyOwnerCeoLoadDetailModal"', "Detailed load modal"),
        ("CEO-04", "p.fetchCompanyCeoLoads(", "Store request for CEO load pagination"),
        ("CEO-05", "p.returnDocCeo(", "Store request to return printable document"),
        ("CEO-06", "c=Number(b)", "Numeric document identifier conversion"),
        ("CEO-07", "https://www.google.com/maps?q=", "Maps link"),
        ("CEO-08", "checkpoint_is_active!==!1", "Truthy default for checkpoint status"),
        ("CEO-09", "checkUserAuthentication().then(", "Client-side session gate"),
        ("CEO-10", "onPageChanged:R", "AppPagination page event"),
        ("CEO-11", 'title:"وثيقة الشحن للطباعة"', "ShipmentDoc print window"),
    ),
    "useFormControl-XQpg82Ny.js": (
        ("FORM-01", 'function n(o){return e(', "Reactive computed helper"),
        ("FORM-02", '.closest("form")', "Checks ancestor HTML form"),
        ("FORM-03", 'export{n as u}', "Exports useFormControl helper"),
    ),
}
MAIN_BUNDLE = (
    ("API-01", 'tt.post("local_form/paginate_company_ceo"', "Outgoing loads list API"),
    ("API-02", 'tt.post("local_form/return_doc_ceo"', "Return print document API"),
    ("API-03", "this.companyOwnerCeoLoads=", "Store list write"),
)

def read_js(path, max_size=2_000_000):
    if not path.is_file() or not 0 < path.stat().st_size <= max_size:
        raise ValueError(f"Missing, empty or oversized JavaScript file: {path.name}")
    data = path.read_bytes()
    start = data[:1024].lstrip().lower()
    if b"\x00" in start or start.startswith((b"<!doctype", b"<html", b"<head")):
        raise ValueError(f"Not a JavaScript source: {path.name}")
    return data

def inspect_source(name, source):
    if name not in PATTERNS:
        raise ValueError("Unknown source")
    return [{"id": ident, "description": desc}
            for ident, fragment, desc in PATTERNS[name]
            if fragment in source]

def inspect_directory(directory, main_bundle=None):
    results = []
    for filename in SHA256:
        data = read_js(directory / filename)
        digest = hashlib.sha256(data).hexdigest()
        found = inspect_source(filename, data.decode("utf-8", "replace"))
        results.append({
            "name": filename, "size_bytes": len(data), "sha256": digest,
            "matches_reviewed_source": digest == SHA256[filename],
            "detected_indicators": found,
        })
    out = {
        "scope": "static, offline source inspection; not backend verification",
        "files": results,
        "indicator_count": sum(len(item["detected_indicators"]) for item in results),
    }
    if main_bundle is not None:
        source = read_js(main_bundle).decode("utf-8", "replace")
        out["main_bundle_indicators"] = [
            {"id": ident, "description": desc}
            for ident, fragment, desc in MAIN_BUNDLE if fragment in source
        ]
    return out

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--main-bundle", type=Path)
    args = parser.parse_args(argv)
    try:
        result = inspect_directory(args.directory, args.main_bundle)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
