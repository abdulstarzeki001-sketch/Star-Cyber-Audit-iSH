# تحليل RejectedLocalDocuments — سجل الوثائق المحلية المرفوضة

**التاريخ:** 8 نوفمبر 2026  
**الملف:** `RejectedLocalDocuments-CC07EpF_.js`  
**الحجم:** 11,186 بايت  
**SHA-256:** `b98b04782e1ee00c7e338bd111e22a45479db6e5171e5a67e808a3458a9c7a25`  
**نطاق الفحص:** مراجعة ساكنة لملف JavaScript المرفق؛ لم يُنفذ أي طلب إلى خادم عبور ولم تُستعمل بيانات معاملات أو جلسات حقيقية. المشروع المستهدف بالتحديث مستودع **Star-Cyber-Audit-iSH**، وليس منصة عبور.

## 1. الوظيفة الأساسية

المكوّن الداخلي `RejectedLocalDocuments` يعرض **«الوثائق المرفوضة (منتج محلي)»**. وظيفته جلب قائمة سجلات الرفض، وإتاحة بحث متعدد الحقول ونطاق تواريخ وتقسيم صفحات، وعرض رقم الوثيقة وموظف القراءة وجهته وهاتفه ووقته ونوعه وموقعه وسبب الرفض، ثم زر معاينة الوثيقة.

**الملف لا يتضمن طلبًا مباشرًا لرفض وثيقة أو إعادة ضبطها أو حذفها.** جلب قائمة السجلات يمر عبر دالة `fetchRejectedLocalReaders` من مخزن/وحدة مستوردة من `index-gleMzSil.js`. **اسم مسار API الحقيقي لجلب القائمة غير ظاهر في هذا الملف** ولا يجوز افتراضه من اسم الدالة. الطلب المباشر الوحيد المثبت هنا هو `POST local_form/return_doc_qrcode`، ويُستخدم للمعاينة.

## 2. كيف يرتبط بمسار QR الموجود في المشروع

```text
RejectedLocalDocuments (Vue view)
   ├─ fetchRejectedLocalReaders(search, dates, pagination)
   │     └─ shared module imported from index-gleMzSil.js
   │          └─ actual list API endpoint UNKNOWN from this file alone
   ├─ table: rejected local document reading records
   │     └─ optional Google Maps link for x_coordinate/y_coordinate
   └─ preview(row)
         └─ POST local_form/return_doc_qrcode
              ├─ doc_number:Number(...)
              ├─ qrStore.add(local preview entry)
              ├─ sessionStorage["qr_preview_entry"]
              └─ QRDocument route with autoPrint/autoDownload request

QrControlScan / QRReadings (reviews in this repository)
   └─ same document preview API, but different reader-list APIs

DisableDocument (previous review)
   └─ POST local_form/reset_company_qrcode
      distinct workflow; NOT called by RejectedLocalDocuments
```

يفترض مسار المعاينة أن `QRDocument` يقبل سجل المعاينة عبر حالة التوجيه أو المخزن. راجع ملف `QRDocument-BJwpoEJY.js` لتحديد ما إذا كانت `autoPrint` و`autoDownload` تُنفذان فعلًا، لأن هذه الوحدة **تطلبهما** فقط.

## 3. الحقول والبحث

خمسة حقول بحث متاحة بالواجهة: `doc_reader_name`، `doc_reader_org_name`، `doc_reader_phone`، `time_stamp`، `doc_number`. عند اختيار الوقت يظهر حقلا تاريخ **من/إلى**. يحمل `fetchRejectedLocalReaders` معلمات `searchdata` أو `searchQuery/searchFields` وكذلك `start_date/end_date`، ويتعامل مع الصفحة والحجم عبر `AppPagination`.

أعمدة الجدول **تسعة**: التسلسل، رقم الوثيقة، الموظف، الجهة/الهاتف، الوقت، النوع، الموقع، سبب الرفض، المعاينة. لكن صف «لا توجد بيانات» يحمل `colspan="8"`.

