# تدقيق معمّق: useHealthCertificate — دورة بيانات الشهادات الصحية

**تاريخ المراجعة:** 8 نوفمبر 2026  
**المصدر:** ملف JavaScript رفعه المستخدم: `useHealthCertificate-DVL2cDcP.js`  
**الحجم:** 17,870 بايت  
**SHA-256:** `36acf66c8a1ad736f6da9bca1d8a9dced9f1bf377451c8913dcf4ddc15eff479`  
**نوع الاختبار:** تحليل ثابت لشيفرة واجهة Vue/Vite؛ **لا توجد أي طلبات إلى خادم حكومي أو جلسات دخول أو اختبار صلاحيات**. لا يعاد نشر المصدر الخارجي مع هذا التقرير.

## 1. الدور في مشروع UBOOR

هذه وحدة منطق مشتركة (composable)، اسمها الداخلي `Oe`، وتصدر دوال الاستخدام `Oe as a` و`De as u`؛ تنشئ حالة مشتركة عند أول استخدام عبر `let T=null`. تسند لوائح الشهادات الصحية ومعلومات الجغرافيا الإدارية والجهات، وتوفّر جلب وثيقة وسجل قراءات ومعاينة وتصدير Excel وإنشاء شهادة ورفع مرفق.

**ليست قارئ QR بالكاميرا**؛ الملف `QRHealthCertificate-Byvh35hk.js` السابق هو واجهة القراءة التي ترسل إلى `BorderPort_HS/read_doc_health`. أما هذه الوحدة فتجلب السجل والتفاصيل وتتعامل مع جغرافية المصدر والوجهة ووثائق الطباعة والمعاينة. `useExitGate` يستورد وظائف منها لملء أسماء المناطق، وليس لدينا دليل من الملفين أن QRHealthCertificate يستورد هذه الوحدة مباشرة.

## 2. خريطة الاعتمادات والتدفق

```text
QRHealthCertificate (camera)
    └── POST BorderPort_HS/read_doc_health
        └── sessionStorage["hc_print"] -> HealthCertificatePrint (تحتاج المصدر)

Other health-certificate screens
    └── useHealthCertificate (shared singleton)
        ├── fetchHealthCertificates -> pagination-healthcertificate
        ├── createHealthCertificate -> health-certificates
        ├── fetchOriginalDocumentByHash -> return_doc_hc/{hash}
        ├── fetchCertificateReaders -> paginate_qrcode_reader
        ├── fetchCertificateReaderDetail -> return_doc_hc_by_docnumber
        │     ├── qrStore (localStorage)
        │     └── sessionStorage["qr_preview_entry"]
        ├── downloadCertificateReaders -> download_health_qrcode_readers
        ├── downloadHealthCertificates -> download_health_certificates_excel
        ├── uploadPathDocumentFile -> path-document-file
        └── province / district / subdistrict / organization lookups
```

هذه خريطة علاقة وظيفية للواجهة الأمامية، وليست مخطط قواعد بيانات أو إثباتًا لتسلسل يستدعي كل الدوال عند المسح.

## 3. جرد 12 مسار API مميزًا

| النوع | الطريقة | مسار API النسبي | العمل الذي يؤديه العميل |
|---|---|---|---|
| شهادات | POST | `BorderPort_HS/pagination-healthcertificate` | قائمة الشهادات والصفحات |
| شهادات | POST | `BorderPort_HS/health-certificates` | إنشاء شهادة، بمدخلات يمررها المستدعي |
| تفاصيل | GET | `BorderPort_HS/return_doc_hc/{hash}` | جلب وثيقة بمُعرّف مُرمّز في URL |
| تفاصيل | POST | `BorderPort_HS/return_doc_hc_by_docnumber` | جلب التفاصيل برقم الوثيقة |
| قراءات | POST | `BorderPort_HS/paginate_qrcode_reader` | قائمة قراءات QR للشهادات |
| تصدير | POST | `BorderPort_HS/download_health_qrcode_readers` | استخراج Excel للقراءات |
| تصدير | POST | `BorderPort_HS/download_health_certificates_excel` | استخراج Excel للشهادات |
| بيانات مرجعية | GET ثم POST عند 405 | `BorderPort_HS/get_provinces` | المحافظات |
| بيانات مرجعية | POST | `BorderPort_HS/get_districts` | الأقضية، مع مسار فرعي بلا مرشح |
| بيانات مرجعية | POST | `BorderPort_HS/get_subdistricts` | النواحي |
| بيانات مرجعية | GET ثم POST عند 405 | `BorderPort_HS/get_orgs` | الجهات |
| مرفقات | POST | `BorderPort_HS/path-document-file` | رفع ملف مصاحب |

مسار `read_doc_health` **ليس ضمن هذه الوحدة**؛ وجوده مؤكد في ملف القارئ السابق. الطرق الواردة هنا مشتقة من مواضع `g.get` و`g.post` في الملف نفسه.

