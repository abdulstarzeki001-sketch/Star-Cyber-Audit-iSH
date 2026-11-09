# مراجعة دفعة QR / UBOOR الخامسة — سبعة ملفات، سطرًا ودالةً

**التاريخ:** 9 نوفمبر 2026  
**المصادر:** سبعة ملفات JavaScript رفعها المستخدم ضمن المحادثة.  
**طريقة الإثبات:** SHA-256 وGit blob SHA-1 للملفات السبعة، قراءة المصدر مباشرة وفحص Node.js النحوي فقط للملفين الجديدين (دون تشغيل المنصة).  
**نتيجة الجرد:** ملفان جديدان `AppPagination` و`BaseModal`؛ خمسة ملفات **مطابقة بايتًا ببايت** لنسخ مؤرشفة مسبقًا.  
**سجل البصمات:** [manifest.json](manifest.json)  
**مواضع المصدر:** [SOURCE_ANCHORS.json](SOURCE_ANCHORS.json) يحوي 60 موقعًا حرفيًا مع offset ورقم السطر الأصلي في الملفين الجديدين.  
**حماية:** هذا فحص **Static Frontend**؛ لم نتصل بمنظومات الحكومة ولم نعتمد مستندًا أو نختبر صلاحيات Backend، ولم ننشر QR أو بيانات أشخاص حقيقية.

> معظم ملفات Vite مصغّرة، ولذلك `AppPagination` و`BaseModal` يضمان عشرات الوظائف في **سطر مادي واحد**. «سطر سطر» هنا يعني تحليل كل كتلة دالة أو شرط مع موقع الحرف الدقيق، لا اختراع ترقيم أسطر مستحدث.

## 1) AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5(1).js

**الحجم 11,774 بايت؛ سطر مادي واحد؛ SHA-256:** `7c94b32bcc68a625b8136dee16767e8c59e066cefeadbb958f5fdec5bc02c4f5`.  
**الملف الفريد الذي رُفع:** [AppPagination.js](../../../research/user-supplied/2026-11-09/AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5.js).

### تفكيك المكونات بحسب ظهورها في النص

| مرجع الموضع | الكتلة | المهمة |
|---|---|---|
| PG-01–PG-04 | `PaginationRoot` | سياق الصفحات، current page، إجمالي الصفوف، حجم الصفحة، عدد الصفحات المحسوب، حدث update:page الداخلي |
| PG-05/06 | `PaginationFirst / PaginationLast` | أزرار الصفحة الأولى والأخيرة، والتعطيل عند الحد |
| PG-07–PG-09 | `C / ge / me` | توليد مدى أرقام الصفحات، ثم تمثيل الفجوات بنقاط حذف |
| PG-10/11 | `PaginationList / PaginationListItem` | توليد عناصر الصفحة، وإظهار الصفحة المحددة عبر aria-current |
| PG-12/13 | `PaginationNext / PaginationPrev` | أزرار التالي والسابق |
| PG-14 | `ButtonGroup` | حاوية أزرار التحكم |
| PG-15 | `Pagination` | تجميع عناصر التنقل، وتبديل الأسهم بحسب RTL |
| PG-16–PG-30 | `AppPagination` | الربط الفعلي مع تطبيق عبور، إدخال حجم الصفحة وإصدار الأحداث للأب |

### عقد المكوّن

```text
Props:
 currentPage = 1
 totalPages = 1
 perPage = 10
 totalRows = 0

Emits:
 "page-changed"     -> {page: Number, per_page: Number}
 "per-page-changed" -> {page: 1, per_page: Number}
```

يحسب المكوّن `PaginationRoot.pageCount` حسب المعادلة:

```javascript
Math.max(1, Math.ceil(total / (itemsPerPage || 1)))
```

حيث `total` يأتي من `totalRows`، و`itemsPerPage` من `perPage`. **خاصية `totalPages` تُعرّف في Props، لكنها لا تستعمل في بناء عدد الصفحات الظاهر.** إذا كان totalRows لا يساوي ما يفترضه خادم التصفح، قد تظهر صفحات أقل أو أكثر مما يقرره خادم API.

### ماذا يحدث عند ضغط الأزرار؟

