# UBOOR — Verified qrStore Module Addendum

**Date:** 2026-11-06  
**Exact source URL:** https://customs-uboor.ur.gov.iq/assets/qrStore-B8bgApfd.js  
**Collection:** public HTTP GET, confirmed HTTP 200 and `application/javascript` from live page fetch.  
**Scope:** exact `qrStore-B8bgApfd.js` body plus locally retained frontend bundles named in the source review. No backend code or authenticated API access was assessed.

## 1. Exact source (formatted only)

```js
const e = "qr_readings";
function n() {
  try {
    const t = localStorage.getItem(e);
    return t ? JSON.parse(t) : [];
  } catch {
    return [];
  }
}
function r(t) {
  try {
    localStorage.setItem(e, JSON.stringify(t));
  } catch {}
}
function s(t) {
  const a = n();
  a.unshift(t);
  r(a);
}
export { s as a, n as l };
```

**Export `a`:** add a record to the beginning of the array. **Export `l`:** read the array from `localStorage`. The module has no other exports or direct network requests.

## 2. Observed call sites in the saved frontend bundles

| Bundle | Import/function | Proven action |
|---|---|---|
| `QRLocal-5TAaXbzM.js` | `a as fe` | After a successful `local_form/read_doc_company` request, adds `{id:Date.now(), type:'محلي', value:url, date, raw:{url}, response:serverData, x:latitude, y:longitude, auto_send:!!serverData.is_main}`, then attempts to navigate to `QRDocument`. |
| `QRDocument-BJwpoEJY.js` | `l as CB` | Resolves preview IDs from local QR history. On success of its optional auto-upload process, reads and rewrites the key directly to remove `auto_send` on the matching ID. |
| `useExitGate-BvHNutwH.js` | `a as L` | `fetchCertificateReaderDetail` adds certificate previews after `BorderPort_HS/return_doc_hc_by_docnumber`; `fetchAchievementDocDetail` adds achievement previews after `support_org/return_doc_qrcode_export`. |
| `AchievementDocument-DEzIzJ3I.js` | Indirect through `useExitGate` | Uses `fetchAchievementDocDetail` for query-based fetching; this does not itself cryptographically validate a QR. |

**Important distinction:** the `searchImportedGoods` flow in `useExitGate` invokes `support_org/read_qr_exitgate` and sets shared reactive document data; this particular function does **not** call the `qrStore` append function. It is incorrect to claim every gate scan necessarily writes to `qr_readings`.

## 3. Verified findings, severity and evidence limits

1. **Persisting history across the audited logouts (privacy, medium–high where shared devices exist).** `qrStore` has no user identifier in its key, no per-user scope, no delete/clear function, and uses persistent `localStorage`. In the examined `index-gleMzSil.js` logout code, employee logout removes `auth` while company-owner logout removes its dedicated auth keys; neither removes `qr_readings`. Another unreviewed module or a manual browser cleanup could still clear it. This is evidence about the audited code, not a claim about all possible server or browser behavior.
2. **Potentially sensitive information at rest (privacy, contextual).** QRLocal saves full QR URL, backend response object and GPS coordinates. Whether a given backend response actually carries sensitive information requires examining the response. Browser local storage is not server storage and is not intrinsically encrypted by this module.
3. **Malformed valid JSON can abort insertion (reliability, high for the affected client).** JSON decoding accepts objects, strings, `null`, or other values. `s(record)` immediately invokes `.unshift` on the decoded value, without checking `Array.isArray`. This raises a JavaScript error if storage is not an array; `QRLocal` has a surrounding catch that can then prevent the expected preview navigation.
4. **Invalid JSON is silently treated as empty (integrity, medium).** `n()` catches parse errors and returns `[]`; the next successful write replaces the corrupt value, with no recovery or user warning.
5. **Failed localStorage write is silently ignored (reliability, medium).** `r(t)` discards `setItem` exceptions such as storage quotas or access restrictions and `s(t)` does not report success/failure. Consequently UI navigation may continue without a stored preview.
6. **No retention policy, caps, deduplication or schema validation (reliability/privacy, medium).** Every call to `s(t)` prepends another record; the array grows without automatic trimming, time-based expiration or duplicate checks.
7. **Not proof of official document validity (integrity, important boundary).** The module never calls a government validation API and does not sign, decrypt or validate records. It stores client-side data. `Date.now()` IDs are client-generated and do not constitute authoritative `doc_id` values.
8. **Local display must not be trusted as server-origin truth.** `QRDocument` can read and render `qr_readings` entries. Client-side storage is mutable by local scripts. No claim is made that this defeats backend authorization, or that the server accepts altered records.
9. **`auto_send` is a frontend work flag, not an official issuance flag.** Under certain conditions, `QRDocument` uses it to create a screenshot file and submit `POST BorderPort_HS/path-document-file`; after success, it removes the flag from the local record. Only actual backend logs can establish acceptance/validation of the submission.

## 4. Recommended corrections

- Keep the authoritative history on the server, keyed by authenticated account and session, if regulatory traceability is required.
- Restrict browser history to the minimum required fields; avoid full `response` objects, GPS coordinates and sensitive QR payloads unless strictly necessary.
- Use scoped keys per user or clear local history during a verified logout; define lifecycle requirements explicitly.
- Reject non-arrays and malformed entries; validate record schema and guard `unshift`.
- Bound list length and expiration; handle quota errors explicitly and show the user a save failure instead of swallowing it.
- Use stable unique IDs that cannot collide, with exact match checks in previews. Never fall back to an unrelated record.
- Verify official document numbers/status/signatures on the server; do not treat local flags, screenshots or QR images as evidence of authenticity.
- Prevent duplicate POST requests during error handling; avoid logging access tokens and full QR records in production.

## 5. What remains unverified

- Server-side QR signature and data authenticity checks.
- Official document expiry rules, revocation and any valid official `doc_id` mapping.
- Whether backend logs are retained and audited independent of local storage.
- User role separation, server-side enforcement and data lifecycle beyond the examined frontend chunks.

**Bottom line:** This module is a tiny browser-side history utility, not a QR decoder, certificate issuer, cryptographic validator, or official database. The most important verified risks are cross-session data persistence on shared browser profiles, weak storage reliability and the temptation to treat a mutable cached preview as official status.