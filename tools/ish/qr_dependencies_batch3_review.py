#!/usr/bin/env python3
"""Offline, read-only verifier for the 2026-11-08 QR/UBOOR dependencies batch.

Reads local uploaded JS only. Never executes JS, fetches government APIs,
decodes user QR data, or prints source strings and credentials.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = {
    "jsQR-CKtgBSaS.js": "7b28d8063265694524209c30a0b20471c0ae3f85cf5c260a469907740bcb28a4",
    "StationsDetailsModal.vue_vue_type_script_setup_true_lang-CppuJXhm.js": "8afe444c1fe2203397347394dd66b198ec611fc657f8907f933b6e78269d4b94",
    "Modal-C_od4hhs.js": "04830b150d5a6dda684a75c954409c44b5b1c1e2ecd685b198deb49217a25194",
    "index-BKvq_4_A.js": "25bd2f9df43d5ed1ae182f1dd68d1c05f735a5352ce7fe9149af501a1c706f05",
    "browser-3Qg8aFGH.js": "ac20dcd5e80b582864e38bd16a87f2068f938b6b32785f5ddd5a4b9ed7b3e0af",
    "Select-DZpjzzNJ.js": "0c230f2ecf805c6253fbe14adc9ce43944a85074b098024a2513f2fd4a348254",
    "QrLocalImporter-DYzNB5Fh(2).js": "59ff26bfbc4b731799101527e9604fc736c170e80e4988eb69be672990cf8208",
    "CompanyOwnerView-CIdFF3LL(3).js": "78af159ff95bf493a5050b4fb0fe6e4068ee49576100829ce1783644f92d2b2d",
    "FormField-DW4k76E2.js": "a88958cbe6ad3a4b53f9e4c93cc129553ecdae580144f96d6a60596aa84ccca7",
    "useAttachments-YD2hRx7D.js": "384aa93decf853b8135044a50511b472c7860c564e81467565b43b87ed40d173",
}
DEFAULT_ENTRANCE_NAME = "EntranceGateView-B9IBJo4k.js"

def safe_read(path, limit=2_000_000):
    if not path.is_file() or not 0 < path.stat().st_size <= limit:
        raise ValueError(f"Missing, empty or oversized file: {path.name}")
    raw = path.read_bytes()
    head = raw[:1024].lstrip().lower()
    if head.startswith((b"<html", b"<!doctype", b"<head")) or b"\x00" in head:
        raise ValueError(f"Not a JavaScript source: {path.name}")
    return raw

def inspect_batch(root):
    inventory = []
    sources = {}
    for name, expected in EXPECTED_SHA256.items():
        raw = safe_read(root / name)
        sha256 = hashlib.sha256(raw).hexdigest()
        sources[name] = raw.decode("utf-8", "replace")
        inventory.append({
            "name": name, "bytes": len(raw), "sha256": sha256,
            "matches_reviewed_version": sha256 == expected,
        })
    return inventory, sources

def inspect_attachment_contract(parent, child, downloader):
    """Cross-source observations, not evidence of backend vulnerability."""
    return {
        "parent_passes_registration_paths": '"attachments-register":' in parent,
        "child_declares_registration_prop": "attachmentsRegister:" in child,
        "child_displays_entrance_attachments": "attachmentsEntrance" in child,
        "child_displays_sonography_attachments": "attachmentsSonography" in child,
        "child_emits_download_file": 'emits:["close","download-file"]' in child,
        "parent_handles_download_file": "onDownloadFile" in parent,
        "downloader_uses_download_file_api": '"carrier_register/download_file"' in downloader,
        "downloader_requests_blob": 'responseType:"blob"' in downloader,
        "registration_paths_not_rendered": (
            '"attachments-register":' in parent and
            "attachmentsRegister:" not in child and
            "attachmentsEntrance" in child and
            "attachmentsSonography" in child
        ),
    }

def inspect_renderers(sources):
    reader = sources["jsQR-CKtgBSaS.js"]
    maker = sources["browser-3Qg8aFGH.js"]
    snapshot = sources["index-BKvq_4_A.js"]
    return {
        "jsqr_decoder_present": "binaryData" in reader and "location:" in reader,
        "qr_generator_to_data_url_present": "z.toDataURL=" in maker,
        "snapshot_to_blob_export_present": "export{Ut as t}" in snapshot,
        "snapshot_fetches_embedded_resources": "await fetch(t,e)" in snapshot,
    }

def analyze(root, entrance=None):
    inventory, sources = inspect_batch(root)
    parent = safe_read(entrance).decode("utf-8", "replace") if entrance else None
    child = sources["StationsDetailsModal.vue_vue_type_script_setup_true_lang-CppuJXhm.js"]
    downloader = sources["useAttachments-YD2hRx7D.js"]
    result = {
        "scope": "static local inspection only; no live endpoints or signature checks",
        "files": inventory,
        "rendering_library_roles": inspect_renderers(sources),
    }
    if parent is not None:
        result["station_attachment_contract"] = inspect_attachment_contract(
            parent, child, downloader
        )
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="Directory containing the 10 user-supplied JS files")
    parser.add_argument("--entrance", type=Path, default=None,
                        help="Optional local EntranceGateView JS for cross-file comparison")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.root, args.entrance)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
