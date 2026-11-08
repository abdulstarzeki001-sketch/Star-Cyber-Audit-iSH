#!/usr/bin/env python3
"""Read-only, offline indicators for an uploaded ShipmentDoc Vue/Vite bundle.

No JavaScript execution, network calls, QR decryption, or document validation.
Prints SHA-256 and generic source indicators only; never source contents,
QR tokens, phone numbers, or data from a live government account.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "fb7034cc56552ec33c4a79674697dcd3691ec0dec8862fbd66c00e3ab1cfcf5b"
RULES = (
    ("SD-01", "CompanyOwnerLayout component", ('__name:"CompanyOwnerLayout"',), "layout"),
    ("SD-02", "ShipmentDoc component", ('__name:"ShipmentDoc"',), "layout"),
    ("SD-03", "document passed through doc prop", ('props:{doc:{}}',), "data_contract"),
    ("SD-04", "items rendered only if array", ('const i=u.doc?.items;return Array.isArray(i)?i.map',), "data_contract"),
    ("SD-05", "nested qr_code fallback", ('i?.qr_code||i?.response?.qr_code',), "qr_source"),
    ("SD-06", "trusts existing data image URL as image", ('r.startsWith("data:image")',), "qr_source"),
    ("SD-07", "recognizes UBOOR robot URL", ('r.startsWith("https://customs-uboor.ur.gov.iq/robot?url=")',), "qr_normalization"),
    ("SD-08", "extracts URL fragment by string split", ('r.split("url=")[1]||""',), "qr_normalization"),
    ("SD-09", "long generic Base64 text classified as image", ('/^[A-Za-z0-9+/=]+$/.test(r)&&r.length>80',), "qr_classification"),
    ("SD-10", "constructs PNG data URL for Base64", ('data:image/png;base64,',), "qr_classification"),
    ("SD-11", "license or vehicle or driver fallback for QR", ('i?.license_approval_number||i?.vehicle_number||i?.driver_name||""',), "qr_authenticity"),
    ("SD-12", "draws QR locally", ('Q.toDataURL(n,{width:200,margin:1})',), "qr_render"),
    ("SD-13", "async QR watcher", ('E(()=>u.doc,async i=>{',), "reactivity"),
    ("SD-14", "immediate deep watcher", ('{immediate:!0,deep:!0}',), "reactivity"),
    ("SD-15", "separate print window", ('window.open("","_blank","width=900,height=1000")',), "printing"),
    ("SD-16", "fallback browser print", ('window.print()',), "printing"),
    ("SD-17", "A4 printing CSS", ('@page { size: A4; margin: 0; }',), "printing"),
    ("SD-18", "fixed print page height", ('height: 296mm !important',), "printing"),
    ("SD-19", "print page overflow hidden", ('overflow: hidden;',), "printing"),
    ("SD-20", "copies inline styles for print", ('document.querySelectorAll("style")',), "printing"),
    ("SD-21", "copies linked styles for print", ('document.querySelectorAll(\'link[rel="stylesheet"]\')',), "printing"),
    ("SD-22", "prints doc_id header", ('a.doc?.doc_id||"—"',), "fields"),
    ("SD-23", "prints date or current_date", ('a.doc?.date_str||a.doc?.current_date||""',), "fields"),
    ("SD-24", "prints time_str", ('a.doc?.time_str||""',), "fields"),
    ("SD-25", "prints company name from two fields", ('a.doc?.company_name_project||a.doc?.company_name||""',), "fields"),
    ("SD-26", "prints license approval number", ('a.doc?.license_approval_number||""',), "fields"),
)

def inspect(source):
    """Match literal patterns. Findings describe source behavior, not exploits."""
    if '__name:"ShipmentDoc"' not in source:
        raise ValueError("This file does not contain the ShipmentDoc Vue component")
    return [{"id": ident, "description": label, "area": area}
            for ident, label, fragments, area in RULES
            if all(fragment in source for fragment in fragments)]

def read_js(path, max_bytes=2_000_000):
    if not path.is_file() or not (0 < path.stat().st_size <= max_bytes):
        raise ValueError("Missing, empty, or oversized source file")
    raw = path.read_bytes()
    head = raw[:1024].lstrip().lower()
    if b"\x00" in head or head.startswith((b"<!doctype", b"<html", b"<head")):
        raise ValueError("HTML/WAF or binary response is not a JavaScript bundle")
    return raw

def analyze_path(path):
    raw = read_js(path)
    indicators = inspect(raw.decode("utf-8", errors="replace"))
    sha256 = hashlib.sha256(raw).hexdigest()
    return {
        "source_filename": path.name,
        "size_bytes": len(raw),
        "sha256": sha256,
        "matches_reviewed_version": sha256 == EXPECTED_SHA256,
        "indicator_count": len(indicators),
        "indicators": indicators,
        "limitations": "frontend static evidence, no live verification or official authenticity checks",
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Local ShipmentDoc-*.js path")
    args = parser.parse_args(argv)
    try:
        output = analyze_path(args.source)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
