# مراجعة UBOOR TECH — نتائج موثقة حتى 6 نوفمبر 2026

## منهج العمل وحدوده

تحليل ثابت للملفات المحفوظة لدى المستخدم، ومقارنة داخلية بين الوحدات، مع تحقق من المرجع الرسمي للمركز الوطني للتحول الرقمي العراقي (NDTC). لم تُنفّذ طلبات إلى API الخادم، ولا اختبارات تسجيل دخول أو إصدار أو رفض أو تجاوز WAF. الاستنتاجات أدناه تخص نسخة الشيفرة المحفوظة ولا تؤكد بالضرورة الحالة الحية لأي إصدار أحدث.

**المصدر الحكومي:** https://ndtc.gov.iq/services/aboor-platform — يصف منصة عبور وأنظمة TIR والمنتج المحلي والمستورد والشهادة الصحية البيطرية. تاريخ إطلاق نظام المنتج المحلي 15-01-2026. الإحصاءات المنشورة مؤرخة 19-08-2026، وليست لحظية.

## قائمة مصادر الشيفرة والتحقق من البصمات

| الملف | بايت | SHA-256 |
|---|---:|---|
| `index-gleMzSil.js` | 1,416,085 | `83d3f35e2cf05cc56fca81a3531b98381d291dc1e903957be7b6e433466b7ac3` |
| `QRLocal-5TAaXbzM.js` | 10,014 | `1e3ea9982971b4e4e08bb2ebee1520fe6a5056bc8590de4288fec80456fa9626` |
| `QRDocument-BJwpoEJY.js` | 607,716 | `23f8c5d87b6a91511af2a96f57075e8502861bd2f6d92d914a14222db4199400` |
| `QrCodeReaderCustoms-a-UBVR7y.js` | 16,490 | `09b62507255c25910a196ca0ca1e5fb6d961be5d10287face07cc777aaf45c0b` |
| `useExitGate-BvHNutwH.js` | 6,027 | `9d9a109e58d619a8afdf91bfcbd9f7e45377ddb8236e82e13597b896e56c3306` |

## نتائج مثبتة من الشيفرة الأصلية

