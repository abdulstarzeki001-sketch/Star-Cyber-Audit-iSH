#!/bin/sh
# Star Cyber Audit — offline Phase 1 checks on iSH / a-Shell / Linux.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
command -v python3 >/dev/null 2>&1 || {
  echo "Install Python 3 first (iSH: apk add python3)." >&2
  exit 127
}

COMMAND=${1:-scan}
case "$COMMAND" in
  scan)
    mkdir -p reports
    python3 -m tools.security.rule_engine --root . --json reports/security_rules.json
    python3 -m tools.security.secret_scan --root . --json reports/secret_scan.json --fail-on-secrets
    printf '%s\n' "Offline reports: reports/security_rules.json and reports/secret_scan.json"
    ;;
  compare)
    if [ "$#" -ne 3 ]; then
      echo "Usage: sh tools/ish/phase1_security.sh compare BEFORE.json AFTER.json" >&2
      exit 2
    fi
    mkdir -p reports
    python3 -m tools.security.compare_reports \
      --before "$2" --after "$3" \
      --json reports/change_comparison.json \
      --markdown reports/change_comparison.md
    ;;
  test)
    python3 -m py_compile analyze.py tools/security/*.py
    python3 -m unittest discover -s tests -v
    ;;
  *)
    echo "Usage: sh tools/ish/phase1_security.sh [scan|test|compare BEFORE.json AFTER.json]" >&2
    exit 2
    ;;
esac