- زر رقم الصفحة أو «التالي» يغيّر `s.value` مؤقتًا ويصدر `page-changed` مع `page` الجديد و**`per_page:e.perPage` المأخوذ من Prop**، لا من قيمة حقل الكتابة غير المؤكدة.
- حقل «عدد العناصر» مرتبط بـ`a.value`. عند Enter أو زر التحديث، يحاول `Number(a.value)` ثم، عندما تكون موجبة وغير NaN، يرسل `per-page-changed` ويعيد الصفحة إلى 1.
- إذا كانت القيمة صفرًا/سالبة/غير رقمية يضع `a.value=10` لكنه **لا يصدر حدث تغيير حجم الصفحة**؛ هذا يعني أن الشاشة الأب قد تظل على الحجم القديم.
- لا يوجد فحص `Number.isInteger` أو `Number.isFinite` أو حد أعلى في هذا المكوّن؛ إدخال كسري/كبير جدًا أو Infinity برمجيًا ليس محظورًا صراحة في المعالج.
- مزامنة الصفحة والحجم من الأب تتم بمراقبين مستقلين لخاصيتي `currentPage` و`perPage`.

### الربط مع ملفي المشروع السابقين

**`CompanyOwnerCeoLoadsView`** يمرر:
`current-page=x.value`، `total-pages=D.value`، `per-page=m.value`، `total-rows=V.value`، ويستقبل الحدثين بـ`onPageChanged:R` و`onPerPageChanged:R`. المعالج `R=a=>{x.value=a.page,m.value=a.per_page,I()}` يستدعي `fetchCompanyCeoLoads` في store الذي يستخدم `POST local_form/paginate_company_ceo`. الشكل متوافق مع الحدث الجديد، ولكن إهمال `totalPages` وعدم ضبط `per_page` محليًا قد يؤديان إلى اختلاف عدد الصفحات المعروض عن العدد المسترجع.

**`IndexPage`** يستخدم AppPagination لجدول فترات بقاء المركبات، مع نتائج `POST metrics/kpi/vehicle_stay_duration`. ينبغي توحيد حقول التصفح لهذا الجدول مع عقد AppPagination.

### الملاحظات مرتبة بالأولوية

| درجة | الشاهد | الأثر/المطلوب |
|---|---|---|
| P2 | `totalPages` معرف وغير مستخدم | فرض عقد موحد: totalRows + perPage موثوقان، أو استخدام totalPages عندما يكون هو مصدر الحقيقة |
| P2 | حجم صفحة غير صحيح يعيد 10 دون emit | إصدار قيمة افتراضية معترف بها، أو إظهار خطأ دون تغيير محلي صامت |
| P2 | `Number(a.value)` دون integer/finite/maximum | validate Number.isSafeInteger والحجم المقبول من Backend |
| P3 | الحدث `page-changed` يستعمل قيمة الـProp رغم حقل كتابة غير مطبق | توضيح UI أن حجم الصفحة لا يطبق إلا بضغط الزر، أو توحيد المصدر |
| P3 | التنقل يعطل حسب pageCount | اختبار حالات totalRows=0 و1 وحدود الصفحة وبعد تغيير الفلاتر |

هذه **ملاحظات واجهة** وليست إثباتًا أن خادم UBOOR يقبل حجم صفحة غير صالح.

## 2) BaseModal-DjCaQzje(1).js

**الحجم 3,587 بايت؛ سطر مادي واحد؛ SHA-256:** `035b2869ad0e11fbfc228fde484c732225d2d9e197356a9172bf5d429b06b842`.  
**المصدر الجديد:** [BaseModal.js](../../../research/user-supplied/2026-11-09/BaseModal-DjCaQzje.js).

### تحليل الكتل بالترتيب

| مرجع الموضع | الجزء | ما يحدث |
|---|---|---|
| BM-01–BM-05 | Props / emits | `isOpen`، العنوان، الحجم، الأبعاد، السماح بالنقر الخارجي، زر الإغلاق، Esc؛ حدثا close وupdate:isOpen |
| BM-06/07 | `modal-title-...` / sizing | ID محسوب لربط عنوان الحوار، ودعم أبعاد مخصصة أو قياسية |
| BM-08/09 | `u / M` | إغلاق النافذة؛ النقر على الخلفية يغلق فقط إذا كان disableOutsideClick=false وtarget===currentTarget |
| BM-10–BM-14 | `_ / b / z` | عند الفتح: إيقاف تمرير الصفحة وتعويض شريط التمرير؛ عند الإغلاق: مسح القيم |
| BM-15–BM-18 | `g / k` | جمع العناصر القابلة للتركيز، وإرجاع Tab/Shift+Tab من آخر عنصر إلى الأول والعكس |
| BM-19–BM-21 | `watch(isOpen)` | حفظ العنصر السابق النشط، التركيز داخل النافذة، وإرجاع التركيز عند الإغلاق |
| BM-22/23 | lifecycle | تسجيل مستمع keydown عند mount وإزالته عند unmount |
| BM-24–BM-30 | render | Teleport إلى body، انتقالات fade/slide، role=dialog، aria-modal، aria-labelledby، ومعالجة Escape |

