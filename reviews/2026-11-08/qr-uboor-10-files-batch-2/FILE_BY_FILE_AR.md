# مراجعة الدفعة الثانية من 10 ملفات — QR / UBOOR / UR-DMS

**تاريخ الفحص:** 8 نوفمبر 2026  
**المصدر:** الملفات التي رفعها المستخدم في المحادثة، تمت قراءتها كاملة وحُسبت SHA-256 وGit Blob SHA-1 محليًا.  
**النطاق:** تحليل واجهات Vue/Vite وDMS/Webpack دون تنفيذ الشيفرة أو طلب أي API حكومي أو استعمال جلسات مصادقة.  
**الخصوصية:** لا تُنشر في هذه الإضافة نسخ JavaScript جديدة من الطرف الثالث أو QR فعلي أو بيانات شركة/سائق/مستخدم؛ فقط تقرير وبصمات وأداة فحص واختبارات اصطناعية.  
**البصمات الكاملة:** [manifest.json](manifest.json)

**النتيجة:** ثمانية مصادر مطابقة لنسخ سبق فحصها بالتفصيل، و`EntranceGateView` و`ExitGateView` خضعا لمراجعتين مخصصتين أعمق في هذه الدفعة. لا تعني لاحقات أسماء الملفات `(1)` و`(4)` تحديثًا في المصدر عندما تكون البصمة نفسها.

## 1) `QrControlScan-M6uGJnR1(1).js` — سجل QR المحلي

الحجم **8,315 بايت**، SHA-256: `0848ead8a6082769241885b6e5de6fd26aa783cbfce832f46448780378bbd78c`.

مكوّن Vue لعرض «سجل القراءات» والبحث بالنص/التاريخ، والتصفح، ومعاينة الوثيقة والتصدير وفق امتيازات واجهة. **لا يشغّل الكاميرا ولا يُصدر POST بنفسه**؛ يستورد `be()` من `useLocalCompany-DfV5kpAj.js`. ويختلف عن مكوّن `QRReadings` الذي يحوي طلبات API مباشرة.

**ملاحظة هندسية:** لا يجب اعتبار قيد زر التصدير/المعاينة ضمانًا لصلاحية Backend، ولا الوثيقة المعروضة من تخزين محلي حدث قراءة رسميًا.  
[التحليل السابق](../QrControlScan_deep_review_AR.md).

## 2) `DisableDocument-AXBjrkYS(1).js` — قراءة وتعطيل وثيقة

الحجم **11,505 بايت**، SHA-256: `e8f574544e0f910f8ec66446810627a13352065d7b6ae2a3b1a89c0439f60e01`.

قارئ QR خاص بعملية `POST local_form/reset_company_qrcode`، مع `url` والإحداثيات الجغرافية والتوكن. يستعمل `BarcodeDetector` أو `jsQR`، ويغلف النص الخام داخل `robot?url=` عند الحاجة.

**أبرز نقطة:** هذا إجراء قد يغيّر حالة وثيقة، وليس استعلام عرض فقط. في فرع الاستثناء يوجد POST تشخيصي قد يعيد العملية. لا يثبت JavaScript نجاح تعديل رسمي أو إمكانية تخطي التفويض.  
[التحليل السابق](../DisableDocument_deep_review_AR.md).

## 3) `EntranceGateView-B9IBJo4k.js` — بوابة الدخول

الحجم **21,501 بايت**، SHA-256: `d48910ae500903a80deaf740cba67485c76e3af789fcff2e1f4d6f86d2419988`.

يحوي مكوّنين: `EntranceGateView` وشاشة قرار `EntranceGateModel`، ويستورد `jsQR` و`useAttachments` و`StationsDetailsModal`. يفتح الكاميرا ويرسم كل إطار على Canvas ثم يستخدم `jsQR`؛ لا يستخدم `BarcodeDetector` في هذا الملف.

1. يمرّر QR وGPS إلى `POST carrier_register/scrape_search_goods_gateway_register`.
2. يتوقع HTTP 200 و`response.data.Agent_name` ليستقبل بيانات البضاعة، ويضبط `hash_id`.
3. يتيح قرار `APPROVED` أو `REJECTED` وسببًا ومرفقات، مع زر يظهر عند وجود امتياز `gateway_decision` وحالة `status="غير محددة"`.
4. يرسل `POST carrier_register/gateway_decision` باستخدام `FormData`: `hash_id`، `decision`، `decision_reason`، `x_coordinate`، `y_coordinate`، ومفاتيح `attachment[0]` إلخ.
5. يمكن التقاط ملف JPEG من كاميرا منفصلة ضمن نافذة القرار.

