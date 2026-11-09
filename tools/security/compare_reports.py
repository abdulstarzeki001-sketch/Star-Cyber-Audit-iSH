#!/usr/bin/env python3
"""Offline comparison of two Star Cyber Audit analysis.json snapshots."""
import argparse
import json
from pathlib import Path

from .core import save_report

MAX_REPORT_BYTES = 20_000_000
MAX_DETAIL_RECORDS = 3000


def load_snapshot(path):
    path = Path(path)
    if path.stat().st_size > MAX_REPORT_BYTES:
        raise ValueError("report exceeds size limit")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("files"), list):
        raise ValueError("expected Star Cyber Audit JSON with files array")
    if len(doc["files"]) > 5000:
        raise ValueError("report contains too many entries")
    result = {}
    for item in doc["files"]:
        if not isinstance(item, dict):
            raise ValueError("invalid file record")
        name = item.get("relative_path") or item.get("name")
        if not isinstance(name, str) or not name or len(name) > 1024:
            raise ValueError("missing or invalid file path")
        # Files in separate report origins may use identical paths; default
        # analyzer itself de-duplicates by relative_path.
        if name in result:
            raise ValueError("duplicate relative_path in report")
        flags = item.get("flags") or []
        api_paths = item.get("api_paths") or []
        if (not isinstance(flags, list) or not isinstance(api_paths, list) or
                any(not isinstance(x, str) for x in flags + api_paths)):
            raise ValueError("invalid flags or api_paths")
        result[name] = {
            "sha256": item.get("sha256"),
            "flags": set(flags),
            "api_paths": set(api_paths),
        }
    return result


def compare(old, new):
    before = set(old)
    after = set(new)
    added = sorted(after - before)
    removed = sorted(before - after)
    modified = sorted(
        name for name in before & after
        if old[name]["sha256"] != new[name]["sha256"]
    )
    new_flags = []
    resolved_flags = []
    new_apis = []
    removed_apis = []
    for name in sorted(before | after):
        a = old.get(name, {"flags": set(), "api_paths": set()})
        b = new.get(name, {"flags": set(), "api_paths": set()})
        for field, new_bucket, gone_bucket in (
            ("flags", new_flags, resolved_flags),
            ("api_paths", new_apis, removed_apis),
        ):
            new_bucket.extend({"path": name, "value": v} for v in sorted(b[field] - a[field]))
            gone_bucket.extend({"path": name, "value": v} for v in sorted(a[field] - b[field]))
    return {
        "schema_version": 1,
        "tool": "star-report-diff",
        "static_read_only": True,
        "summary": {
            "before_files": len(old), "after_files": len(new),
            "files_added": len(added), "files_removed": len(removed),
            "files_modified": len(modified),
            "indicators_added": len(new_flags),
            "indicators_resolved": len(resolved_flags),
            "api_references_added": len(new_apis),
            "api_references_removed": len(removed_apis),
        },
        "changes": {
            "added_files": added[:MAX_DETAIL_RECORDS],
            "removed_files": removed[:MAX_DETAIL_RECORDS],
            "modified_files": modified[:MAX_DETAIL_RECORDS],
            "new_indicators": new_flags[:MAX_DETAIL_RECORDS],
            "resolved_indicators": resolved_flags[:MAX_DETAIL_RECORDS],
            "new_api_references": new_apis[:MAX_DETAIL_RECORDS],
            "removed_api_references": removed_apis[:MAX_DETAIL_RECORDS]
        },
        "details_capped": any(len(seq) > MAX_DETAIL_RECORDS for seq in
                              (added, removed, modified, new_flags,
                               resolved_flags, new_apis, removed_apis)),
        "interpretation": "Static evidence deltas; not proof of exploitable vulnerabilities."
    }


def markdown_summary(report):
    summary = report["summary"]
    labels = [
        ("Files before", "before_files"),
        ("Files after", "after_files"),
        ("Added files", "files_added"),
        ("Removed files", "files_removed"),
        ("Modified files", "files_modified"),
        ("New review indicators", "indicators_added"),
        ("Resolved review indicators", "indicators_resolved"),
        ("New API references", "api_references_added"),
        ("Removed API references", "api_references_removed"),
    ]
    rows = ["# Star Cyber Audit — offline comparison", "",
            "| Measure | Count |", "|---|---:|"]
    rows += ["| {} | {} |".format(label, summary[key]) for label, key in labels]
    rows += ["", "Static metadata only. Flags are **not proven vulnerabilities**."]
    if report["details_capped"]:
        rows += ["Detail lists reached the cap; refer to summary totals."]
    return "\n".join(rows) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two offline Star Cyber Audit JSON reports")
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--json", type=Path, help="optional JSON output")
    parser.add_argument("--markdown", type=Path, help="optional Markdown summary")
    args = parser.parse_args(argv)
    try:
        result = compare(load_snapshot(args.before), load_snapshot(args.after))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.json:
        save_report(result, args.json)
    note = markdown_summary(result)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(note, encoding="utf-8")
    print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
