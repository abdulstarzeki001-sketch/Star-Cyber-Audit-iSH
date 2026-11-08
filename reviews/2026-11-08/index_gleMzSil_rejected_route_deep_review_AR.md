# تدقيق الحزمة الرئيسية index-gleMzSil — كشف مسار الوثائق المرفوضة

**تاريخ التدقيق:** 8 نوفمبر 2026. **المصدر:** `index-gleMzSil(1)(1).js` الذي أرسله المستخدم. **الحجم:** 1,416,085 بايت. **SHA-256:** `83d3f35e2cf05cc56fca81a3531b98381d291dc1e903957be7b6e433466b7ac3`.

هذا **تحليل ثابت للمتصفح**. لم تنفذ شيفرة المنصة، ولم ترسل طلبات إلى خوادم الحكومة، ولم تستخدم بيانات معاملات أو رموز جلسات. لا تُنشر نسخة جديدة من ملف الحكومة في المستودع العام.

## 1. المسار الحقيقي لسجلات الرفض — محسوم

وجدنا التعريف الوحيد للدالة `fetchRejectedLocalReaders(t={})` في وحدة الحالة الرئيسية. وهي تُرسل:

```http
POST https://customs-uboor.ur.gov.iq/api/local_form/pagination_rejected_qrcode_reader
```

يجري تكوين عنوان URL من `baseURL` الخاص بـAxios `tt`: `https://customs-uboor.ur.gov.iq/api/`، واسم endpoint النسبي `local_form/pagination_rejected_qrcode_reader`. **هذا دليل على تكوين العميل، وليس اختبار اتصال ناجح بالخادم**.

تعد الدالة جسم الطلب بالصفحة والحجم الافتراضيين `page=1` و`per_page=10`، والفرز `sort_by:"id"` و`sort_dir:"desc"`. وتقبل اختياريًا `searchdata`، أو تحول `searchQuery` مع `searchFields` إلى قائمة محددات؛ في غياب الحقول قد ترسل `search`. كما تدعم `start_date` و`end_date`.

### نموذج تركيب بيانات للاختبارات فقط

```json
{
  "page": 1,
  "per_page": 10,
  "sort_by": "id",
  "sort_dir": "desc",
  "searchdata": [{"doc_number": "SYNTHETIC"}],
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}
```

لا يمثل المثال مستندًا حكوميًا أو طلبًا مرسلًا فعليًا.

## 2. خريطة الربط مع RejectedLocalDocuments

```text
/dashboard/qr/local-rejected
  └─ RejectedLocalDocuments-CC07EpF_.js
       ├─ fetchRejectedLocalReaders(filters)
       │    └─ POST /api/local_form/pagination_rejected_qrcode_reader
       │         └─ response.data + pagination -> table
       └─ preview(row)
            └─ POST /api/local_form/return_doc_qrcode
                 ├─ QR preview -> qrStore
                 ├─ sessionStorage["qr_preview_entry"]
                 └─ QRDocument view
```

هذه الشاشة **تعرض سجلات رفض** ولا تتضمن أمرًا مباشرًا لرفض أو تعطيل الوثيقة. أمر `local_form/reset_company_qrcode` يوجد في `DisableDocument`، وهو مسار وظيفي مختلف. و`QRReadings` و`QrControlScan` يستخدمان مسارات سجل قراءات أخرى. لا دليل من frontend وحده على اشتراك هذه المسارات في جدول قاعدة بيانات واحد.

## 3. حماية المسار والمصادقة

- `RejectedLocalDocuments` مسار فرعي داخل `/dashboard`، والأب يحمل `meta.requiresAuth:true`؛ يرث الطفل شرط المصادقة من تعريف الأب.
- `Qr.beforeEach` يفحص `isAuthenticated`، و`usisfirstlogin`، و`to.meta.requiresAuth`. **الحارس الظاهر لا يفحص امتيازًا خاصًا بفتح سجل الرفض**.
- يُحمّل مخزن المستخدم بيانات `user` و`token` و`user_permissions` و`user_privileges` من `localStorage["auth"]`، ونسخة Axios تضيف ترويسة Bearer عند توافر التوكن.
- معالج استجابة Axios يعرض رسالة لرمز HTTP 403، ويسجل خروج المستخدم عند HTTP 401. **هذا لا يثبت صحة التفويض الخادمي أو إمكان تجاوزه**. اختبار ذلك لا يتم على الإنتاج دون تخويل صريح.

## 4. نتائج سلامة الاستجابة والبيانات

عند رجوع `success:false` أو `error` في JSON، تعرض `fetchRejectedLocalReaders` رسالة خطأ، لكنها بعد ذلك **تُرجع بيانات الاستجابة** إلى المستدعي، ولا توقف المسار. في مكوّن `RejectedLocalDocuments` السابق، ينفذ العميل `n=t.data||[];w.value=n.map(...)` دون التحقق من أن `data` مصفوفة.

