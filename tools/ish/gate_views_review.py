#!/usr/bin/env python3
"""Offline, read-only Vue/Vite gate-view JS indicators.

No JS execution, government API requests, authentication, QR decryption
or printing of source snippets, QR contents, customer data or tokens.
"""
import argparse
import hashlib
import json
from pathlib import Path

RULES = {
    "entrance": (
        ("EG-01", "EntranceGateView component", ('__name:"EntranceGateView"',)),
        ("EG-02", "Decision modal component", ('__name:"EntranceGateModel"',)),
        ("EG-03", "Entrance lookup API", ('J.post("carrier_register/scrape_search_goods_gateway_register"',)),
        ("EG-04", "Agent_name required for display", ('!n.data.Agent_name',)),
        ("EG-05", "GPS truthy zero guard", ('l.latitude&&l.longitude&&isFinite(l.latitude)&&isFinite(l.longitude)',)),
        ("EG-06", "Entrance decision API", ('J.post("carrier_register/gateway_decision",g)',)),
        ("EG-07", "Decision sent using multipart FormData", ("const g=new FormData",)),
        ("EG-08", "Attachment multipart slots", ('attachment[',)),
        ("EG-09", "Approved decision value", ('value:"APPROVED"',)),
        ("EG-10", "Rejected decision value", ('value:"REJECTED"',)),
        ("EG-11", "UI privilege gate", ('"gateway_decision"',)),
        ("EG-12", "Camera URL accepts HTTPS only", ('!x.startsWith("http")||!x.startsWith("https://")',)),
        ("EG-13", "Manual input submits without same camera check", ('M.value.trim()&&(await V(M.value.trim())',)),
        ("EG-14", "Generic success toast for decision", ('"تم إرسال قرار الموافقة بنجاح"',)),
        ("EG-15", "Captured photo as JPEG", ('a.toDataURL("image/jpeg")',)),
        ("EG-16", "jsQR scanner import", ('./jsQR-CKtgBSaS.js',)),
        ("EG-17", "Decision only offered for undefined status", ('status=="غير محددة"',)),
        ("EG-18", "Lookup response hash ID passed to decision", ('o.value.hash_id=n.data.hash_id',)),
    ),
    "exit": (
        ("XG-01", "ExitGateView component", ('__name:"ExitGateView"',)),
        ("XG-02", "useExitGate dependency", ('./useExitGate-BvHNutwH.js',)),
        ("XG-03", "jsQR dependency", ('./jsQR-CKtgBSaS.js',)),
        ("XG-04", "Media camera initialization", ('navigator.mediaDevices.getUserMedia(',)),
        ("XG-05", "Camera accepts HTTP or HTTPS", ('!a.startsWith("http://")&&!a.startsWith("https://")',)),
        ("XG-06", "Manual input passed to imported function", ('c.value.trim()&&(await _(c.value.trim())',)),
        ("XG-07", "Video frame scan loop", ('d=requestAnimationFrame(y)',)),
        ("XG-08", "Cancels animation on cleanup", ('cancelAnimationFrame(d)',)),
        ("XG-09", "Stops tracks on cleanup", ('u.getTracks().forEach(a=>a.stop())',)),
    ),
}
MARKERS = {"entrance": '__name:"EntranceGateView"', "exit": '__name:"ExitGateView"'}
SHA256 = {
    "entrance": "d48910ae500903a80deaf740cba67485c76e3af789fcff2e1f4d6f86d2419988",
    "exit": "4c7d47c65b845c7b00143dfed244f28435cf5e2c64d6da9330820b3b53fbdc52",
}

def read_local_js(path, max_bytes=1_000_000):
    if not path.is_file() or not 0 < path.stat().st_size <= max_bytes:
        raise ValueError("JavaScript file is missing, empty, or too large")
    raw = path.read_bytes()
    start = raw[:1024].lstrip().lower()
    if b"\x00" in start or start.startswith((b"<!doctype", b"<html", b"<head")):
        raise ValueError("Unexpected HTML/WAF/binary response instead of JS")
    return raw

def scan_source(source, kind):
    if kind not in RULES:
        raise ValueError("Unknown view type")
    if MARKERS[kind] not in source:
        raise ValueError("Requested view marker missing from input")
    return [{"id": key, "indicator": description} for key, description, needles in RULES[kind]
            if all(needle in source for needle in needles)]

def scan_file(path, kind):
    raw = read_local_js(path)
    checksum = hashlib.sha256(raw).hexdigest()
    return {
        "filename": path.name,
        "bytes": len(raw),
        "sha256": checksum,
        "matches_reviewed_version": checksum == SHA256[kind],
        "kind": kind,
        "findings": scan_source(raw.decode("utf-8", "replace"), kind),
        "scope": "offline static frontend review only; no backend or official validity checks",
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Local EntranceGateView or ExitGateView JS")
    parser.add_argument("--view", choices=tuple(RULES), required=True)
    args = parser.parse_args(argv)
    try:
        result = scan_file(args.source, args.view)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