**نتائج جديدة:** شرط QR المستخرج من الكاميرا يقبل HTTPS فقط بينما الإدخال اليدوي لا يستخدم فحصًا مماثلًا؛ حالة حمولة سابقة قد تبقى إذا فشل بحث جديد؛ بعد POST القرار تُعرض عبارة «تم إرسال قرار الموافقة بنجاح» حتى عندما تكون القيمة المطلوبة `REJECTED`. تحقق الخادم غير ظاهر.  
[المراجعة الجديدة المفصلة](../EntranceGateView_deep_review_AR.md).

## 4) `QRCheckpoints-Brs0uL0-(1).js` — عرض تاريخ السيطرات

الحجم **2,797 بايت**، SHA-256: `b2f6e7519df369ff58345adedcc4fb1cc2d83416f409cffe0cd93a8869aae53b`.

يستقبل `props.items`، أو يستعمل `history.state.read_doc` ثم `sessionStorage["qr_read_doc"]` ثم بيانات `route.query.read_doc` عند الحاجة. يعرض `doc_reader_org_name` و`time_stamp` وإحداثيات المكان وروابط خرائط.

**المراجعة:** لا يطلب API ولا يسجل قراءة ولا ينفذ رفضًا. البدائل المحلية غير مرتبطة بمُعرّف وثيقة إلزاميًا في الكود، وقد يظهر سجل قديم أو غير مطابق؛ ووجود إحداثي واحد لا يكفي لرابط خريطة صحيح.  
[التحليل السابق](../QRCheckpoints_deep_review_AR.md).

## 5) `CompanyOwnerView-CIdFF3LL(2).js` — صاحب الشركة والشحنة

الحجم **24,517 بايت**، SHA-256: `78af159ff95bf493a5050b4fb0fe6e4068ee49576100829ce1783644f92d2b2d`.

يتضمن `CompanyOwnerItems` و`VSearchHashCode` و`AppUrLogin` و`CompanyOwnerView`. تتضمن عملية مالك الشركة التحقق بـ`company_verification` والبحث بـ`search_iraqi_company` وجلب المواد بـ`get_company_items` و`PUT company_item_reduce` وتجديد الوثيقة عبر `return_company_doc/{hash}`. يعرض نتيجة الشحنة في `ShipmentDoc`.

**المراجعة:** طباعة hash في Console، رقم الهاتف في رابط العودة، التوجيه داخل `finally`، تحقق كميات في الواجهة فقط، والإحداثيات الصفرية؛ توجد كتابة `vihcle_info` حرفيًا في payload. يجب الرجوع إلى عقد الخادم قبل تعديل الاسم.  
[التحليل السابق](../CompanyOwnerView_deep_review_AR.md).

## 6) `QrCodeReaderCustoms-a-UBVR7y(3).js` — سجل قراءات المستورد

الحجم **16,490 بايت**، SHA-256: `09b62507255c25910a196ca0ca1e5fb6d961be5d10287face07cc777aaf45c0b`.

واجهة سجل قراءات الجهة والوثيقة؛ بحث واختيار حقول وتصفية وأزرار نسخ وتصدير ومعاينة استمارة الناقل. تعتمد `useExitGate` لتنزيل سجل المستورد واسترجاع تفاصيل `AchievementDocument`؛ لا تشغّل كاميرا رغم اسم «Reader».

**المراجعة:** فرق `doc_number` عن `doc_id` بين مسار البحث والتصدير، وفصل الأذونات، وتجنب طباعة أجسام التصدير الحساسة في Console.  
[مرجع سابق](../../2026-11-07/reference/UBOOR_verified_update_2026-11-06.md).

## 7) `QRDocument-BJwpoEJY(4).js` — معاينة المنتج المحلي

الحجم **607,716 بايت**، SHA-256: `23f8c5d87b6a91511af2a96f57075e8502861bd2f6d92d914a14222db4199400`. حجم الملف الكبير يشمل مكتبات مشتركة للطباعة والتوليد، وليس كله منطق مستند.

يعرض `QRDocument` ورقم الوثيقة والبيانات و`read_doc` وQR والطباعة؛ يتعامل مع `RefuseDocModal` و`POST local_form/refuse_doc_company`، ويرفع صورة PNG مشروطًا بعلم `auto_send` إلى `BorderPort_HS/path-document-file`.

**المراجعة المهمة:** عند فشل مطابقة ID في قائمة `qr_readings` قد يختار أول سجل `x[0]`، فيعرض وثيقة غير المطلوبة محليًا. هذا لا يغير قاعدة بيانات الحكومة ولا يثبت تجاوز تفويض الخادم.  
[التحليل السابق](../QRDocument_deep_review_AR.md).

## 8) `AchievementDocument-DEzIzJ3I(3).js` — استمارة الناقل

الحجم **11,641 بايت**، SHA-256: `bec1dbe0a25694f05f30d5dcf6edb253fb2f9276d9e00b583ba416aabc941d7c`.