1. **قناة إنشاء شحنة الشركة:** `PUT local_form/company_item_reduce` تستخدم Bearer صاحب الشركة. يتم تفكيك `response.data.data ?? response.data` لتحديث الحالة، بينما تُرجع الدالة `response.data` للمتصل. هذان مساران مختلفان للبيانات.
2. **تأكيد صاحب الشركة:** `POST local_form/company_verification` يرسل `{code}` ولا يتضمن رقم الهاتف في جسم هذه الدالة. يتلقى `access_token` ويخزنه في `localStorage` باسم `company_owner_token`.
3. **المصادقة المختلطة:** معالج طلبات Axios المشترك يستبدل رأس `Authorization` صراحة إذا وجد توكن موظف في Store `UserAuth`. لذلك قد يطغى توكن موظف على توكن صاحب شركة رغم تمرير الأخير في الدالة.
4. **رد HTTP 401:** المعالج المشترك يدعو `logout()` للموظف و`logoutOwner()` لصاحب الشركة في الرد نفسه. هذه معالجة مشتركة حتى لو كان الطلب يخص سياقًا واحدًا.
5. **قراءة المحلية:** `QRLocal` يستخدم `POST local_form/read_doc_company` ويرفق `url`, `x_coordinate`, `y_coordinate`. يكوّن رابط `/robot?url=` من النص الذي لا يبدأ بـ `http`. الإحداثيات قد تكون فارغة إذا تعذر الحصول عليها؛ لا توجد ممانعة محلية صريحة كما في بوابة الخروج.
6. **سرية التوكن:** `QRLocal` يطبع توكن الدخول مباشرة عبر `console.debug("[QRLocal] auth token:", y.token)` ويطبع بيانات طلب القراءة والرد.
7. **إعادة الإرسال بعد فشل القراءة:** عند حدوث استثناء من الطلب الأصلي، ينفذ `QRLocal` طلب `fetch` ثانياً إلى المسار نفسه ويطبع نص الاستجابة. تكرار الطلب مثبت؛ ما إذا كان المسار يغيّر الحالة الخادمية غير مثبت.
8. **مسار Login خاطئ:** `QRLocal` يستدعي `{name:"Login"}` عند غياب توكن، لكن قائمة المسارات في حزمة main تحتوي `LoginView` لا `Login`.
9. **حساب 48 ساعة محلي ومشروط:** تتحقق الواجهة من فارق `2880*60*1000` مللي ثانية فقط عندما لا تحتوي رسالة الاستجابة إحدى الكلمات العربية `/تم|نجح|نجاح|تم ارسال|تمت/`. تفحص أحدث تاريخ قابل للتحليل بين `date_str`, `date`, `created_at`, `license_approval_date`. لا دليل أن 48 ساعة هي قاعدة الخادم العامة أو قاعدة حكومية ملزمة.
10. **إشارة النجاح النصية ضعيفة:** مجرد احتواء الرسالة على مقطع `تم` يجعل فرع فحص عمر الوثيقة لا يعمل. مثال لغوي مثل «لم يتم» يطابق ذلك النمط. لا يوجد دليل على ورود هذه الرسالة بعينها من الخادم.
11. **سجل المعاينة المحلي:** `QRDocument` يبحث عن المعاينة بواسطة ID محلي. إذا لم يجده، يستخدم أول عنصر من السجل (`x[0]`) بدل عرض حالة «غير موجود»، ثم يفحص `qr_preview_entry` في Session Storage. هذا قد يعرض عنصرًا مختلفًا عند طلب ID غير موجود.
12. **تتبع قراءات السيطرات:** يعرض `QRDocument` زر «عرض السيطرات» ويحفظ `read_doc` في `sessionStorage` تحت المفتاح `qr_read_doc`.
13. **طلب رفض الوثيقة:** `POST local_form/refuse_doc_company` يرسل `{url,message,x_coordinate,y_coordinate}` مع توكن موظف. واجهة الرفض تظهر فقط عند `is_main` وامتياز `refuse_doc_company`؛ وتتحقق من سبب الرفض ومن المصادقة. عند نقص الموقع تستخدم السلسلة النصية `"0"`.
14. **تحميل صورة الوثيقة تلقائيًا:** عندما يحمل سجل المعاينة `auto_send`، ينشئ `QRDocument` صورة PNG من عنصر المستند، ويرفع `FormData` بحقلين `url` و`file` إلى `POST BorderPort_HS/path-document-file`. اسم الملف `local_document.png`، ولا يثبت هذا توقيعًا أو إنشاء PDF من الخادم.
15. **تفاصيل سجل المنفذ:** `useExitGate` يستخدم `POST support_org/paginate_qrcode_reader_import` مع ترشيح وتواريخ، و`POST support_org/return_doc_qrcode_export` لاسترجاع وثيقة الإنجاز، و`POST BorderPort_HS/return_doc_hc_by_docnumber` لاسترجاع شهادة صحية، و`POST support_org/download_qrcode_readers_import` لتنزيل Excel.
16. **مسح بوابة الخروج:** `POST support_org/read_qr_exitgate` يتطلب تحقق الواجهة من وجود الإحداثيات. نجاح الحالة HTTP 200 وحده كافٍ في الدالة للانتقال إلى `AchievementDocument` دون اختبار صريح لمعنى `success` داخل JSON.
17. **اختلاف خرائط البحث والتصدير:** البحث في `useExitGate` يطابق `doc_number` مع `doc_id`. أما تحويل مرشحات Excel في `QrCodeReaderCustoms` فيحافظ على `doc_number`؛ مساران مختلفان ثابتان بالشفرة. لا يوجد دليل أن عقود API تتطلب تطابقهما.
18. **صلاحية عرض تنزيل Excel:** في شاشة قراءات المنفذ، ظهور زر Excel مشروط بامتياز يحمل الاسم `download_health_qrcode_readers`. الاسم المثبت لا يعني صلاحيات الخادم أو أن الامتياز خاطئ، لكنه يجب أن يراجع مقابل RBAC الرسمي.
19. **تعريفات التوجيه:** في هذه الحزمة 63 تعريفًا لأسماء مسارات بحسب استخراج `name:` في فهرس Router؛ `QRMenu` و`HealthCertificates` يظهران مرتين. الأثر أثناء التشغيل غير محدد دون مراجعة إصدار التوجيه وبنيته النهائية.

## واجهات API الجديدة المثبتة مقارنة بالمراجعة الأولى

| HTTP | مسار نسبي | الغرض الذي تُظهره الواجهة |
|---|---|---|
| POST | `local_form/read_doc_company` | قراءة وثيقة شركة محلية |
| POST | `local_form/refuse_doc_company` | إرسال سبب رفض وثيقة |
| POST | `BorderPort_HS/path-document-file` | رفع صورة الوثيقة مع قيمة QR |
| POST | `support_org/read_qr_exitgate` | قراءة رمز بوابة الخروج |
| POST | `support_org/paginate_qrcode_reader_import` | قائمة قراءات المنفذ |
| POST | `support_org/return_doc_qrcode_export` | إعادة بيانات وثيقة الإنجاز بالرقم |
| POST | `BorderPort_HS/return_doc_hc_by_docnumber` | بيانات شهادة صحية بالرقم |
| POST | `support_org/download_qrcode_readers_import` | تنزيل ملف Excel |

## معلومات غير معروفة ولا يجب الجزم بها

