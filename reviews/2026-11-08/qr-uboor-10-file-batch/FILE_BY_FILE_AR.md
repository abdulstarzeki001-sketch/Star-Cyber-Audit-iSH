# تحليل دفعة 10 ملفات UBOOR — ملفًا ملفًا وربط المخرجات

**تاريخ الفحص:** 8 نوفمبر 2026  
**الطريقة:** قراءة كاملة للملفات المرفوعة في هذه الدفعة، حساب SHA-256 وGit Blob SHA-1، مطابقة تقارير المراجعات السابقة، استخراج المسارات النصية، تحليل `ShipmentDoc` بدقة جديدة. لا تشغيل JavaScript ولا استدعاءات إلى خوادم الحكومة أو بيانات أشخاص فعلية.  
**سجل البصمات:** [manifest.json](manifest.json)  
**سياسة الأرشفة:** 9 ملفات تطابق شيفرة سبق تحليلها؛ لا نرفع نسخًا متكررة من source تابع لجهات أخرى إلى المستودع العام. الملف العاشر يوثَّق تقريرًا وفاحصًا واختبارات، وليس نسخة JS إضافية.

## 1. `QRLocal-5TAaXbzM(5).js` — قارئ المنتج المحلي

**10,014 بايت** | SHA-256: `1e3ea9982971b4e4e08bb2ebee1520fe6a5056bc8590de4288fec80456fa9626` | **مطابق للمؤرشف**.

- الكاميرا: `getUserMedia` و`BarcodeDetector` و`jsQR` احتياطيًا.
- يحاول أخذ إحداثيات GPS من الحالة المشتركة أو `navigator.geolocation`. الإحداثيات لا تمثل موقع QR في الصورة.
- يطبّع نص QR غير المبدوء بـ`http` إلى `https://customs-uboor.ur.gov.iq/robot?url=...` مع ترميز الحمولة.
- يرسل `POST local_form/read_doc_company` بجسم `{url,x_coordinate,y_coordinate}` وترويسة Bearer. عند النجاح يحفظ سجلًا في `qrStore` مع `auto_send:!!response.is_main` ثم ينتقل إلى `QRDocument`.
- **المراجعة الأمنية:** يطبع التوكن في Console، وقد يرسل POST تشخيصيًا ثانيًا عند خطأ، ويمرر فحص 48 ساعة في بعض الاستجابات بناءً على كلمات نجاح نصية. لا يوجد فك حكومي مشفر في هذا المكوّن.

المراجعة السابقة: [QRLocal_revalidation_AR.md](../QRLocal_revalidation_AR.md).

## 2. `QRReadings-B-a3jcrk(1).js` — شاشة سجل القراءة

**14,489 بايت** | SHA-256: `31c9ac2eadc4a256d0d321317431bcd7655e6eabb06a3d848c4b676e631f7cb9` | **مطابق للمراجع سابقًا**.

- مكوّن `QRReadings` يعرض جداول قراءات الوثائق، بحثًا وصفحات ونطاق تواريخ وصلاحيات أزرار.
- خلافًا لبعض شاشات السجلات الأخرى، يُصدر استدعاءات API مباشرة: `POST local_form/pagination_qrcode_reader` و`POST local_form/download_qrcode_readers` و`POST local_form/return_doc_qrcode` للمعاينة.
- عند استرجاع تفاصيل الوثيقة قد يصنع مدخل معاينة بمعرّف `Date.now()`، وهو معرّف محلي غير مساوٍ لرقم وثيقة رسمي.
- **المراجعة الأمنية:** طبقة صلاحيات الأزرار لا تثبت تحقق الخادم؛ معاينة الرد المحلي يجب أن تتطابق مع رقم الوثيقة المطلوب. بعض سجلات debug قد تتضمن كامل ردّ الوثيقة.

المراجعة السابقة: [QRReadings_deep_comparison_AR.md](../QRReadings_deep_comparison_AR.md).

## 3. `QRImported-C65Oqm1K(1).js` — قارئ QR للمستورد

**8,913 بايت** | SHA-256: `d2756b08358ced044c8f9982d4da8b19ba9a38996fc7c4f682e0d67148d59eee` | **مطابق للمراجع سابقًا**.