**الإعدادات الافتراضية في الكود:**
- `disableOutsideClick: true` — النقر خارج النافذة لا يغلقها.
- `showCloseButton: true` — زر الإغلاق ظاهر.
- `enableEscapeKey: true` — Escape يغلقها إذا وصل الحدث إلى عنصر المحتوى.
- عند الإغلاق: يصدر `close` و`update:isOpen=false`.

### الربط مع بقية الأكواد

- `CompanyOwnerView` يستعمل `BaseModal` لإدخال معلومات الشحنة وعرض الوثائق.
- `CompanyOwnerCeoLoadsView` يستعمله لتفاصيل الحمولة ونافذة `ShipmentDoc`؛ نافذة الطباعة تمرر `enable-escape-key:false` و`disable-outside-click:true`.
- `StationsDetailsModal` يستورد `BaseModal` لعرض بيانات المحطات وملفاتها. حدث `download-file` في النافذة الداخلية يذهب إلى الأب الذي يستعمل `useAttachments`؛ BaseModal نفسه **لا ينزّل ملفات ولا يرسل POST**.
- هذه المكتبة مختلفة عن `Modal-C_od4hhs.js`؛ كلاهما Dialog، لكن لا يجوز الخلط بين تنفيذيهما.

### المراجعة الأمنية وتجربة الاستخدام

| درجة | شاهد المصدر | تعليق |
|---|---|---|
| P2 | `document.body.style.overflow=""` و`paddingRight=""` عند الإغلاق | لا يستعيد القيم السابقة؛ قد يمسح نمطًا أصليًا للصفحة أو يكسر قفل تمرير حوار آخر متداخل |
| P2 | قفل تمرير global بلا عداد/stack | عند نافذتين متداخلتين، إغلاق إحداهما قد يحرر التمرير بينما الثانية ما تزال مفتوحة |
| P3 | Tab trap يلف عند أول/آخر عنصر قابل للتركيز | يحتاج اختبار keyboard حقيقي للحوار الخالي من عناصر تفاعلية، إذ يعود بدل عدم نقل التركيز |
| P3 | استعادة `document.activeElement` السابقة | إذا أزيل عنصر الاستدعاء من DOM قبل إغلاق النافذة فقد لا يمكن استعادة التركيز بشكل مفيد |
| P3 | `role=dialog` و`aria-*` موجودة | إيجابي، لكن اختبار قارئ الشاشة وإدارة focus الفعلية مطلوب؛ وجود الخصائص لا يكفي وحده |

لا يُظهر المكوّن تفويضًا رسميًا أو تغيير بيانات معاملة، ولذلك لا توجد فيه أدلة على تجاوز إداري.

## 3) QrLocalImporter-DYzNB5Fh(5).js

**7,222 بايت؛ SHA-256:** `59ff26bfbc4b731799101527e9604fc736c170e80e4988eb69be672990cf8208`؛ **نسخة مطابقة** لأرشيف `QrLocalImporter-DYzNB5Fh.js`. يفتح الكاميرا، ويحاول `BarcodeDetector` ثم fallback `jsQR`، ويأخذ GPS، ويمرر محتوى QR بعد تطبيع الرابط إلى `useExitGate.searchImportedGoods`. ملف القراءة لا يستدعي Backend مباشرة. توجد حماية محلية من قراءة متكررة لمدة 3 ثوان، وقد يمنع إحداثي صفر بواسطة شرط truthy. عند قراءة ناجحة يتم إيقاف مسح الإطارات حتى يعاد تفعيله. لا يدل نجاح فك الصورة على صحة وثيقة أو صلاحية خادم.

## 4) CompanyOwnerCeoLoadsView-Coghn9Xh(2).js

**20,697 بايت؛ SHA-256:** `fcc33ae6957649ab3a6881196b231e1891dd7ec0d1a440b376ab45bcffefcacd`؛ مطابق للمؤرشف. يعرض سجلات الحمولات، خيارات البحث، تفاصيلها، والرجوع إلى `ShipmentDoc` للطباعة. يعتمد الآن على `AppPagination` الذي استلمناه وفهمنا أحداثه، وعلى `BaseModal` الذي استلمناه. تتضمن مخاطر نصية تحويل `doc_number` إلى Number، ووضع افتراضي نشط عند غياب قيم boolean؛ هذه ليست أحكامًا على صحة البيانات الحكومية.

## 5) useExitGate-BvHNutwH(5).js

**6,027 بايت؛ SHA-256:** `9d9a109e58d619a8afdf91bfcbd9f7e45377ddb8236e82e13597b896e56c3306`؛ مطابق للمؤرشف. دواله:

