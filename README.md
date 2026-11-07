# Star Cyber Audit — iSH + Cloudflare

An **independent, read-only JavaScript static-auditing toolkit** for iSH (Alpine on iPhone), a-Shell, and Linux, with an Arabic web dashboard. It was created to inspect publicly available or locally owned JS sources, classify anti-bot HTML, and produce structured reports without executing target code.

[Open the live dashboard](https://star-cyber-audit-ish.abo330899.workers.dev/) · [Health check](https://star-cyber-audit-ish.abo330899.workers.dev/health)

> **Unofficial educational research.** Not affiliated with Iraqi UBOOR or a government authority. Indicators are not confirmed vulnerabilities. The dashboard does not authenticate to, probe, or proxy the government site.

## Quick start — iSH (iPhone)

```sh
apk add python3 ca-certificates
mkdir -p /mnt/star-audit
mount -t ios . /mnt/star-audit
cd /mnt/star-audit
sh run.sh
```

Choose the folder containing `run.sh` when the iOS Files picker opens. The executable analyzes local snapshots when present; source control deliberately excludes third-party snapshot files.

## Options

```sh
sh run.sh --local ./my-files  # Recursively scan local JS/MJS/CJS/HTML without executing them
sh run.sh --local ./research  # Scan archived sources locally; no network calls
sh run.sh --fetch             # GET four allowlisted static assets
sh run.sh --fetch-all         # GET twenty allowlisted static assets, lightly paced
```

No POST, login, token, document verification, or WAF bypass functionality is included. An HTML WAF challenge is recorded separately and never passed off as JavaScript.

## Reports

Locally generated `reports/` files:
- `analysis.json` — machine-readable file metadata, routes, imports, storage indicators and review flags
- `inventory.csv` — filename, classification, size and SHA-256
- `api_paths.txt` — file-to-API references, **not network calls**
- `review_flags.txt` — static heuristics for human inspection
- `report.html` — offline report
- `fetch_status.json` — summary of optional GET requests

The [web dashboard](https://star-cyber-audit-ish.abo330899.workers.dev/) loads a **sanitized historical sample** by default. Import `reports/analysis.json` through the browser to explore your own data locally; it is not uploaded to Cloudflare.

## Architecture

| Component | File | Purpose |
| --- | --- | --- |
| iSH runner | `run.sh` | POSIX shell launcher |
| Static analyzer | `analyze.py` | Python standard library only |
| Historical overview | `UBOOR_FLOW_NOTES_AR.md` | Known front-end flows, limitations |
| Public dashboard | `site/worker.js` | Standalone Cloudflare Worker |
| Sanitized sample | `site/sample-data.json` | No originals, tokens, or private records |

Cloudflare deployment **is live** on `star-cyber-audit-ish.abo330899.workers.dev`. A GitHub repository connection was created in Cloudflare Builds; automated trigger/CI deployment has **not** been enabled and is not implied by the one-time API deployment. The exact production Worker source is versioned in `site/worker.js`.

## Security and licensing boundaries

Do not commit locally captured HTTP requests, personal data, session cookies, access tokens, third-party JavaScript archives, or non-redacted reports. `.gitignore` excludes `offline_samples`, `downloads`, and `reports`. Sample metadata is historical and does not establish current backend behavior or document validity.

See [Arabic documentation](README_AR.md) and [GitHub notes](README_GITHUB_UPLOAD.md).

### Scanner maintenance

The analyzer recursively enumerates local JS/MJS/CJS/HTML, keeps relative paths to
avoid collisions, includes DMS `/api/verify/` references, and rejects HTML/WAF/JSON
before using file-extension hints. GitHub Actions tests local fixtures plus archived
source snapshots; it does **not** query external government systems in CI.

## QrLocalImporter deep review (8 November 2026)

Read the [Arabic evidence-based review](reviews/2026-11-08/QrLocalImporter_deep_review_AR.md), then run the new read-only iSH analyzer against **your own local source file**:

```sh
python3 tools/ish/qr_importer_review.py /path/to/QrLocalImporter-DYzNB5Fh.js
python3 -m unittest discover -s tests -p 'test_qr_importer_review.py' -v
```

The repository stores the SHA-256 and review findings, **not a new copy of the uploaded third-party script**. The review does not contact UBOOR APIs or establish backend vulnerabilities.

## useLocalCompany deep review (8 November 2026)

The [Arabic review](reviews/2026-11-08/useLocalCompany_deep_review_AR.md) documents the
company/item forms, client-side QR readings, server reading lists, document previews,
attachment downloads, and log-event API calls.

Run the additional **offline-only** checker on a local copy of the user-supplied source:

```sh
python3 tools/ish/use_local_company_review.py /path/to/useLocalCompany-DfV5kpAj.js
python3 -m unittest discover -s tests -p 'test_use_local_company_review.py' -v
```

Evidence: 16,940 bytes; SHA-256 `2a94cadad67e987ef5fcbce9d443f134bbce8293dea69d6e37220c195afa76f4`.
The repo does **not** add the third-party source file for this review. Nine source
indicators are **not** claims of nine exploitable vulnerabilities. No backend API is called.

## QrControlScan source review (8 November 2026)

[Arabic deep source review](reviews/2026-11-08/QrControlScan_deep_review_AR.md) joins the
QrControlScan Vue view to the previously reviewed useLocalCompany composable.
The UI itself does **not** issue direct government API calls. Its dependency
handles list, preview and export API actions. The report separates frontend
evidence and unknown backend authorization.

Run the local, offline checker against the two locally available files:

```sh
python3 tools/ish/qr_control_scan_review.py /path/to/QrControlScan-M6uGJnR1.js \
  --dependency /path/to/useLocalCompany-DfV5kpAj.js
python3 -m unittest discover -s tests -p 'test_qr_control_scan_review.py' -v
```

Evidence SHA-256: `0848ead8a6082769241885b6e5de6fd26aa783cbfce832f46448780378bbd78c`
(8,315 bytes). This update adds no copy of the third-party JS source, account
secrets, HTTP traffic, or document records.

## QRReadings deep comparison (8 November 2026)

The [Arabic deep comparison](reviews/2026-11-08/QRReadings_deep_comparison_AR.md)
covers the QRReadings view, `QrControlScan`, and `useLocalCompany`:
distinct list/export endpoints; a shared document-preview API; client-side demo
rows, session storage, console logging, and authorization UI. The work is
**read-only** and does not establish backend access or document validity.

Use the offline checker on locally held sources:

```sh
python3 tools/ish/qr_readings_offline_review.py /path/to/QRReadings-B-a3jcrk.js \
  --control /path/to/QrControlScan-M6uGJnR1.js \
  --composable /path/to/useLocalCompany-DfV5kpAj.js
python3 -m unittest discover -s tests -p 'test_qr_readings_offline_review.py' -v
```

Source snapshot: 14,489 bytes; SHA-256
`31c9ac2eadc4a256d0d321317431bcd7655e6eabb06a3d848c4b676e631f7cb9`.
This addition does not publish a new copy of third-party JS, session tokens,
user records, or government API responses.

## QRImported static deep review (8 November 2026)

[Read the Arabic report](reviews/2026-11-08/QRImported_deep_comparison_AR.md)
comparing this import-reader frontend with QRLocal and QrLocalImporter. The most
significant difference is **camera-image pixel coordinates** being placed in
`x_coordinate/y_coordinate` rather than browser GPS latitude and longitude.
Other static indicators cover bearer-token debug logging, duplicate POST
diagnostics, session defaults, RAF lifecycle, and local response persistence.

Run the offline static checker on **locally obtained source files**:

```sh
python3 tools/ish/qr_imported_review.py /path/to/QRImported-C65Oqm1K.js \
  --qr-local /path/to/QRLocal-5TAaXbzM.js \
  --exit-importer /path/to/QrLocalImporter-DYzNB5Fh.js
python3 -m unittest discover -s tests -p 'test_qr_imported_review.py' -v
```

The two comparison flags are optional. Snapshot SHA-256:
`d2756b08358ced044c8f9982d4da8b19ba9a38996fc7c4f682e0d67148d59eee`
(8,913 bytes). This repository update contains no new copy of third-party
government JavaScript, login token, document record, or live backend request.
Thirteen matched frontend patterns do **not** establish thirteen vulnerabilities.

## QRHealthCertificate deep review (8 November 2026)

The [Arabic evidence-based audit](reviews/2026-11-08/QRHealthCertificate_deep_review_AR.md)
examines the health-certificate camera reader and its
`POST BorderPort_HS/read_doc_health` flow. Its **client-side 48-hour
heuristic is conditional**: a substring match in the response message can
skip the check; otherwise the UI chooses the newest parseable date from
several unrelated fields, including license approval. This is **not a claim**
that the government backend permits an expired document.

Use the stdlib-only offline review tool on a locally held copy:

```sh
python3 tools/ish/qr_health_certificate_review.py /path/to/QRHealthCertificate-Byvh35hk.js \
  --qr-local /path/to/QRLocal-5TAaXbzM.js \
  --qr-imported /path/to/QRImported-C65Oqm1K.js
python3 -m unittest discover -s tests -p 'test_qr_health_certificate_review.py' -v
```

Comparisons are optional. Snapshot: 10,900 bytes, SHA-256:
`78b26ef2ba7f02c92745bc9bc5e61731d4972a390ba3c866d62ae8e000788936`.
There are 16 version-specific source indicators (not proven vulnerabilities).
No third-party script, secrets, personal records, or live UBOOR API responses
were added as part of this report.

## useHealthCertificate deep static review (8 November 2026)

The [Arabic audit](reviews/2026-11-08/useHealthCertificate_deep_review_AR.md)
analyzes the certificate management composable: 12 relative BorderPort_HS
API routes, shared singleton state, province/district/subdistrict lookup caches,
reader lists, document previews, downloads and uploads. Its 13 version-specific
patterns are **frontend review indicators**, not confirmed server vulnerabilities.
Unlike the QRHealthCertificate scanner, this module has **no** local 48-hour
expiry test or camera reader.

```sh
python3 tools/ish/use_health_certificate_review.py /path/to/useHealthCertificate-DVL2cDcP.js
python3 -m unittest discover -s tests -p 'test_use_health_certificate_review.py' -v
```

Source snapshot SHA-256:
`36acf66c8a1ad736f6da9bca1d8a9dced9f1bf377451c8913dcf4ddc15eff479`
(17,870 bytes). The update adds **no new copy** of third-party JS,
secrets, personal documents or authenticated API response data.

## DisableDocument static audit (8 November 2026)

The [Arabic evidence-based deep review](reviews/2026-11-08/DisableDocument_deep_review_AR.md)
covers the QR camera's `POST local_form/reset_company_qrcode` flow. Key issues
include an **optimistic success card** shown before the server confirms a reset,
an `expired:true` state not respected by the success condition, a diagnostic
second POST in the error handler, shared token debug logging, and location
freshness. No government backend was contacted or changed.

A second provided `QRHealthCertificate-Byvh35hk 2.js` file was **byte-identical**
to the earlier health scanner file (SHA-256:
`78b26ef2ba7f02c92745bc9bc5e61731d4972a390ba3c866d62ae8e000788936`).

```sh
python3 tools/ish/disable_document_review.py /path/to/DisableDocument-AXBjrkYS.js \
  --health "/path/to/QRHealthCertificate-Byvh35hk 2.js"
python3 -m unittest discover -s tests -p 'test_disable_document_review.py' -v
```

DisableDocument evidence: 11,505 bytes; SHA-256
`e8f574544e0f910f8ec66446810627a13352065d7b6ae2a3b1a89c0439f60e01`.
Seventeen version-specific frontend patterns are review flags, **not**
confirmed exploitable vulnerabilities. The public repository update does not
include a new copy of third-party source, session credentials, or government
document data.
