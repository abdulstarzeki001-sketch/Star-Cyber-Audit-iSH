# Star Cyber Audit V2 — Cloudflare Dashboard

## Overview
Separate Cloudflare Worker preview for the offline security foundation. It does not overwrite the existing star-cyber-audit-ish Worker.

Four supported local report formats:
- reports/analysis.json — read-only source analysis
- reports/security_rules.json — heuristic rule engine
- reports/secret_scan.json — secret candidates (no secret values)
- reports/change_comparison.json — offline source snapshot comparisons

## Privacy
The dashboard parses selected JSON files in the browser using File.text and JSON.parse. There are no browser network requests to upload file data. Strict Content Security Policy uses first-party script/style assets and connect-src none. UI renders untrusted data through textContent, not innerHTML.

No credentials, OpenAI keys, or government API calls are included. Files are held in page memory only; exporting creates a metadata-only summary. Sample data is clearly marked as demonstration, not verified findings.

## Test commands
Run with Node 22 or newer:

    node --check site/worker-v2.mjs
    node tests/worker_v2.test.mjs

GitHub Actions also runs these tests on pull requests.

## Deployment
Publish this isolated module Worker as star-cyber-audit-v2 in the existing abo330899 Cloudflare Workers account only after tests pass. Preserve the earlier star-cyber-audit-ish production Worker.

The actual workers.dev URL must be confirmed from Cloudflare and health-checked after deployment. A GitHub push alone does not deploy this new Worker.

## Limits
Browser imports: 8 JSON files maximum and 8 MB per file. Display lists are capped for phone performance. The dashboard is not a penetration testing engine, a live QR verifier, or evidence of exploitable backend vulnerabilities. Review static indicators manually.