## 4. تفاصيل بنية البيانات

- `items/rows`: قائمة شهادات من رد `pagination-healthcertificate`.
- `pagination`: `Current_Page` و`MaxPages` و`Per_Row` و`TotalRows`.
- `searchdata` و`start_date` و`end_date`: مرشحات محفوظة في حالة مشتركة.
- `provincesMap`، `districtsMap`، `subdistrictsMap` و`orgsMap`: تحويل IDs إلى أسماء بشرية.
- `fetchCertificateReaders`: يحاول توحيد الحقول `doc_number`، و`reader_name`، و`org_name`، و`phone`، و`time_stamp`، وإحداثيات القراءة، والمعرفات الجغرافية.
- `fetchCertificateReaderDetail`: يحول رقم الوثيقة إلى `String` في الطلب، ويخزّن نسخة محلية من الرد ضمن `qrStore` و`sessionStorage`. هذا ليس تأكيدًا لأصالة الوثيقة.

## 5. النتائج ذات الأولوية

| رقم | المستوى التقني المقترح | نمط مثبت | الأثر المحتمل والتوصية |
|---|---|---|---|
| HC-01 | متوسطة / جلسات | `let T=null` يعيد الحالة نفسها لكل مستدعٍ في حياة صفحة التطبيق | احتمال بقاء بيانات الشهادات والمرشحات وخرائط المناطق بعد تبديل المستخدم إن لم تُطهّر؛ ربط الحالة بسياق الحساب |
| HC-02 | متوسطة / خصوصية | `console.log` يطبع جسم طلب قائمة الشهادات و`console.debug` يطبع الرد الكامل | ظهور بيانات البحث/الوثائق في Console أو تجميع السجلات؛ تسجيل معلومات غير حساسة فقط |
| HC-03 | متوسطة / تحقق استجابات | يظهر `error` أو `success:false` ثم يستمر بتطبيع `data` وتحديث النتائج | قد تُعرض بيانات رغم حالة فشل منطقي؛ إيقاف التحديث عند الفشل |
| HC-04 | متوسطة / سلامة البيانات | `re()` يختار أول خاصية قيمتها مصفوفة إذا لم يجد المسارات المعروفة | احتمال اختيار مصفوفة لا تضم شهادات، مثل `errors`؛ عقد استجابة صريح |
| HC-05 | متوسطة / تزامن | عند وجود طلب districts قيد التنفيذ داخل `M` يعود فورًا بقائمة cache قبل اكتماله | احتمال أسماء ناقصة مؤقتًا؛ حفظ Promise الطلب ومشاركته بين المستدعين |
| HC-06 | متوسطة / أداء | `ensureLocationLookupsForCertificate` قد يمر على المحافظات ثم الأرقام 1..18 بحثًا عن قضاء غير معروف | طلبات كثيرة وتباطؤ محتمل؛ API بحث مباشر أو تحميل مجمع محدود |
| HC-07 | متوسطة / اعتمادية | `const d=i.data||[]; (d||[]).map(...)` من غير `Array.isArray` | رد بقيمة object يؤدي إلى خطأ عند العرض |
| HC-08 | متوسطة / صحة التفاصيل | `fetchOriginalDocumentByHash` يبتلع أخطاء GET ويعيد `null`، وقد يرجع payload يحمل `error` | إخفاء سبب خطأ المصادقة أو اعتبار خطأ منطقي بيانات وثيقة |
| HC-09 | متوسطة / خصوصية | معاينة الوثيقة تحفظ `raw.response` في `qrStore` و`sessionStorage` | بقاء بيانات الوثيقة في المتصفح؛ تقليل الحقول ومدة الاحتفاظ |
| HC-10 | متوسطة / تصفية | مرشح `doc_number` في قراءات QR يحاول `Number(value)` | قد يفقد أصفار البداية أو دقة معرّفات كبيرة؛ ضبط نوع المعرّف وفق العقد |
| HC-11 | منخفضة / تنظيف | `clear()` يصفر قائمة الشهادات والصفحات والخطأ لكنه لا يصفر خرائط المواقع والمنظمات ولا مرشحات البحث | احتمال عرض خرائط أو مرشحات قديمة لمستخدم آخر ضمن الصفحة نفسها |
| HC-12 | متوسطة / أداء | `prefetchLocationNamesForItems` ينفذ `Promise.all` على مجموعات المناطق | ضغط متزامن على API عند قوائم كبيرة؛ حد أقصى للتوازي |
| HC-13 | منخفضة / تكامل | مقارنة `t.province_id===Number(e)` مع معرف `province_id` المخزن دون تطبيع رقمي موحد | يمكن ألا تتطابق قيمة نصية مع رقم صحيح؛ توحيد الأنواع قبل المقارنة |

