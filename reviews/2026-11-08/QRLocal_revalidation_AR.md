# QRLocal-5TAaXbzM(3).js — تأكيد النسخة والربط مع CompanyOwnerView

**التاريخ:** 8 نوفمبر 2026.  
**الحجم:** 10,014 بايت.  
**SHA-256:** `1e3ea9982971b4e4e08bb2ebee1520fe6a5056bc8590de4288fec80456fa9626`.  
**Git Blob SHA-1:** `b36aa6e06c9fdc421f47bb4c59434b5989b59894`.

الملف **مطابق بايتًا ببايت** للنسخة `research/source-archive/2026-11-07/uboor/QRLocal-5TAaXbzM.js` المؤرشفة سابقًا. لم ننشر نسخة إضافية من الشيفرة الحكومية. لم تُنفذ شيفرة JavaScript أو أية طلبات إلى خادم عبور.

## 1. مسار عمل القارئ المحلي

```text
Camera -> BarcodeDetector or jsQR
   -> QR raw text
   -> GPS via composable or navigator.geolocation
   -> normalizes non-http QR text to /robot?url=...
   -> POST /api/local_form/read_doc_company with {url, x_coordinate, y_coordinate}
   -> checks response and a conditional 48-hour local expiry heuristic
   -> qrStore.a({id:Date.now(), type:"محلي", response, auto_send:!!a.is_main})
   -> QRDocument?id=<local_id>
   -> QRDocument may upload local_document.png when auto_send is true
```

هذه الإحداثيات مأخوذة من GPS، **وليست** موضع الباركود داخل إطار الكاميرا كما يحدث في `QRImported-C65Oqm1K.js`.

## 2. ما لم يتغير في النسخة الجديدة

- يستخدم `read_doc_company` ويرسل Bearer من توكن جلسة المستخدم.
- يسجل `auth token` وبيانات POST في Console (ينبغي حذف التوكن من سجلات الإنتاج).
- يفحص التاريخ من `date_str` أو `date` أو `created_at` أو `license_approval_date` ويطبق حد `2880*60*1000` = 48 ساعة، **فقط عندما لا تشير رسالة `message` إلى النجاح**؛ ليست هذه آلية رسمية لإثبات انتهاء الصلاحية.
- عند استثناء Axios ينفذ طلب `fetch` تشخيصيًا ثانيًا بطريقة POST إلى المسار نفسه، حتى إن كان الاستثناء بسبب استجابة فشل منطقي/خادمي؛ قد تتكرر عملية ذات أثر جانبي. لا تختبر هذا المسار على الإنتاج دون تصريح.
- يقبل GPS إذا كانت القيم truthy ومنتهية، ما يستبعد الصفر الرقمي؛ إذا فشل الحصول على GPS قد يبقى الحقل فارغًا ويستمر إرسال الطلب.
- ينقل `is_main` من استجابة المستوى الأعلى إلى البيانات عندما يظهر في ذلك المستوى، ثم يضبط `auto_send:!!a.is_main`، وبذلك قد يبدأ رفع صورة الوثيقة بمجرد دخول `QRDocument`.
- يخزن معرف عرض محليًا من `Date.now()`، وهو **ليس** `doc_id` صادرا عن الخادم.

## 3. المقارنة مع CompanyOwnerView

| المقارنة | QRLocal | CompanyOwnerItems |
|---|---|---|
| الوظيفة | مسح QR وقراءة وثيقة | تقديم طلب شحن وتخفيض كميات |
| API | POST `read_doc_company` | PUT `company_item_reduce` |
| إدخال الموقع | GPS أثناء المسح | GPS أثناء ملء الشحنة |
| مخزن النتيجة | `localStorage["qr_readings"]` عبر qrStore | حالة Vue ونافذة `ShipmentDoc` |
| عرض الوثيقة | `QRDocument` | `ShipmentDoc` |
| شرط رفع الصورة | `auto_send` عند `is_main` | لا يظهر طلب رفع صورة مباشر في `CompanyOwnerItems` |

لا يثبت وجود حقول متشابهة أن المسارين يستخدمان جدول بيانات واحدًا أو صلاحية الخادم نفسها.

## 4. اختبارات وملاحظة أمنية

استُخدم `tools/ish/company_owner_review.py` لتعريف 10 مؤشرات `CL-01..CL-10` لربط مسار `QRLocal` بالتحليل الجديد. الاختبارات الاصطناعية في `tests/test_company_owner_review.py` لا تنفذ أي مسح حي أو إرسال طلب إلى خادم.

لا تثبت النتائج تجاوز صلاحيات حكومة العراق أو تغيير حالة مستند. أي اختبار لتفويض الخادم يجب أن يكون في نظام مملوك ومصرح به، وببيانات اصطناعية.

**الخطوة التالية المفيدة:** دراسة `ShipmentDoc-Dx885_fz.js` لفهم مسار عرض مستند الشحنة المؤقت دون الاعتماد على مظهر المستند كدليل أصالة.