يعرض نتيجة `support_org/return_doc_qrcode_export` أو استجابة قراءة بوابة الخروج. يستخدم QR مأخوذًا من `qr_code || doc_id || doc_number` ويرسم صورة محليًا؛ عند فشل الرسم قد يستخدم خدمة خارجية `quickchart.io`. يعرض `QRCheckpoints`، ويطبع HTML بقياسات A4.

**المراجعة:** سقوط QR إلى رقم الوثيقة ليس توقيعًا، وتوليد QR خارجي قد يكشف النص لخدمة طرف ثالث، و`height:296mm;overflow:hidden` قد يقص مستندًا طويلًا.  
[التقرير السابق](../../2026-11-07/reference/UBOOR_AchievementDocument_verified_addendum_2026-11-06.md).

## 9) `ExitGateView-D33Au6wp.js` — بوابة الخروج

الحجم **4,468 بايت**، SHA-256: `4c7d47c65b845c7b00143dfed244f28435cf5e2c64d6da9330820b3b53fbdc52`.

مكوّن صغير يقرأ QR باستخدام كاميرا الفيديو وCanvas و`jsQR` ثم يمرره إلى `useExitGate.searchImportedGoods`؛ هذه الدالة تستدعي `support_org/read_qr_exitgate` في الملف المستورد. يوقف مسارات الفيديو عند توقف الكاميرا أو إغلاق الشاشة.

**الفرق عن بوابة الدخول:** كاميرا الخروج تسمح بالنصوص التي تبدأ بـHTTP أو HTTPS؛ الإدخال اليدوي ينقل النص مباشرة إلى الخدمة المستوردة؛ **لا يوجد نموذج `gateway_decision` أو مرفقات في هذا المكوّن**.  
[المراجعة الجديدة المفصلة](../ExitGateView_deep_review_AR.md).

## 10) `employee.21e9f881(20261108-121032).js` — لوحة موظفي أور/DMS

الحجم **33,085 بايت**، SHA-256: `265169d6dbf0cf25cbcb654d61f50c1468b7e088ae56e43598f82218642a12f5`؛ Git Blob SHA-1: `45a027208a4928f9a32dd97e85aafc459cbaf355`، مطابق لما هو مؤرشف.

يخص تطبيق `DMS` المبني بـWebpack/Vue 2، وليس جزءًا تنفيذيًا من حزمة UBOOR/Vite نفسها. يعرض لوحة الموظف وقائمة أدوار ومسارات قراءة QR والوثائق والإدارة، ويوفر `opendm()` للتنقل إلى نظام آخر.

**المراجعة:** وظيفة `opendm()` قد تطبع `userRedirect` و`passRedirect` وتضيف قيمتيهما إلى URL ضمن `su1` و`su2`؛ لا يثبت الكود أن الثانية كلمة مرور صالحة لكنه يخلق خطر تسرب إن كانت قيمة اعتماد. يحتاج فصل مصادقة وحماية بيانات المستخدم.  
[تقرير DMS](../dms-employee-assets/DETAILED_STATIC_AUDIT_AR.md).

## مقارنة وظيفية سريعة

```text
CompanyOwnerView -> company_item_reduce / return_company_doc -> ShipmentDoc
QRLocal/QRImported -> read_doc_company -> qrStore -> QRDocument
QrControlScan -> useLocalCompany -> سجل قراءات المحلي -> QRDocument
QRCheckpoints -> عرض read_doc الوارد من سياق المستند
DisableDocument -> reset_company_qrcode  [إجراء حالة مستقل]
EntranceGateView -> scrape_search_goods_gateway_register -> gateway_decision
ExitGateView -> useExitGate -> read_qr_exitgate -> AchievementDocument
QrCodeReaderCustoms -> useExitGate -> سجل مستورد/معاينة
employee.21e9f881 -> تطبيق DMS وواجهة أدوار/روابط مختلفة
```

## الإضافة إلى GitHub

- [Manifest البصمات](manifest.json): عشر بصمات SHA-256 وGit blob لأسماء الملفات المرفوعة.
- [EntranceGateView deep review](../EntranceGateView_deep_review_AR.md) و[ExitGateView deep review](../ExitGateView_deep_review_AR.md).
- فاحص offline جديد [gate_views_review.py](../../../tools/ish/gate_views_review.py): 18 مؤشر دخول و9 خروج.
- [اختبارات اصطناعية](../../../tests/test_gate_views_review.py): 34 اختبارًا لأسماء المكونات والدوال والقيود والإدخالات غير السليمة.
- هذا التقرير يربط الملفات الثمانية المتطابقة بتقاريرها السابقة، ويمنع إنشاء نسخ مكررة من المصدر.

**لا يعني عدد المؤشرات أو نجاح CI وجود ثغرات خادمية مؤكدة.** لم نختبر خدمات الحكومة أو نفك تشفير أي QR أو نغيّر معاملة رسمية.
