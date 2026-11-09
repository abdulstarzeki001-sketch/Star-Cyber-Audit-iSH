#!/usr/bin/env python3
"""Offline secret leak scanner. Never displays or uploads matched secret values."""
import argparse
import re
from pathlib import Path

from .core import project_files, numbered_lines, save_report

ROOT = Path(__file__).resolve().parents[2]
# High-confidence identifiers only. Patterns and reports do not contain matched values.
PATTERNS = {
    "OPENAI_API_KEY": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{22,}\b"),
    "GITHUB_TOKEN": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "AWS_ACCESS_KEY_ID": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GOOGLE_API_KEY": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "SLACK_TOKEN": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "PRIVATE_KEY_HEADER": re.compile(
        r"-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"),
}
MAX_LINE_LENGTH = 20_000


def scan(root, include_evidence=False):
    root = Path(root).resolve(strict=True)
    findings = []
    inspected = 0
    for path in project_files(root, include_evidence=include_evidence):
        inspected += 1
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(numbered_lines(path), 1):
            # Fixed-size, bounded regex inputs; no sample/token retained.
            clipped = line[:MAX_LINE_LENGTH]
            for name, detector in PATTERNS.items():
                if detector.search(clipped):
                    findings.append({
                        "path": rel, "line": number, "kind": name,
                        "severity": "high", "value_included": False
                    })
    findings.sort(key=lambda f: (f["path"], f["line"], f["kind"]))
    return {
        "schema_version": 1,
        "tool": "star-secret-scan",
        "static_read_only": True,
        "scope_note": "First-party local files by default; excludes archived evidence and oversized files.",
        "files_scanned": inspected,
        "findings": findings
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local high-confidence secret leak scanner")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--include-evidence", action="store_true")
    parser.add_argument("--fail-on-secrets", action="store_true",
                        help="exit 2 if any high-confidence candidate exists")
    parser.add_argument("--json", type=Path, help="save metadata-only report here")
    args = parser.parse_args(argv)
    try:
        report = scan(args.root, args.include_evidence)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        save_report(report, args.json)
    print("Secret scan: {} local files, {} high-confidence candidates. No values printed.".format(
        report["files_scanned"], len(report["findings"])))
    for finding in report["findings"][:25]:
        print("  {}:{} [{}]".format(finding["path"], finding["line"], finding["kind"]))
    if len(report["findings"]) > 25:
        print("  ... {} additional candidates (see JSON metadata)".format(
            len(report["findings"]) - 25))
    return 2 if args.fail_on_secrets and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
