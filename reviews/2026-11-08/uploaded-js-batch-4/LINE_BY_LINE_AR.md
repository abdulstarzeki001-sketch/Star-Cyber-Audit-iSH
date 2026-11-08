# تحليل ملفات JavaScript الـ15 — ملفًا ملفًا ومقطعًا مقطعًا

**التاريخ:** 8 نوفمبر 2026
**النطاق:** 15 ملفًا رفعها المستخدم؛ 13 ملفًا فريدًا محفوظًا كاملًا في [أرشيف المصادر](../../../research/user-supplied/2026-11-08/). ثلاث شيفرات جديدة في سجل التحليل؛ 12 نسخة مكررة من ملفات سبق تدقيقها.
**المنهج:** قراءة ثابتة، بصمات SHA-256 وGit blob، ومطابقة الحزمة الرئيسية القديمة لتفسير دوال الـstore. لا تشغيل JS حكومي ولا استدعاءات API الحية.
**ملاحظة «سطر سطر»:** معظم ملفات الإنتاج Minified، وقد يحوي السطر المادي الواحد مئات التعليمات. لذلك ربطنا الدوال والأقسام والطلبات بمواقعها الدقيقة في [SOURCE_ANCHORS.json](SOURCE_ANCHORS.json)، ولا نختلق أرقام أسطر غير موجودة.

## جدول الملفات الخمسة عشر

| # | ملف الرفع | الوظيفة | حالة المقارنة |
|---|---|---|---|
| 1 | browser-3Qg8aFGH(1).js | توليد QR إلى Canvas/Data URL | مطابق للتحليل السابق |
| 2 | CompanyOwnerView-CIdFF3LL(4).js | صاحب الشركة، الشحن، إعادة وثيقة | مطابق |
| 3 | **IndexPage-cUNA67sR.js** | **لوحة الأداء والإحصاءات** | **جديد** |
| 4 | Modal-C_od4hhs(1).js | إدارة Dialog، focus وARIA | مطابق |
| 5 | index-BKvq_4_A(1).js | تصوير DOM وتصدير Blob/PNG | مطابق |
| 6 | jsQR-CKtgBSaS(1).js | فك QR من صورة/مصفوفة بكسلات | مطابق |
| 7 | **CompanyOwnerCeoLoadsView-Coghn9Xh.js** | **سجل حمولات صاحب الشركة والطباعة** | **جديد** |
| 8 | FormField-DW4k76E2(1).js | الحقول والأخطاء ووصفها | مطابق |
| 9 | Modal-C_od4hhs(2).js | نسخة أخرى من #4 | مطابق تمامًا |
| 10 | **useFormControl-XQpg82Ny.js** | **التحقق من وجود عنصر داخل form** | **جديد** |
| 11 | QrLocalImporter-DYzNB5Fh(3).js | ماسح المستورد المرتبط بـuseExitGate | مطابق |
| 12 | index-BKvq_4_A(2).js | نسخة أخرى من #5 | مطابق تمامًا |
| 13 | useAttachments-YD2hRx7D(1).js | تنزيل مرفقات المحطات عبر Blob | مطابق |
| 14 | Select-DZpjzzNJ(1).js | اختيار مفرد/متعدد وعناصر نموذج | مطابق |
| 15 | StationsDetailsModal.vue_vue_type_script_setup_true_lang-CppuJXhm(1).js | تفاصيل المحطات ومرفقاتها | مطابق |

جميع الأسماء الأصلية والأحجام والبصمات في [manifest.json](manifest.json). توجد نسخة فريدة واحدة لكل محتوى أصلي، بدل تكرار الملفات التي أضيفت إليها لاحقات رقمية عند التنزيل.

## تحليل IndexPage-cUNA67sR.js — 28,700 بايت / سطر إنتاجي واحد

**هذا الملف لوحة مؤشرات أداء، وليس قارئ QR أو أداة إصدار وثائق.** يبدأ باستيراد دوال Vue/Pinia وعميل Axios مشترك وAppPagination، ويعرّف أربع وحدات واجهة: dashboard store، KpiCard، ChartSection، DateRangeFilter، ثم مكوّن IndexPage الأساسي.

### تتبع الدوال في ترتيب المصدر

