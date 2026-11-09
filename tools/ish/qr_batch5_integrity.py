#!/usr/bin/env python3
"""Offline integrity/anchor verification for 2026-11-09 QR/UBOOR review batch.

Reads repository-local files only; does not execute the archived JS, access
government systems, or display full source/QR/customer data.
"""
import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = Path("reviews/2026-11-09/qr-uboor-batch-5")


def utf16_length(value):
    """Equivalent to JavaScript String.length for code-point slices."""
    return len(value.encode("utf-16-le")) // 2


def git_blob_sha(raw):
    prefix = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + raw).hexdigest()


def byte_checks(raw):
    return {"bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_sha1": git_blob_sha(raw)}


def scan(root=REPO_ROOT):
    manifest = json.loads((root / REPORT_DIR / "manifest.json").read_text("utf-8"))
    anchor_db = json.loads((root / REPORT_DIR / "SOURCE_ANCHORS.json").read_text("utf-8"))
    outcomes = []
    for entry in manifest["files"]:
        path = root / entry["repository_path"]
        if not path.is_file():
            outcomes.append({"file": entry["canonical_name"], "ok": False,
                             "error": "missing archived source"})
            continue
        raw = path.read_bytes()
        actual = byte_checks(raw)
        ok = (actual["bytes"] == entry["bytes"]
              and actual["sha256"] == entry["sha256"]
              and actual["git_blob_sha1"] == entry["git_blob_sha1"])
        outcomes.append({"file": entry["canonical_name"], "ok": ok,
                         "status": entry["status"]})
    anchor_results = []
    for file in anchor_db["files"]:
        path = root / file["source"]
        if not path.is_file():
            anchor_results.append({"file": Path(file["source"]).name,
                                   "matched": 0, "total": len(file["anchors"])})
            continue
        source = path.read_text("utf-8")
        found = 0
        for anchor in file["anchors"]:
            needle = anchor["fragment"]
            point = source.find(needle)
            offset = utf16_length(source[:point]) if point >= 0 else -1
            line = source.count("\n", 0, point) + 1 if point >= 0 else None
            if (point >= 0 and offset == anchor["offset_utf16"]
                    and line == anchor["physical_line"]):
                found += 1
        anchor_results.append({"file": Path(file["source"]).name,
                               "matched": found, "total": len(file["anchors"])})
    return {
        "offline": True,
        "source_count": len(outcomes),
        "verified_sources": sum(row["ok"] for row in outcomes),
        "anchors": anchor_results,
        "all_valid": (all(row["ok"] for row in outcomes)
                      and all(row["matched"] == row["total"] for row in anchor_results)),
        "note": "Static source integrity and literal anchor match only; NOT live backend validation.",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=REPO_ROOT,
                   help="Root of local clone of Star-Cyber-Audit-iSH")
    args = p.parse_args(argv)
    try:
        result = scan(args.root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        p.error(f"Invalid archive or manifest: {exc}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
