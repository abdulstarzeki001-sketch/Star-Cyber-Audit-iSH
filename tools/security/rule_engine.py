#!/usr/bin/env python3
"""Offline, review-only code rule engine. No active testing or code execution."""
import argparse
import json
import re
from pathlib import Path

from .core import project_files, numbered_lines, save_report

ROOT = Path(__file__).resolve().parents[2]
SEVERITIES = {"info", "low", "medium", "high"}
RULE_ID = re.compile(r"^SC-[A-Z0-9]{3,14}$")
MAX_LINE_LENGTH = 4000


def load_rules(filename):
    """Load repository-reviewed declarative regex rules, not executable plugins."""
    obj = json.loads(Path(filename).read_text(encoding="utf-8"))
    if obj.get("schema_version") != 1 or not isinstance(obj.get("rules"), list):
        raise ValueError("unsupported rule schema")
    if len(obj["rules"]) > 100:
        raise ValueError("too many rules")
    seen = set()
    rules = []
    for item in obj["rules"]:
        if not isinstance(item, dict):
            raise ValueError("rule must be an object")
        rid = item.get("id")
        pattern = item.get("pattern")
        extensions = item.get("extensions")
        if (not isinstance(rid, str) or not RULE_ID.fullmatch(rid) or
                rid in seen or item.get("severity") not in SEVERITIES or
                not isinstance(item.get("title"), str) or
                not isinstance(item.get("recommendation"), str) or
                not isinstance(pattern, str) or not 1 <= len(pattern) <= 240 or
                "\n" in pattern or not isinstance(extensions, list) or
                not extensions or len(extensions) > 25 or
                any(not isinstance(x, str) or not re.fullmatch(r"\.[a-z0-9]{1,7}", x)
                    for x in extensions)):
            raise ValueError("invalid or duplicate rule definition")
        seen.add(rid)
        rules.append({**item, "compiled": re.compile(pattern, re.IGNORECASE)})
    return rules


def scan(root, config, include_evidence=False):
    root = Path(root).resolve(strict=True)
    rules = load_rules(config)
    findings = []
    inspected = 0
    for path in project_files(root, include_evidence=include_evidence):
        inspected += 1
        rel = path.relative_to(root).as_posix()
        applicable = [r for r in rules if path.suffix.lower() in r["extensions"]]
        if not applicable:
            continue
        for number, line in enumerate(numbered_lines(path), 1):
            # A hard bound protects the tool from pathological minified files.
            clipped = line[:MAX_LINE_LENGTH]
            for rule in applicable:
                if rule["compiled"].search(clipped):
                    findings.append({
                        "rule_id": rule["id"],
                        "severity": rule["severity"],
                        "confidence": "heuristic",
                        "path": rel,
                        "line": number,
                        "title": rule["title"],
                        "recommendation": rule["recommendation"],
                    })
    findings.sort(key=lambda f: (f["path"], f["line"], f["rule_id"]))
    return {
        "schema_version": 1,
        "tool": "star-rule-engine",
        "static_read_only": True,
        "proven_vulnerabilities": 0,
        "files_scanned": inspected,
        "rules_loaded": len(rules),
        "findings": findings
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Star Cyber Audit read-only local rule engine")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--include-evidence", action="store_true",
                        help="explicitly include archived local research and reviews")
    parser.add_argument("--json", type=Path, help="save metadata-only report here")
    args = parser.parse_args(argv)
    try:
        report = scan(args.root, args.config or args.root / "config/security_rules.json",
                      args.include_evidence)
    except (OSError, ValueError, json.JSONDecodeError, re.error) as exc:
        parser.error(str(exc))
    if args.json:
        save_report(report, args.json)
    print("Rule engine: {} local files, {} rules, {} review indicators (not proven vulnerabilities).".format(
        report["files_scanned"], report["rules_loaded"], len(report["findings"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