- `searchImportedGoods`: `POST support_org/read_qr_exitgate` مع URL وGPS، والانتقال إلى `AchievementDocument` عند HTTP 200.
- `fetchCertificateReadersCustoms`: `POST support_org/paginate_qrcode_reader_import` لفهرس قراءات المستورد.
- `fetchCertificateReaderDetail`: `POST BorderPort_HS/return_doc_hc_by_docnumber`.
- `fetchAchievementDocDetail`: `POST support_org/return_doc_qrcode_export`.
- `downloadCertificateReadersCustoms`: `POST support_org/download_qrcode_readers_import` في `arraybuffer` ثم حفظ Excel.
- `ensureLocationLookupsForCertificate`: يفوض تحميل أسماء المواقع إلى `useHealthCertificate`.

**تنبيه:** HTTP 200 وحده لا يساوي اعتمادًا خادميًا نهائيًا.

## 6) CompanyOwnerView-CIdFF3LL(6).js

**24,517 بايت؛ SHA-256:** `78af159ff95bf493a5050b4fb0fe6e4068ee49576100829ce1783644f92d2b2d`؛ مطابق. يجمع `AppUrLogin` و`VSearchHashCode` و`CompanyOwnerItems` و`CompanyOwnerView`. يرسل اختيار المواد والمعلومات إلى `PUT company_item_reduce` ويفتح `ShipmentDoc`؛ ويستعمل `return_company_doc/{hash}` لمسار إعادة توليد/استرجاع الوثيقة. الواجهة تحمل المفتاح `vihcle_info` حرفيًا. وصلت `BaseModal` المستخدمة في إدخال معلومات السائق والشحنة.

## 7) index-gleMzSil(3).js

**1,416,085 بايت؛ 946 سطرًا ماديًا؛ SHA-256:** `83d3f35e2cf05cc56fca81a3531b98381d291dc1e903957be7b6e433466b7ac3`؛ **مطابق بايتًا ببايت لـ`research/raw-uploads/2026-11-07/index-gleMzSil(1).js`**. هذا ملف Vite جامع: Vue ومكونات UI وRouter/Pinia وAxios stores وتعيين المسارات الديناميكية.

الأجزاء المتعلقة بهذه الدفعة:
- store صاحب الشركة: `companyVerifyLogin` و`companyVerifyLoginWithCode` و`searchCompanyOwner` و`getOwnerCompanyItems` و`companyItemsReduce` و`returnCompanyDoc`.
- سجل حمولات الرئيس: `fetchCompanyCeoLoads` → `POST local_form/paginate_company_ceo`؛ `returnDocCeo` → `POST local_form/return_doc_ceo`.
- وظائف مشغلي السجلات وQR والعرض العام: مصادقة توكن الشركة/الموظف، مسارات المكونات، Ajax interceptors وأدوار العرض.
- استيراد `AppPagination` و`BaseModal` كأجزاء lazy يثبت أنهما ضمن نفس بناء الأصول، لكنه لا يضيف إليهما أي وظيفة توقيع QR أو إصدار مستند رسمي.

هذا الملف كبير ويضم الكثير من كود مكتبات Vue المجمّع. لذلك لم نكرر نشره؛ مصدره الأصلي متاح في المستودع السابق، والحديث هنا عن التغييرات التي أضافها **وصول اعتمادياته الناقصة**.

## ماذا أصبح محسومًا وماذا بقي ناقصًا؟

**أصبح لدينا:**
- عقد إصدار أحداث الصفحات وكيف يستجيب له سجل حمولات صاحب الشركة.
- قاعدة احتساب عدد الصفحات وسلوك تطبيق حجم الصفحة.
- مكوّن BaseModal المستخدم في بوابة الشركة والسجلات والمحطات.
- المصدر الكامل للحزمة الرئيسية وربطها بملفات المكونات السابقة.
- سبعة checksums للمقارنة مع أي ملفات مستقبلية.

**لم نحصل بعد على:**
- `index-ccmhdhtn.js`، الحزمة الرئيسية من بناء واجهة صاحب الشركة الآخر؛ مقارنتها مع الحزمة الحالية ما زالت مهمة.
- `Input-XMNBc09N.js` الذي يستخدمه AppPagination؛ مطلوب لتفصيل سلوك حقل الإدخال.
- `Textarea-vxo1mVYX.js` وبعض ملفات CSS لمراجعة النماذج المطبوعية والأبعاد.
- Backend أو عقد API معتمد يثبت كيف تُصدر الوثيقة وتُتحقق صلاحية QR.

## الحدود

جميع النتائج أدلة على **نص JavaScript client-side** فقط. لم نجرب حسابات أو توكنات أو QR حكومية أو استدعاءات تغيير حالة، ولا يمكن استنتاج صلاحية الوثيقة الرسمية من وجود صورة QR أو شاشة ShipmentDoc أو زر طباعة. 