- الكاميرا و`BarcodeDetector` مع `jsQR` مثل قارئ المحلي.
- في هذا المكوّن يمكن استخراج `x_coordinate` و`y_coordinate` من **مركز الرمز ضمن صورة الفيديو**، لا GPS؛ يجب عدم الخلط بين النوعين.
- يستخدم أيضًا `POST local_form/read_doc_company`، ويحفظ المعاينة ثم ينتقل إلى `QRDocument`.
- **المراجعة الأمنية:** طباعة توكن المصادقة وطلب POST تشخيصي ثانٍ عند الخطأ. وجود نفس endpoint لا يعني أن دلالة الإحداثيات أو قواعد المنتج المحلي والمستورد متطابقة.

المراجعة السابقة: [QRImported_deep_comparison_AR.md](../QRImported_deep_comparison_AR.md).

## 4. `useExitGate-BvHNutwH(3).js` — إدارة بوابة الخروج

**6,027 بايت** | SHA-256: `9d9a109e58d619a8afdf91bfcbd9f7e45377ddb8236e82e13597b896e56c3306` | **مطابق للمؤرشف**.

- وحدة composable/store وليست شاشة كاميرا ولا قالب PDF.
- تتضمن `POST support_org/read_qr_exitgate` لإرسال قراءة المستورد، و`support_org/paginate_qrcode_reader_import` للقائمة، و`support_org/download_qrcode_readers_import` للتصدير، و`support_org/return_doc_qrcode_export` للاسترجاع، و`BorderPort_HS/return_doc_hc_by_docnumber` لتفاصيل شهادة.
- `searchImportedGoods` تتأكد من وجود الموقع في الواجهة، وتعدّ HTTP 200 نجاحًا للانتقال إلى `AchievementDocument`. الوظيفة نفسها لا تضيف سجلًا إلى `qrStore`؛ بعض دوال استرجاع التفاصيل الأخرى تضيف مدخل معاينة.
- **المراجعة:** يجب فصل نجاح HTTP عن معنى قبول الوثيقة، وتجنب الخلط بين السجل المحلي والحدث الخادمي.

مرجع سابق: [UBOOR_verified_update](../../2026-11-07/reference/UBOOR_verified_update_2026-11-06.md).

## 5. `QrLocalImporter-DYzNB5Fh(1).js` — قارئ الاستيراد عند الخروج

**7,222 بايت** | SHA-256: `59ff26bfbc4b731799101527e9604fc736c170e80e4988eb69be672990cf8208` | **مطابق للمراجع سابقًا**.

- يفتح الكاميرا ويكتشف QR عبر `BarcodeDetector` أو `jsQR` احتياطيًا.
- يحاول تحديد الموقع بواسطة GPS، ثم يسلم قيمة القراءة إلى `searchImportedGoods` من `useExitGate`.
- **لا يضم بنفسه** النص المباشر لـ`support_org/read_qr_exitgate`؛ يظهر هذا المسار في الملف الذي يستورده. عدم العثور على المسار في الماسح وحده ليس دليلًا على عدم وجود طلب.
- **المراجعة:** خطأ أو تكرار القراءة وحالات غياب الموقع، مع الانتباه إلى أن نجاح انتقال الصفحة لا يثبت أن المستند أصبح معتمدًا رسميًا.

المراجعة السابقة: [QrLocalImporter_deep_review_AR.md](../QrLocalImporter_deep_review_AR.md).

## 6. `useLocalCompany-DfV5kpAj(1).js` — وظائف الشركة المحلية

**16,940 بايت** | SHA-256: `2a94cadad67e987ef5fcbce9d443f134bbce8293dea69d6e37220c195afa76f4` | **مطابق للمراجع سابقًا**.