| موضع الفهرس | الجزء | كيف يعمل |
|---|---|---|
| I-01 | dashboard state | يضع kpiOverview=null، employeePerformance=[]، vehicleStay=null، dateRange وتفاصيل التحميل |
| I-02 | fetchKpiOverview | POST metrics/kpi بمدى التاريخ، يخزن بيانات الاستجابة ويحدد lastUpdated |
| I-03 | fetchEmployeePerformance | POST metrics/kpi/processing_times_by_employee؛ يتوقع data مصفوفة |
| I-04 | fetchVehicleStay | POST metrics/kpi/vehicle_stay_duration مع page وper_page ومرشحات التاريخ |
| I-05 | fetchAllMetrics | يستدعي الثلاثة بصورة متوازية عبر Promise.all |
| I-06/I-07 | updateDateRange / resetFilters | تغيير الفترة ثم إعادة الجلب |
| I-08/I-10 | getters وchart transforms | معدل الاستجابة، متوسط الأداء، إحصاءات المركبات، مخططات المنافذ والمراحل |
| I-11/I-12 | KpiCard / ChartSection | عرض القيم، التحميل، الأخطاء المرئية والحالة الفارغة والرسوم |
| I-13/I-14 | DateRangeFilter | اليوم، آخر 7/30 يومًا، الشهر الحالي/السابق، وتحويل التاريخ إلى نص |
| I-15–I-22 | IndexPage | إظهار واجهات الأدوار، الجلب عند التركيب، تحديث كل 300000ms، جدول المركبات وصفحاته |

**واجهات API في هذا الملف:**

- POST local API path: metrics/kpi
- POST local API path: metrics/kpi/processing_times_by_employee
- POST local API path: metrics/kpi/vehicle_stay_duration

هذا المكوّن يعرض إجمالي الطلبات، المرسل/المجاب من كردستان، المنافذ، مراحل الطلب، سرعة معالجة الموظفين، وفترة بقاء المركبات. بعض الأقسام مشروطة بقيم user_privileges مثل tir_report_view، والصفحة الأساسية بقيم user_permissions مثل tracking أو tir_view. **فحص العرض لا يثبت تفويض الخادم**.

**نتائج مهمة من الشيفرة:**
1. تحويل datepicker إلى YYYY-MM-DD باستخدام toISOString() يحوّل اليوم المحلي إلى UTC؛ يمكن أن ينتج تاريخ اليوم السابق في بعض المناطق الزمنية.
2. نافذة «آخر 7 أيام» تُنشأ من تاريخ اليوم ناقص سبعة أيام؛ قد تضم ثمانية تواريخ إذا اعتبر الخادم التاريخين شاملين.
3. fetchAllMetrics متوازٍ، وتغيير الفترة بسرعة بلا إلغاء لنتائج الطلبات الأقدم قد يخلط بيانات الفترات؛ هذه فرضية تحتاج اختبارًا اصطناعيًا.
4. يوجد جلب عند تركيب الصفحة وجدولة تحديث كل 5 دقائق بغض النظر عن نتيجة شرط إظهار المحتوى في JSX. يجب فرض صلاحيات metrics على الخادم.
5. getter criticalVehicles يعتمد على vehicleStay.data.filter عند وجود vehicleStay، لكنه لا يتحقق من أن data مصفوفة؛ هذا خطر مشروط عند استدعائه، وليس دليل انهيار حالي.
6. بعض نسب الرسوم تستعمل percent || fallback، فتُعامَل نسبة 0 الصحيحة كقيمة مفقودة.
7. averageProcessingTime يحسب المتوسط الحسابي لمتوسطات الموظفين، لا المتوسط المرجح بعدد طلبات كل موظف؛ يختلف معنى المقياس.
8. ربط عدد المركبات بـpagination.* وقراءة stay_duration_days.toFixed(1) يفترض عقد استجابة بأرقام وتصفح صحيحة.

**المطلوب لتحسين تطبيق تملكه:** DTO لكل استجابة، تثبيت معنى التقويم والمنطقة الزمنية، ضبط صلاحيات API على الخادم، منع نتائج الطلبات القديمة، وتوحيد حالات التحميل والخطأ.

## تحليل CompanyOwnerCeoLoadsView-Coghn9Xh.js — 20,697 بايت / سطر إنتاجي واحد

يُنشئ **ثلاثة مكونات Vue**: CompanyOwnerCeoLoadDetailModal، وCompanyOwnerCeoLoads، وCompanyOwnerCeoLoadsView. لا يوجد POST في هذا الملف نفسه؛ فهو يستدعي دوال store موجودة في الحزمة الرئيسية التي سبق رفعها وفحصها.

### تتبع التدفق بدقة