تفاصيل صف القراءة تأتي من `data` مع بدائل: `doc_number??doc_id`، و`reader_name` من حقول مختلفة، و`rejection_reason??reason??notes`. هذا الأخير **لا يثبت** أن كل `notes` تمثل سبب رفض رسميًا.

## 4. النتائج ذات الأولوية

| ID | مستوى المراجعة | دليل الواجهة | أثر محتمل |
|---|---|---|---|
| RL-01 | معماري | القائمة عبر `fetchRejectedLocalReaders` لا عبر API مباشر | يجب فحص تعريف الدالة لتحديد المسار والصلاحيات وبنية البيانات الحقيقية |
| RL-02 | متوسط | `n=t.data||[];w.value=n.map(...)` بلا فحص مصفوفة | خطأ عرض إذا كان `data` كائنًا؛ لا نستنتج شكل رد الخادم الحقيقي |
| RL-03 | متوسط | `catch` يطبع فشل `loadPage` دون مسح `w.value` | استمرار عرض صفوف قديمة بعد خطأ شبكة أو API |
| RL-04 | مراجعة تفويض | زر «معاينة الوثيقة» موجود مباشرة في الجدول دون شرط `user_privileges` **داخل هذا الملف** | يلزم توثيق تفويض الخادم وحماية المسار؛ هذا لا يعني وصولًا غير مخول |
| RL-05 | متوسط | `doc_number:Number(t)` في طلب المعاينة | احتمال فقد صفر أولي، أو فقد دقة عدد كبير، أو إرسال null من NaN |
| RL-06 | منخفض | إضافة `company_type` فقط إذا كانت truthy | القيمة الرقمية 0 قد تُحذف إن كانت مسموحة في العقد |
| RL-07 | متوسط / خصوصية | تسجيل `raw.response` في `qrStore` و`sessionStorage` | تخزين محتوى وثائق محليًا؛ قلل البيانات وحدد مدة احتفاظ |
| RL-08 | مراجعة تجربة استخدام | طلب `autoPrint:true` و`autoDownload:true` في حالة التوجيه | احتمال طباعة/تنزيل غير مقصود إذا احترمت الشاشة المستقبلة العلمين |
| RL-09 | مراجعة خصوصية الموقع | رابط `https://www.google.com/maps?q=...` يضم الإحداثيات | عند فتح الرابط تُرسل الإحداثيات إلى Google؛ يقتضي سياسة واضحة للخصوصية |
| RL-10 | منخفض | `x_coordinate&&y_coordinate` لإظهار الخريطة | إحداثي 0 الصحيح سيُعدّ غير متوفر؛ لا يوجد في هذا المكوّن تحقق من المدى |
| RL-11 | مراجعة خصوصية | رقم هاتف القارئ معروض `u(a.phone)` | ضرورة تحديد من يحق له رؤية الرقم |
| RL-12 | متوسط دلالي | `rejection_reason??reason??notes` | قد يُعرض نص ملاحظة عامة تحت عنوان «سبب الرفض» |
| RL-13 | منخفض | `colspan="8"` للجدول ذي الأعمدة التسعة | اختلال عرض حالة القائمة الفارغة |
| RL-14 | متوسط | يؤخذ رد `return_doc_qrcode` ويُخزن دون فحص صريح لـ`success:false` | احتمال معاينة/تخزين رد منطقي فاشل بحالة HTTP 200 |
| RL-15 | متوسط / شرطي | `async loadPage` يحدث `w.value` فور عودة كل طلب بلا معرّف تسلسل ظاهر | إذا تداخل بحثان قد تطغى استجابة قديمة على نتائج أحدث؛ يلزم اختبار محلي |
| RL-16 | منخفض | خطأ المعاينة في `catch` يُطبع في Console فقط | المستخدم قد لا يعرف لماذا لم تُفتح الوثيقة |