**النتائج المحتملة:** قد يواصل التطبيق معالجة بيانات رغم وجود فشل منطقي، أو يتعرض لخطأ عرض إذا كان `data` كائنًا، وقد تظل نتائج قديمة ظاهرة عند فشل الجلب. هذه أخطاء محتملة في التكامل، لا إثبات لرد معين صادر من الخادم.

## 5. تنظيف جلسة Axios

- عند الدخول أو `loadAuth` يمكن ضبط `tt.defaults.headers.common.Authorization`.
- في `logout()`، تُصفّر حالة المستخدم ويُحذف `localStorage["auth"]`.
- **لا يظهر في مسار الخروج حذف صريح لترويسة Authorization الافتراضية**، كما لا يمسحها `loadAuth` في فرع عدم وجود جلسة.
- طلبات Axios اللاحقة تضيف ترويسة من `nu().token` إذا كان حاضرًا، لكنها لا تزيل بالضرورة القيمة القديمة في defaults إذا كان غائبًا.

**الاستنتاج المشروط:** بعد تسجيل الخروج، قد يبقى Bearer قديم في نسخة Axios الحية حتى يتغير أو يعاد تحميل الصفحة. لا يوجد هنا إثبات لتسرب بيانات مستخدم أو استعمال حساب آخر. التوصية لمشروع تملكه هي تجنب تخزين Authorization بشكل مشترك طويل العمر، أو حذفها صراحة عند الخروج.

## 6. ملف صفحة طباعة الشهادة الصحية — الاسم محسوم

تعريف المسار في الحزمة:

```text
path: health-certificates/print
name: HealthCertificatePrint
asset: PrintHealthCertificateView-Q9yNncqz.js
```

الرابط الظاهر في استيراد العميل:
`https://customs-uboor.ur.gov.iq/assets/PrintHealthCertificateView-Q9yNncqz.js`.

هذا هو **اسم الملف الصحيح** الذي نحتاجه لفحص مصدر `hc_print` المخصص للطباعة، دون التخمين بـHash غير مؤكد. لم يتم جلب الملف من الإنترنت للتحقق من إتاحته الآن.

## 7. فهرس مؤشرات التدقيق الـ15

| المعرّف | الاكتشاف | درجة المراجعة |
|---|---|---|
| IR-01 | تحديد API لقائمة الرفض | مؤكد |
| IR-02 | page / per_page / sort_by / sort_dir | مؤكد |
| IR-03 | دعم مرشحات البحث | مؤكد |
| IR-04 | نطاق التاريخ | مؤكد |
| IR-05 | إظهار الخطأ ثم إرجاع الرد | **اعتمادية / متوسطة** |
| IR-06 | وراثة requiresAuth من /dashboard | مؤكد |
| IR-07 | تثبيت مسار RejectedLocalDocuments | مؤكد |
| IR-08 | حارس Router يفحص المصادقة | مؤكد |
| IR-09 | لا فحص امتياز محدد داخل حارس Router الظاهر | مراجعة التفويض |
| IR-10 | تعيين عنوان Axios الأساسي | مؤكد |
| IR-11 | إرفاق Bearer من حالة المستخدم | مؤكد |
| IR-12 | التعامل مع HTTP 403 في الواجهة | مؤكد |
| IR-13 | عدم تصفير Authorization الافتراضية صراحة عند الخروج | **جلسات / متوسطة** |
| IR-14 | تحليل JSON المخزن محليًا دون معالج فساد ظاهر | منخفضة |
| IR-15 | اكتشاف اسم مكوّن طباعة الشهادة | مؤكد |

**المؤشرات الـ15 ليست 15 ثغرة أو نتائج خادم**. معظمها تثبيت حقائق معمارية؛ والباقي ملاحظات اعتمادية/جلسات تخضع للظروف.

## 8. طريقة تشغيل المراجع دون شبكة

```sh
python3 tools/ish/index_rejected_route_review.py "/path/to/index-gleMzSil(1)(1).js"
python3 -m unittest discover -s tests -p 'test_index_rejected_route_review.py' -v
```

الأداة لا تنفّذ JavaScript ولا تتصل بموقع عبور، وتخرج JSON بأسماء المؤشرات والمسارات وبصمة SHA-256 فقط؛ لا تحفظ رموز جلسات أو محتوى معاملات. أضيفت **14 اختبارًا اصطناعيًا** لتثبيت هذه الأنماط ومنع اعتبار غياب تحقق في الواجهة دليلًا على غياب التفويض الخادمي.

## 9. ملفات المراجعة التالية

1. `PrintHealthCertificateView-Q9yNncqz.js` — كيف تستخدم صفحة الطباعة بيانات `hc_print`.
2. `QRDocument-BJwpoEJY.js` — كيف تفسر الشاشة رد `return_doc_qrcode` وخيارات `autoPrint/autoDownload`. يوجد أرشيف سابق للملف.
3. توثيق عقد API رسمي أو مخول (إن توفر) — للتحقق من معنى `success` ونوع `data` والتفويض، وليس لتنفيذ تجارب على الإنتاج.

**حد الإثبات:** لا تحتوي هذه النتائج على أدلة على تجاوز صلاحيات، أو تعطيل وثيقة، أو مفاتيح التوقيع الحكومي.