1. C-14/C-15: CompanyOwnerCeoLoadsView يقرأ حالة صاحب الشركة ويستدعي checkUserAuthentication ثم يعيد التوجيه إلى CompanyOwner عند غياب جلسة العميل.
2. C-07: CompanyOwnerCeoLoads يهيئ صفحة البداية والصفحات المتاحة وحجم الصفحة والمرشحات والقائمة.
3. C-08/C-09/C-10/C-11: يبني searchdata من driver_name وvehicle_number وcheckpoint_name_control وdoc_number مع تواريخ بداية/نهاية.
4. C-12: يستدعي store.fetchCompanyCeoLoads(page, perPage, filters, startDate, endDate).
5. من الحزمة الرئيسية: store يرسل POST local_form/paginate_company_ceo ببيانات sort_by="checkpoint_time_stamp" وsort_dir="desc"، وAuthorization لتوكن صاحب الشركة.
6. C-01: نافذة التفاصيل تعرض اسم الشركة، السائق، المركبة، السيطرة، إجازة المصنع، الموقع، الملاحظات وبيانات أخرى.
7. C-05: عند الضغط على الطباعة تُمرر قيمة doc_number ونوع الشركة company_type.
8. C-13: store.returnDocCeo يستدعي POST local_form/return_doc_ceo بجسم يحوي doc_number وcompany_type إذا توفر.
9. C-18: الاستجابة تُعرض داخل ShipmentDoc في نافذة طباعة.
10. C-16: AppPagination يرسل حدث تغيير الصفحة/الحجم، ثم يتكرر جلب القائمة.

**النقطة الأساسية:** paginate_company_ceo لجلب **قائمة حمولات**، وreturn_doc_ceo لجلب **تفاصيل وثيقة قابلة للطباعة**. لا نستنتج من اسميهما كيفية إصدار QR المشفّر في الخادم أو إنشاء سجل جديد.

### نتائج التدقيق

- **CEO-01:** حقل doc_number يحاول Number(value) عند البحث؛ الأرقام ذات الأصفار الأولى قد تفقد الأصفار، والأرقام الطويلة تتجاوز دقة Number الآمنة.
- **CEO-02:** new Date(invalid).toLocaleDateString("ar-IQ") قد يعطي Invalid Date دون رمي استثناء؛ catch ليس ضمانًا للعرض الصحيح.
- **CEO-03:** رابط الخرائط يبنى من إحداثيات الحمل مباشرة دون تحقق محلي من المدى الرقمي؛ مشاركة الموقع مع Google تحدث فقط عند الضغط.
- **CEO-04:** تنسيق الهاتف يضع +964 تلقائيًا، وقد يكرر رمز الدولة إذا جاءت القيمة من API دولية أصلًا.
- **CEO-05:** حالة checkpoint_is_active تُعتبر نشطة ما لم تساوِ false حرفيًا؛ القيمة غير المعروفة قد تعرض «نشطة».
- **CEO-06:** store يعين companyOwnerCeoLoads من data.data أو data دون تحقق مصفوفة واضح؛ يلزم توافق Schema.
- **CEO-07:** مسار /company-owner/ceo-loads في Router يحمل requiresAuth:false، لكن المكوّن يفحص الجلسة بعد التحميل. التفويض الفعلي يجب أن يطبقه خادم البيانات.
- **CEO-08:** لا يثبت عرض ShipmentDoc أو نجاح HTTP أن المستند وقّعه الخادم.
- **CEO-09:** التصفح يعتمد على AppPagination غير المرفق، لذا يلزم التأكد من توقيع الحدث page/per_page.
- **CEO-10:** استجابات تصفية متزامنة بلا تمييز أحدث طلب قد تعيد عرض نتائج أقدم؛ يلزم اختبار محلي.

**الملاحظات الإيجابية:** فصل عرض القائمة عن تفصيل الحمولة وعن طلب الطباعة؛ دعم مرشحات متعددة؛ معالجة للخطأ في Promise؛ إغلاق الحوارات وإعادة ضبط الفلاتر.

## تحليل useFormControl-XQpg82Ny.js — 132 بايت / سطر واحد

هذا الملف صغير، ويمكن تفكيك نصه دون إخفاء أي منطق:

