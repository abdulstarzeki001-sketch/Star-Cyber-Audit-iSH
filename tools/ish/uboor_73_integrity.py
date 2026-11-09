#!/usr/bin/env python3
"""Verify private UBOOR transcription and its 2291-row annotated index offline.

Reads only local repo files, never sends web/API requests, never executes any
third-party JavaScript and never prints original phone/hash/token values.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("research/private-evidence/2026-11-09/UBOOR_ALL_73_IMAGES_COMPLETE_TEXT_2026-11-09 2.txt")
REPORT = Path("reviews/2026-11-09/uboor-73-entries")
EXPECTED_BYTES = 137148
EXPECTED_LINES = 2291
EXPECTED_GIT_BLOB_SHA1 = "54282a0c7d4711a7b493d394712e02a7fb820e2f"


def git_blob_sha1(payload: bytes) -> str:
    header = b"blob " + str(len(payload)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + payload).hexdigest()


def verify(root: Path = ROOT):
    raw = (root / SOURCE).read_bytes()
    source_text = raw.decode("utf-8")
    source_lines = source_text.splitlines()
    checks = {
        "bytes_match": len(raw) == EXPECTED_BYTES,
        "lines_match": len(source_lines) == EXPECTED_LINES,
        "git_blob_sha1_match": git_blob_sha1(raw) == EXPECTED_GIT_BLOB_SHA1,
    }
    index_path = root / REPORT / "ANNOTATED_LINE_INDEX.tsv"
    with index_path.open("r", encoding="utf-8", newline="") as fp:
        table = list(csv.DictReader(fp, delimiter="\t", quoting=csv.QUOTE_NONE))
    expected_columns = {"line_no", "section", "kind", "note", "evidence_quality", "original_text"}
    checks["index_columns_match"] = bool(table) and expected_columns.issubset(table[0])
    checks["index_rows_match"] = len(table) == EXPECTED_LINES
    mismatches = []
    for number, (original, row) in enumerate(zip(source_lines, table), 1):
        archived_line = original.replace("\t", r"\t").replace("\r", r"\r")
        if row.get("line_no") != str(number) or row.get("original_text") != archived_line:
            mismatches.append(number)
    checks["every_source_line_matches_index"] = not mismatches and len(table) == len(source_lines)
    graph = json.loads((root / REPORT / "EVIDENCE_GRAPH.json").read_text("utf-8"))
    names = {entity["id"] for entity in graph["entities"]}
    checks["graph_has_three_primary_requests"] = {"search", "items", "company_document"}.issubset(names)
    checks["graph_references_valid_lines"] = all(
        1 <= number <= len(source_lines)
        for entity in graph["entities"]
        for attr in ("evidence_lines", "repeat_lines")
        for number in entity.get(attr, [])
    )
    return {
        "offline": True,
        "source_bytes": len(raw),
        "source_lines": len(source_lines),
        "source_git_blob_sha1": git_blob_sha1(raw),
        "indexed_rows": len(table),
        "index_mismatch_line_numbers": mismatches[:10],
        "checks": checks,
        "all_valid": all(checks.values()),
        "limitations": "Verifies file integrity and claim locations only; cannot verify screenshot OCR, backend authorization, issued document authenticity or QR signatures.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = verify(args.root)
    except (OSError, ValueError, KeyError, UnicodeError, json.JSONDecodeError) as error:
        parser.error(f"Invalid local repository source: {error}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
