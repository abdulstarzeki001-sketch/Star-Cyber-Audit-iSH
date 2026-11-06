# Star Cyber Audit — مراجعة الدفعة المرفوعة

**تاريخ المراجعة:** 7 نوفمبر 2026

## ما فُحص

أُجري تحليل ساكن لـ **6 ملفات JavaScript** أرفقها المستخدم مع **4 تقارير تحليل سابقة**. لم يتم تنفيذ JavaScript أو استدعاء API المصادق أو اختبار تطبيق حي أو تجاوز WAF.

**ملخص هذه الدفعة وحدها:** 6 ملفات أصلية؛ 8 مسارات API نصية متميزة؛ 20 مؤشر مراجعة (ليست ثغرات مؤكدة). هذه الأرقام تختلف عن جرد iSH التاريخي المكون من 10 ملفات و33 مسارًا.

## جرد البصمات

| الملف | البايت | SHA-256 |
|---|---:|---|
| `QRDocument-BJwpoEJY.js` | 607716 | `23f8c5d87b6a91511af2a96f57075e8502861bd2f6d92d914a14222db4199400` |
| `qrStore-B8bgApfd.js` | 248 | `122527b8507637168eeb4365f879f160f02620d1dc997c74e3da1880a1573e77` |
| `AchievementDocument-DEzIzJ3I.js` | 11641 | `bec1dbe0a25694f05f30d5dcf6edb253fb2f9276d9e00b583ba416aabc941d7c` |
| `useExitGate-BvHNutwH.js` | 6027 | `9d9a109e58d619a8afdf91bfcbd9f7e45377ddb8236e82e13597b896e56c3306` |
| `QrCodeReaderCustoms-a-UBVR7y.js` | 16490 | `09b62507255c25910a196ca0ca1e5fb6d961be5d10287face07cc777aaf45c0b` |
| `QRLocal-5TAaXbzM.js` | 10014 | `1e3ea9982971b4e4e08bb2ebee1520fe6a5056bc8590de4288fec80456fa9626` |

## مسارات API التي تظهر في هذه الملفات مباشرة

- `BorderPort_HS/path-document-file`
- `BorderPort_HS/return_doc_hc_by_docnumber`
- `local_form/read_doc_company`
- `local_form/refuse_doc_company`
- `support_org/download_qrcode_readers_import`
- `support_org/paginate_qrcode_reader_import`
- `support_org/read_qr_exitgate`
- `support_org/return_doc_qrcode_export`

## تدفق الواجهة المثبت

- `QRLocal` يقرأ QR ويرسل `url` مع الإحداثيات إلى `local_form/read_doc_company`، ثم يحفظ معاينة متصفح.
- `qrStore` يخزن `qr_readings` في `localStorage` دون توقيع أو تحقق رسمي للوثائق.
- `QRDocument` يقرأ المعاينة ويعرض السيطرات ويحتوي طلب رفض ورفع لقطة PNG في وضع `auto_send`.
- `useExitGate` يدير قراءة بوابة الخروج واسترجاع مستند الناقل وسجل القراءات وتنزيل Excel.
- `QrCodeReaderCustoms` يوفر البحث والتنزيل والانتقال إلى تفاصيل المستند.
- `AchievementDocument` يعرض استمارة الناقل ويولد صورة QR بصريًا ويطبع A4.

## النتائج التي تستحق الإصلاح

- **QRDocument-BJwpoEJY.js**: PERSISTENT_BROWSER_STORAGE: preview reads qr_readings and falls back to x[0] for unmatched ID
- **QRDocument-BJwpoEJY.js**: DOCUMENT_REFUSAL_UI: client privilege is not proof of backend authorization
- **QRDocument-BJwpoEJY.js**: AUTO_SEND_PNG: DOM screenshot can be sent to BorderPort_HS/path-document-file
- **qrStore-B8bgApfd.js**: PERSISTENT_BROWSER_STORAGE: shared qr_readings key lacks per-account scope
- **qrStore-B8bgApfd.js**: SCHEMA_GAP: JSON.parse value is not checked with Array.isArray before unshift
- **qrStore-B8bgApfd.js**: SILENT_WRITE_FAILURE: setItem exceptions are swallowed; history unbounded
- **AchievementDocument-DEzIzJ3I.js**: LOCAL_QR_FALLBACK: qr_code || doc_id || doc_number used to render QR image
- **AchievementDocument-DEzIzJ3I.js**: THIRD_PARTY_QR_SERVICE: generator catch sets a QuickChart URL with the QR value
- **AchievementDocument-DEzIzJ3I.js**: DOCUMENT_ID_MISMATCH: fallback view can use shared data without ID matching
- **AchievementDocument-DEzIzJ3I.js**: PRINT_CLIPPING: fixed A4 296mm page and overflow hidden
- **useExitGate-BvHNutwH.js**: HTTP_STATUS_ONLY: gate scan checks HTTP 200 but not success:false JSON field
- **useExitGate-BvHNutwH.js**: DOC_NUMBER_MAPPING: list filters map doc_number to doc_id
- **useExitGate-BvHNutwH.js**: PERSISTENT_BROWSER_STORAGE: detail fetches can append previews to qrStore
- **QrCodeReaderCustoms-a-UBVR7y.js**: ROLE_UI_ONLY: Excel button checks download_health_qrcode_readers, server not evaluated
- **QrCodeReaderCustoms-a-UBVR7y.js**: DOC_NUMBER_MAPPING: selected row navigates with doc_number
- **QRLocal-5TAaXbzM.js**: POSSIBLE_TOKEN_DEBUG_LOG: console.debug includes y.token
- **QRLocal-5TAaXbzM.js**: REVIEW_POST_RETRY: catch block issues a second diagnostic POST via fetch
- **QRLocal-5TAaXbzM.js**: MESSAGE_REGEX: Arabic text regex can match negative messages containing تم
- **QRLocal-5TAaXbzM.js**: CLIENT_EXPIRY_HEURISTIC: 48-hour window is UI-only and not official validity proof
- **QRLocal-5TAaXbzM.js**: GEOLOCATION_OPTIONAL: blank coordinates may be submitted

## حدود الاستنتاج

لا تثبت هذه الأصول البرمجية وجود ضعف خادمي في إصدار الوثائق أو توقيع QR أو صلاحيات الموافقة والرفض. ملفات `index-gleMzSil.js` و`QRCheckpoints` ليست من ضمن الأصول الستة المرفوعة هنا؛ الملاحظات المتعلقة بها تبقى من التقارير التاريخية فقط.

## الخصوصية

المستودع عام؛ لم تُنشر ملفات JavaScript الحكومية الأصلية أو ملفات شبكة فيها Tokens أو Cookies. نُشرت بصمات ونتائج التحليل والتقارير المرفقة فقط. هذه أداة مستقلة وغير رسمية.