- وحدة وظائف متعددة لإدارة بيانات الشركات والمواد والملفات ومتابعة القراءات.
- تُظهر نصوص مسارات مثل `local_form/iraqi_company_create` و`iraqi_company_edit/` و`company_item_create/` و`company_item_edit/`، إضافة إلى تنزيل الملفات.
- تحتوي دالة السجل التي تستخدم `POST local_form/paginate_qrcode_reader2`، والمعاينة عبر `POST local_form/return_doc_qrcode`، والتصدير عبر `download_qrcode_readers`.
- **مهم:** توجد بيانات `QRCODE:...` تجريبية في حالة معينة عندما يغيب السجل المحلي؛ وجود صف في `localStorage` لا يجعله سجل قراءة حكوميًا.
- **المراجعة:** تجنّب بيانات fallback غير المميزة في الواجهة، واربط المعاينات بمستند ورقم صحيح، ولا تطبع الرد الحساس كاملًا.

المراجعة السابقة: [useLocalCompany_deep_review_AR.md](../useLocalCompany_deep_review_AR.md).

## 7. `qrStore-B8bgApfd(2).js` — التاريخ المحلي الصغير

**248 بايت** | SHA-256: `122527b8507637168eeb4365f879f160f02620d1dc997c74e3da1880a1573e77` | **مطابق للمؤرشف**.

- يعرّف مفتاح `localStorage["qr_readings"]`.
- دالة القراءة تعيد `JSON.parse` أو `[]` عند الخطأ.
- دالة الإضافة تستدعي `array.unshift(record)` ثم تحفظ المصفوفة.
- **المراجعة:** لا يتحقق من `Array.isArray`؛ لا TTL ولا حد للسجلات أو فصل المستخدمين، وبعض أخطاء الحفظ تُخفى. لا يوجد API ولا توقيع ولا فك تشفير في هذا الملف.

المراجعة السابقة: [qrStore_deep_review_AR.md](../qrStore_deep_review_AR.md).

## 8. `RejectedLocalDocuments-CC07EpF_(1).js` — شاشة الوثائق المرفوضة

**11,186 بايت** | SHA-256: `b98b04782e1ee00c7e338bd111e22a45479db6e5171e5a67e808a3458a9c7a25` | **مطابق للمراجع سابقًا**.

- جدول بالوثائق المرفوضة المحلية: موظف القراءة، الجهة، الهاتف، تاريخ/وقت القراءة، النوع، الموقع، السبب، ورقم الوثيقة.
- جلب السجل يتم عبر `fetchRejectedLocalReaders` من store في الحزمة الرئيسية؛ اسم الـendpoint لا يظهر مباشرة في هذا الملف.
- الطلب المباشر المثبت هو `POST local_form/return_doc_qrcode` لاسترجاع معاينة مستند؛ يهيئ `qr_preview_entry` ويفتح صفحة معاينة.
- **هذه الشاشة لا ترفض الوثيقة نفسها**؛ العملية المختلفة `refuse_doc_company` توجد في `QRDocument`.
- **المراجعة:** تحقق هوية المستند عند المعاينة، واحتفظ بمعلومات العاملين/الرفض عند الحد الأدنى الضروري.

المراجعة السابقة: [RejectedLocalDocuments_deep_review_AR.md](../RejectedLocalDocuments_deep_review_AR.md).

## 9. `QRHealthCertificate-Byvh35hk(2).js` — قارئ الشهادة الصحية

**10,900 بايت** | SHA-256: `78b26ef2ba7f02c92745bc9bc5e61731d4972a390ba3c866d62ae8e000788936` | **مطابق للمراجع سابقًا**.

- يستخدم الكاميرا و`BarcodeDetector` و`jsQR`، مع إحداثيات جهاز المستخدم عند توفرها.
- يرسل `POST BorderPort_HS/read_doc_health` مع `url,x_coordinate,y_coordinate` وترويسة جلسة.
- يخزن بيانات الطباعة في `sessionStorage["hc_print"]` ويربطها بواجهة `PrintHealthCertificateView`، مع التعامل مع حالات خطأ وانتهاء صلاحيّة وفق الواجهة.
- توجد عتبة 48 ساعة في فحص عميل مشروط، بينما قد يعرض قالب الطباعة قيمة افتراضية أخرى عند غياب `validity_hours`؛ لا يُستنتج من ذلك قانون رسمي للصلاحية.
- **المراجعة:** ربط `hc_print` و`hc_detail` بالمعرّف نفسه، وعدم اعتماد التواريخ والنصوص المحلية بدل قرار الخادم.