الأرقام HC هنا مؤشرات **Frontend** وليست تصنيف CVSS أو ثغرات خادم مثبتة.

### ملاحظات احترازية إضافية

- عند فشل `fetchHealthCertificates` قد تبقى قائمة شهادات قديمة إلى أن تُحدّث أو تُمسح؛ الدالة تعيد رمي الاستثناء للمستدعي.
- `fetchProvinces` و`fetchOrgs` يجربان POST فقط إذا رد GET بـ405؛ ذلك سلوك توافق API وليس خطأ بذاته.
- `uploadPathDocumentFile` يطبع **وجود توكن كقيمة Boolean فقط**؛ لا يطبع التوكن نفسه هنا. لا يجوز الخلط مع مشكلة QRImported السابقة.
- `createHealthCertificate` يرسل البيانات المقدمة له إلى `POST health-certificates`. لا نرى في هذه الوحدة قواعد تحقق تفصيلية، وقد تكون في نموذج الإدخال أو الخادم.
- لا يثبت وجود رابط `return_doc_hc/{hash}` أن hash مفتاح تشفير أو قيمة توقيع، ولا معنى صلاحية أي وثيقة.
- لا يكشف هذا الملف آلية توليد أو فك تشفير QR الحكومي، ولا يثبت قابلية استخدام أي API دون امتيازات.

## 6. الفرق عن تحليل قارئ الشهادة الصحية السابق

| المسألة | `QRHealthCertificate` | `useHealthCertificate` |
|---|---|---|
| المسح بالكاميرا | نعم | لا |
| القراءة الأساسية | `read_doc_health` | لا يوجد استدعاء له هنا |
| التحقق المحلي من 48 ساعة | موجود في القارئ | **غير موجود** في هذه الوحدة |
| معاينة التفاصيل | تخزن `hc_print` للطباعة | تسترجع تفاصيل برقم الوثيقة أو hash وتخزن `qr_preview_entry` |
| سجل قراءات QR | يرسل القراءة | يجلب قائمة `paginate_qrcode_reader` ويصدّرها |
| إحداثيات GPS | عند المسح | يطبع/يطبعّن إحداثيات سجلات قادمة من API |
| أنشطة أخرى | تشغيل الكاميرا والتنقل للطباعة | إدارة شهادات ومناطق وجهات ومرفقات |

التحقق من 48 ساعة في القارئ **لا يثبت أن الخادم يطبق القاعدة نفسها**، كما لا يثبت أن كل طرق الوصول إلى التفاصيل تمر عبره.

## 7. التوصيات وخطة العمل

1. افصل حالة المحادثة/المستخدم عن الحالة المشتركة، وامسح معلومات الوثيقة والمرشحات عند الخروج.
2. أوقف طباعة الردود الحساسة وجسم الطلب كاملًا في Console.
3. اعتمد عقد API واضحًا مع `success` و`data` ذات نوع صريح، ولا تختر أول مصفوفة عشوائية.
4. استبدل caching باستخدام `in-flight Promise` لكل رقم منطقة، وحدد سقف توازي لجلب المناطق.
5. عرّف `doc_number` نوعيًا قبل تحويله، واحفظ أصفاره الأولية ومعرّفاته الكبيرة.
6. احذف نسخ المعاينات المخزنة بعد انتهاء الغرض، ولا تعرض محتوى وثيقة لجهة غير مخولة؛ التحقق الحقيقي يجب أن يكون في Backend.
7. اختبر الحالات على بيانات اصطناعية في مختبر منفصل، مع عدم إرسال POST إلى الإنتاج.

## 8. الأدوات والاختبارات المضافة للمشروع

```sh
python3 tools/ish/use_health_certificate_review.py /path/to/useHealthCertificate-DVL2cDcP.js
python3 -m unittest discover -s tests -p 'test_use_health_certificate_review.py' -v
```

المراجع يعمل دون شبكة أو تنفيذ JS؛ يطبع فقط أسماء الأنماط وبصمة SHA-256 ومسارات API. اختبارات الوحدة تعتمد نصوصًا تجريبية لا تتضمن بيانات حقيقية. الـCI لا يختبر صلاحيات أو صحة الوثائق.

## 9. الملف التالي المطلوب

`HealthCertificatePrint-<hash>.js` (اسم الملف الفعلي يحدد بعد العثور عليه في manifest أو ملفات Vite). نحتاجه لتوضيح طريقة استخدام `sessionStorage["hc_print"]` واختيار الحقول المطبوعة. البديل `DisableDocument-AXBjrkYS.js` لمراجعة دورة الإلغاء أو إعادة الضبط.

**الخلاصة:** تمت مراجعة مصدر معلومات الشهادة والمناطق وسجل قراءات QR والأرشفة والتصدير. الجزء الناقص هو السلوك الخادمي الرسمي وآلية إصدار/توقيع QR، ولن يُستنتج من مجرد بيانات المتصفح.