هذه **16 إشارة مراجعة/تحليل**، وليست 16 ثغرة في الخادم أو تقييم CVSS. بعض النتائج UI أو صحة بيانات، وبعضها مشروط بعقد API أو المكوّن المستقبِل. غياب شرط في هذه الوحدة لا يستبعد وجود حماية في Router أو backend.

## 5. فوارق مهمة عن الملفات السابقة

- **RejectedLocalDocuments:** عرض سجلات الرفض، مع استرجاع قائمة من مخزن عام، ومعاينة عبر `return_doc_qrcode`.
- **QrControlScan:** سجل قراءات المنتج المحلي من `paginate_qrcode_reader2` عن طريق `useLocalCompany`، مع صلاحية معاينة UI.
- **QRReadings:** سجل قراءات آخر من `pagination_qrcode_reader`، مع معاينة مشتركة.
- **DisableDocument:** شاشة أخرى ترسل طلبًا ذا أثر محتمل إلى `reset_company_qrcode`؛ هذا الإجراء غير موجود في RejectedLocalDocuments.
- **QRHealthCertificate:** قراءة شهادة صحية عبر `BorderPort_HS/read_doc_health`، وهي دورة بيانات مستقلة.

**العلاقة المثبتة** هي مشاركة معرّفات الوثائق وواجهة المعاينة والمكونات المشتركة، لا أن كل الشاشات تتعامل مع جدول قاعدة البيانات نفسه أو صلاحيات موحدة.

## 6. توصيات إصلاح إذا كان المشروع مملوكًا لك

1. راجع تنفيذ `fetchRejectedLocalReaders` لتثبيت الـAPI وشكل `data` والتفويض، دون اختبار إنتاج غير مخوّل.
2. أعطِ الشاشة حالة `idle/loading/success/empty/error`، وامسح النتائج القديمة أو ضع عليها تحذيرًا عند فشل التحديث.
3. حافظ على نوع `doc_number` المتفق عليه مع API، وتحقق من النص/المدى بدل `Number` غير المشروط.
4. لا تنفّذ المعاينة أو التخزين إلا بعد التحقق من نجاح رد API ومن صلاحية بيانات الوثيقة.
5. افصل المعاينة عن الطباعة التلقائية، ولا تخزّن ردودًا حساسة طويلًا في المتصفح.
6. استعمل تحققًا رقميًا لإحداثيات الخريطة وعالج القيمة صفرًا؛ واحصل على سياسة موافقة/خصوصية قبل إرسال المكان إلى خدمة طرف ثالث.
7. صحح `colspan` إلى 9، ووحد مصدر «سبب الرفض» مع حالة الوثيقة المثبتة.
8. أضف اختبارات صناعية لحالات التزامن وفشل الطلب وحجب المعاينة؛ مع بقاء صلاحيات الخادم ضمن نطاق اختبار مصرح به.

## 7. تشغيل الفحص المحلي

```sh
python3 tools/ish/rejected_local_documents_review.py \
  "/path/to/RejectedLocalDocuments-CC07EpF_.js"

python3 -m unittest discover -s tests \
  -p 'test_rejected_local_documents_review.py' -v
```

لا ينفّذ الفاحص JavaScript ولا يجري اتصالات بالشبكة، ويعيد بصمة الملف ومؤشرات نصية فقط.

## 8. الملف التالي المطلوب

لتحديد **المسار الحقيقي لقائمة الوثائق المرفوضة** نحتاج تعريف `fetchRejectedLocalReaders` داخل `index-gleMzSil.js`، أو وحدة store الفعلية إن كان التعريف مستوردًا. ولتحديد نتائج الطباعة/التنزيل نحتاج دراسة `QRDocument-BJwpoEJY.js`.

**الحد النهائي:** لم تُفحص خوادم عبور أو بيانات مستخدمين حقيقية، ولا يمكن الجزم بأي تجاوز صلاحيات أو تعديل في وثائق رسمية من هذه الحزمة.