المراجعة السابقة: [QRHealthCertificate_deep_review_AR.md](../QRHealthCertificate_deep_review_AR.md).

## 10. `ShipmentDoc-Dx885_fz(1).js` — الوثيقة المؤقتة والطباعة

**15,473 بايت** | SHA-256: `fb7034cc56552ec33c4a79674697dcd3691ec0dec8862fbd66c00e3ab1cfcf5b` | **مصدر كامل لفحص جديد**.

- يحوي `CompanyOwnerLayout` و`ShipmentDoc`، ويعتمد `props.doc` لعرض تاريخ ورقم الوثيقة والشركة والمواد والسائق والمركبة والمعلومات الترخيصية.
- يفحص `doc.qr_code || doc.response?.qr_code`:
  - صورة `data:image` جاهزة؛ أو رابط `robot?url=` تُؤخذ الحمولة منه؛ أو نص طويل Base64 يصنف صورة PNG؛ أو نص مباشر يرسم QR.
  - عند غياب QR يستخدم `license_approval_number` أو `vehicle_number` أو `driver_name` لرسم QR بديل معلوماتي، إن وجد.
- **لا يوجد QuickChart ولا POST/PUT** داخل هذا الملف؛ هو قالب عرض وطباعة فقط.
- لا يفك `%7C` عندما يقتطع النص بعد `url=`، لذلك قد يحدث اختلاف عند إدخال روابط encoded مقارنةً بالنص الخام. كما أن معيار Base64 لا يثبت أن السلسلة PNG.
- ينسخ HTML/CSS إلى نافذة طباعة A4 ذات ارتفاع ثابت `296mm` و`overflow:hidden`، وقد يقص الصفحات الطويلة.
- يستخدم watcher عميقًا وغير متزامنًا لإعادة رسم QR؛ لا يظهر حارس يمنع نتيجة قديمة من الكتابة بعد تحديث أحدث.

**تقرير جديد:** [ShipmentDoc_deep_review_AR.md](../ShipmentDoc_deep_review_AR.md).  
**فاحص:** [shipment_doc_review.py](../../../../tools/ish/shipment_doc_review.py).  
**اختبارات:** [test_shipment_doc_review.py](../../../../tests/test_shipment_doc_review.py).

## الربط النهائي بين الملفات

```text
شركة/منتجات:
CompanyOwnerView -> company_item_reduce أو return_company_doc
                 -> ShipmentDoc -> QR معطى أو QR محلي للطباعة

قراءة محلي/مستورد عبر شاشة QRDocument:
QRLocal / QRImported -> read_doc_company -> qrStore -> QRDocument

سجل سابق/مرفوض:
QRReadings / RejectedLocalDocuments -> return_doc_qrcode
                                    -> سجل معاينة محلي -> QRDocument

بوابة خروج المستورد:
QrLocalImporter -> useExitGate.searchImportedGoods
                -> support_org/read_qr_exitgate -> AchievementDocument

شهادة صحية:
QRHealthCertificate -> BorderPort_HS/read_doc_health
                    -> hc_print -> PrintHealthCertificateView
```

لا تثبت هذه الروابط كيفية ربط جداول الخادم أو تفويض المستخدم أو توقيع QR، وهي تبين الاتصالات داخل الواجهة فقط.

## ما الذي رفعناه إلى GitHub؟

- manifest بصمات الدفعة والمراجع السابقة.
- هذا التقرير المجمّع، فيه **عشرة أقسام مستقلة لكل ملف**.
- تقرير جديد معمق `ShipmentDoc`.
- أداة فحص ساكن `shipment_doc_review.py` ذات **26 مؤشرًا**.
- اختبار اصطناعي `test_shipment_doc_review.py` يغطي المؤشرات وسلامة الإدخال.

أكواد ملفات الجهات الخارجية لم تُنسخ إلى المستودع العام من جديد؛ النسخ الست القديمة المؤرشفة مسبقًا لم نكررها. هذا العمل لا يتضمن أي طلب مباشر إلى نظام رسمي ولا أي بيانات وثيقة حقيقية.