- خوارزمية توليد QR أو أي توقيع تشفيري وسرّ التوقيع ومصدر مفتاحه.
- هل `company_hash_code` قيمة عشوائية، أو معرفًا، أو تجزئة، أو مزيجًا من ذلك.
- صلاحية وثيقة المنتج المحلي الرسمية؛ شرط 48 ساعة المكتشف في JavaScript ليس إثباتًا على ذلك.
- ما إذا كانت استجابة أي واجهة API الحية تقبل مستندات غير مصرح بها أو تتجاوز تحقق الملكية.
- نجاح أي عملية رفع أو رفض أو إصدار على الخادم؛ لم تنفذ تجارب حقيقية.
- تفاصيل وحدتي `AchievementDocument-DEzIzJ3I.js` و`qrStore-B8bgApfd.js` غير المرفقتين بصورة كاملة؛ محاولات الوصول العام إليهما لم تنجح.

## أولويات الإصلاح لتطبيق مخوّل

1. منع تسجيل رموز المصادقة ومحتويات الوثائق الحساسة في Console؛ وإزالة POST الثاني أثناء معالجة خطأ القراءة.
2. فصل عملاء Axios لسياقي الموظف وصاحب الشركة؛ وربط 401 بسياق الطلب المعني فقط.
3. إصلاح اسم مسار Login، وإظهار نتيجة «لم يتم العثور على المعاينة» بدل fallback إلى سجل مختلف.
4. التمييز بين نجاح HTTP والنجاح المنطقي في JSON، وإظهار فشل رفع PNG تلقائيًا للمستخدم المخوّل.
5. اعتبار صلاحية المستند وملكيته وتوقيعه ورفضه قواعد خادمية؛ وعدم الاعتماد على الكلمات في رسالة الاستجابة أو `localStorage`.
6. توثيق DTO لكل واجهة مع مطابقة `doc_number` و`doc_id` ونوع QR والإحداثيات ومعنى `is_main`.

## خلاصة

يمكن استنتاج بنية تدفق الواجهة الموصوفة أعلاه بدرجة ثقة مرتفعة من الشيفرة المحفوظة، لا إثبات تنفيذ الخادم أو أصالة وثيقة حقيقية. التقارير السابقة التي تتجاوز ذلك يجب تصحيحها.

## ملحق: المطابقة المباشرة مع وحدات الواجهة المقتطعة من تسجيل HTTP

استخرجت الشيفرة المصدرية من سجل HTTP المرفق سابقاً دون نسخ ترويسات الجلسة: `ShipmentDoc-Dx885_fz.js` (14,682 حرفًا) و`CompanyOwnerView-CIdFF3LL.js` (22,977 حرفًا). لا يُعد السجل شهادةً على نجاح استخدام الجلسة أو على قواعد API الداخلية.

في `ShipmentDoc` تبيّن نصًا أن `doc?.qr_code || doc?.response?.qr_code` يُعرض كصورة إن بدأ بـ`data:image`؛ ويُحذف من رابط `/robot?url=` الجزء السابق لـ`url=` لإنشاء QR من الجزء المتبقي؛ ويصنّف النص Base64 الطويل صورة PNG دون تحقق من ترويسة الملف؛ وفي حال غياب `qr_code` يستخدم `license_approval_number` ثم `vehicle_number` ثم `driver_name` لتوليد QR **معلوماتي**. هذه الحالة الأخيرة ليست توقيع تحقق رسمي.

تفتح الطباعة نافذة HTML جديدة بحجم A4؛ إنشاء صفحة قابلة للطباعة لا يثبت اعتماد جهة حكومية. في الطباعة يوجد `height:296mm` مع تصميم صفحة ثابتة، ويجب اختبار القص على الوثائق الطويلة.

## ملحق: أسماء API النسبية في حزمة التطبيق الرئيسية (فهرس نصي)

هذا جرد لسلاسل المسارات الصريحة في `index-gleMzSil.js`؛ لا يتضمن كافة المسارات المركّبة ديناميكياً ولا يعد توثيقًا لعقد الخادم:
- `auth/login_check`
- `auth/login_no_otp`
- `auth/login_otp`
- `auth/logout`
- `auth/send_otp`
- `auth/send_otp_ur_auth`
- `local_form/all_iraqi_company`
- `local_form/company_field_name`
- `local_form/company_item_info/`
- `local_form/company_item_reduce`
- `local_form/company_items_active/`
- `local_form/company_items_delete/`
- `local_form/company_verification`
- `local_form/company_verify_login`
- `local_form/download_company_checkpoint`
- `local_form/download_file`
- `local_form/download_file_item`
- `local_form/get_company_items/`
- `local_form/iraqi_company_active/`
- `local_form/iraqi_company_delete/`
- `local_form/iraqi_company_info/`
- `local_form/iraqi_company_items/`
- `local_form/iraqi_company_reliable/`
- `local_form/paginate_company_ceo`
- `local_form/paginate_company_checkpoint`
- `local_form/pagination_rejected_qrcode_reader`
- `local_form/return_company_doc/`
- `local_form/return_doc_ceo`
- `local_form/return_doc_qrcode`
- `local_form/search_iraqi_company`
- `local_form/send_company_code/`