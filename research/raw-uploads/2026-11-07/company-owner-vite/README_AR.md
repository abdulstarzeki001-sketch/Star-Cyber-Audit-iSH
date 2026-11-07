# CompanyOwnerView — frontend source snapshots

**Collection date:** 2026-11-07  
**Purpose:** archival static analysis of the uploaded Vite/Vue build fragments.  
**Status:** sources preserved as read-only evidence; **not** a complete application or official verification service.

## Uploaded source files

| File | Size (bytes) | Function |
|---|---:|---|
| `companyownerview-cjdszkn6.js` | 38,636 | CompanyOwnerView component; includes layout, ShipmentDoc rendering and browser print logic |
| `input-banvtf9h.js` | 7,831 | Reusable Input component |
| `badge-ddrqdsta.js` | 5,460 | Reusable Badge component |
| `iraqeagle-bf406bbv(20261107-015549).js` | 74 | Imports asset URLs for image logos |
| `companyownerview-citq539c(20261107-015549).css` | 3,693 | CompanyOwner and document scoped styles |
| `index-dxnlxmd6.css` | 217,017 | Base Tailwind/layout style bundle |
| `basemodal-drrlsycw(20261107-015549).css` | 5,451 | Modal component styles |
| `vue3-treeselect-bzqe87yr(20261107-015549).css` | 24,215 | Tree-select component styles |

All eight files were checked after upload to GitHub; the repository lists sizes matching the original source byte sizes.

## Two Cairo font assets intentionally excluded from the public repository

- `cairo-bold-cfhkse12(20261107-015549).ttf`
- `cairo-regular-cb0nqka_(20261107-015549).ttf`

These font files were received separately but not redistributed. The base stylesheet references Cairo filenames; verify the applicable font license and provide authorized local copies if reproducing the styles.

## Static findings from the component

1. `CompanyOwnerView` imports the missing `index-CcmHdHtN.js` build, plus other dependencies such as `Card-CXdTeCyO.js`, `Textarea-Bgo3bJB3.js`, `Table-DtmqfnP9.js`, and `Form-lDZOexkp.js`. These are **not part of this upload**, so the eight files cannot be launched as a standalone app.
2. The bundled `ShipmentDoc` displays QR imagery from `doc.qr_code || doc.response.qr_code` and can generate a QuickChart image URL from a `robot?url=` payload. If a QR is absent or otherwise not recognized, it may fall back to information such as a license approval number, vehicle number, or driver name to form a QR image.
3. An image rendered by a browser QR library or by QuickChart is **not proof** of a signed or valid government document. Loading a third-party image URL may disclose its embedded QR text to the service provider.
4. The logo module includes `/images/Customs.jpg` and `/images/iraqEagle.png`; the original image bytes were not included. CSS or print layout may differ without dependencies and images.
5. `ShipmentDoc` uses a fixed A4 print template in the compiled component; manually check long data lists for clipping. This is a presentation observation, not proof of a PDF server signing method.

## Security / publishing limits

- No backend source, credentialed requests, live API tests, document issuance or official QR signature verification were performed.
- No hard-coded session cookies, long QR query tokens or static Bearer token values were found in these eight text assets during initial inspection. This is not a guarantee that the original system has no sensitive data.
- The repository is public; the fragments should **not** be served as a standalone government replica.
- The deployed Star Cyber Audit dashboard is unchanged by this source archival upload.

Source research only; not affiliated with or endorsed by any government authority.