\`\`\`javascript
import{c as e,bL as r,bM as t}from"./index-gleMzSil.js";
function n(o){return e(()=>r(o)?!!t(o)?.closest("form"):!0)}
export{n as u};
\`\`\`

- **import:** إحضار computed ودوال مساعدة من حزمة Vue المشتركة.
- **function n(o):** تعيد قيمة محسوبة تستجيب لحالة المرجع.
- **الشرط:** إذا كانت r(o) صحيحة، تفحص ما إذا كان العنصر الناتج من t(o) يوجد داخل أقرب عنصر HTML من نوع form بواسطة closest("form")؛ وإلا تعيد true.
- **export:** توفّر الوظيفة بالاسم المصغّر u، وتستهلكها حزمة Select.
- **الأثر:** يقرر سلوك دمج عنصر الاختيار في نموذج HTML؛ لا يصادق على مستخدم ولا يفحص مستندًا.

## الملفات المطابقة السابقة — لا تغييرات مصدرية

**browser-3Qg8aFGH(1):** مكتبة توليد QR؛ تنشئ مصفوفة QR ورسم Canvas أو Data URL. لا توقع QR رسميًا، ولا تكتشف الكاميرا.

**CompanyOwnerView-CIdFF3LL(4):** AppUrLogin وCompanyOwnerView وVSearchHashCode وCompanyOwnerItems. تشمل وظائف البحث بالشركة والشحن عبر company_item_reduce وإعادة الوثيقة عبر return_company_doc. هذه النسخة مطابقة لما سبق، والطلب يحتوي المفتاح vihcle_info بهذه الصيغة.

**Modal-C_od4hhs(1) و(2):** مكتبة Dialog بخصائص focus trapping وEscape وARIA وإدارة الحالة. نسختان متطابقتان داخل هذه الدفعة؛ لا تطبّقان شروط قرار بوابة الدخول.

**index-BKvq_4_A(1) و(2):** مكتبة تحويل DOM إلى SVG/Canvas ثم PNG/Blob مع تحميل خط وصور؛ قد يتأثر الإخراج بحظر CORS. النسختان متطابقتان ولا تنشئان PDF حكوميًا.

**jsQR-CKtgBSaS(1):** فك صورة QR وتحليل BitMatrix وReed–Solomon؛ يخرج data/location، وليس توقيعًا أو شهادة ثقة.

**FormField-DW4k76E2(1):** يعرض Label وHint وError وRequired عبر سياق Vue. التحقق النهائي يقع على الخادم عند التعامل مع معاملات.

**QrLocalImporter-DYzNB5Fh(3):** قارئ QR للمستورد، BarcodeDetector أو jsQR ثم useExitGate.searchImportedGoods، الذي يرسل read_qr_exitgate. لا يختزل الصورة إلى PDF.

**useAttachments-YD2hRx7D(1):** GET carrier_register/download_file مع hash_id وurl وstation_name؛ يحول Blob إلى ملف في المتصفح. الخادم يجب أن يقيّد ملكية المسار والمرفق.

**Select-DZpjzzNJ(1):** Select متعدد/فردي مع modelValue والتحقق من الحقل والكيبورد؛ يستورد useFormControl الجديد الذي فحصناه في هذه الدفعة.

**StationsDetailsModal... (1):** يعرض sections وattachmentsEntrance وattachmentsSonography ويصدر حدث download-file. الأب EntranceGateView يمرر أيضًا attachments-register ولكن الابن لا يعرضها في هذا الإصدار.

## خريطة العلاقات النهائية

\`\`\`text
IndexPage --> dashboard Pinia --> metrics/kpi
                           --> metrics/kpi/processing_times_by_employee
                           --> metrics/kpi/vehicle_stay_duration

CompanyOwnerView --> company_item_reduce --> ShipmentDoc --> browser QR generator
CompanyOwnerCeoLoadsView --> fetchCompanyCeoLoads --> paginate_company_ceo
                         --> returnDocCeo --> return_doc_ceo --> ShipmentDoc

EntranceGateView --> jsQR --> scrape_search_goods_gateway_register
                --> StationsDetailsModal --> useAttachments --> download_file
QrLocalImporter --> jsQR/BarcodeDetector --> useExitGate --> read_qr_exitgate

Modal / Select / FormField / useFormControl --> واجهة الحقول والنماذج
index-BKvq_4_A --> DOM screenshot / PNG Blob
\`\`\`

## ما يزال ناقصًا

- AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5.js (الصفحات في لوحة المؤشرات وسجل الحمولات).
- BaseModal-DjCaQzje.js (النافذة المستخدَمة في تفاصيل المحطات).
- index-ccmhdhtn.js (البناء البديل لبوابة صاحب الشركة).
- Input-XMNBc09N.js وTextarea-vxo1mVYX.js (تفاصيل الحقول).
- مواصفات Backend أو Mock مملوك لاختبار DTO والصلاحيات وإلغاء الطلبات ومنع التكرار.

**حد الإثبات:** كل النتائج عن Frontend ثابت. لا نقول إن الخادم يقبل قرارات دون تفويض، أو أن QR موقّع، أو أنه يمكن استخدام كود الواجهة لإصدار وثائق رسمية.
