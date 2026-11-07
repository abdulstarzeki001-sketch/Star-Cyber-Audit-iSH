# تقرير Star Cyber Audit الشامل — منصة UBOOR / عبور

**تاريخ التقرير:** 7 نوفمبر 2026  
**الحالة:** تحليل ثابت لملفات واجهة منشورة ونسخ JavaScript محفوظة؛ لا توجد جلسة مصادقة بالخادم أو فحص اختراق مباشر  
**النطاق:** التعامل مع QR، تسجيل القراءات، حفظها محليًا، الوثائق والمعاينة والطباعة، تسجيل الدخول، بوابتا الدخول والخروج، الرفض والتعطيل، طبقة Huawei Cloud WAF، وتشغيل مختبر iSH.

## 1. ملخص النتائج

- أكّد تشغيل مختبر iSH تحليل **10 ملفات من 10** كانت محفوظة ضمن `offline_samples/`، واستخراج **33 مسار API مميزًا** من هذه المجموعة، وإصدار **15 إشارة مراجعة آلية**. الإشارات ليست ثغرات مثبتة ولا تمثل العدد الكامل لنقاط API في النظام.
- فوق تلك المجموعة، روجع نص **10 وحدات JavaScript إضافية** من المصادر العامة خلال المحادثة، على عمق متفاوت. لم تدخل كلها ضمن نتائج العدّ الخاصة بتشغيل iSH، فلا ينبغي جمع عدد مساراتها مع 33 دون إعادة الجرد.
- `QRCheckpoints` شاشة لعرض `read_doc`، وليست ماسح QR أو مصدر الحقيقة الحكومي. `qrStore` مخزن `localStorage["qr_readings"]`، وليس سجل قراءة رسميًا.
- `AchievementDocument` و`ShipmentDoc` يمكن أن يصنعا **صورة QR محليًا** من معرّف مستند إذا غاب حقل `qr_code`؛ ظهور صورة الرمز لا يثبت صدور رمز رسمي موقع.
- أكثر نقاط المراجعة أهمية: تسجيل Bearer في Console؛ احتمال تكرار POST عند أخطاء الاتصال؛ احتمال عرض سجل وثيقة غير مطابقة بسبب fallback؛ اختلاط توكن الموظف وصاحب الشركة في Axios؛ وحفظ بيانات محتملة الحساسية في متصفح مشترك.

**الحد الحاسم:** لم نثبت تزوير الوثائق، أو تجاوز صلاحيات الخادم، أو معرفة مفتاح توقيع QR، أو اعتماد قراءات سيطرات غير صحيحة. أي نتيجة من هذا النوع تحتاج دليلًا من الخادم واختبارات مخولة ومنضبطة.

## 2. مصادر المراجعة

### مجموعة iSH المحفوظة (10)
`index-gleMzSil.js`، `QRLocal-5TAaXbzM.js`، `QRDocument-BJwpoEJY.js`، `QrCodeReaderCustoms-a-UBVR7y.js`، `useExitGate-BvHNutwH.js`، `AchievementDocument-DEzIzJ3I.js`، `ShipmentDoc-Dx885_fz.js`، `CompanyOwnerView-CIdFF3LL.js`، `qrStore-B8bgApfd.js`، `QRCheckpoints-Brs0uL0-.js`.

### وحدات عامة إضافية تمت مراجعتها (10)
`QrLocalImporter-DYzNB5Fh.js`، `QrControlScan-M6uGJnR1.js`، `useLocalCompany-DfV5kpAj.js`، `QRReadings-B-a3jcrk.js`، `ExitGateView-D33Au6wp.js`، `EntranceGateView-B9IBJo4k.js`، `DisableDocument-AXBjrkYS.js`، `RejectedLocalDocuments-CC07EpF_.js`، `QRImported-C65Oqm1K.js`، `QRHealthCertificate-Byvh35hk.js`.

### مرجع وظيفي رسمي
المركز الوطني للتحول الرقمي العراقي: https://ndtc.gov.iq/services/aboor-platform. يصف نطاق TIR والمحلي والمستورد والشهادات الصحية، ويؤرخ الإحصاءات المنشورة **19 أغسطس 2026**. تلك الأرقام ليست قياسًا آنيًا في تاريخ التقرير.

## 3. خريطة تدفق QR الموثقة

### أ. المحلي
`QRLocal` → فك رمز الكاميرا بـ `BarcodeDetector` أو `jsQR` → توحيد قيمة QR إلى رابط عند الحاجة (`/robot?url=`) → `POST local_form/read_doc_company` بجسم `url` وإحداثيات → حفظ نسخة القراءة في `qrStore` → فتح `QRDocument` → عرض الوثيقة/قراءات `read_doc` أو رفضها حسب الواجهة.

**ملاحظة:** قراءات QR ونتائج الخادم تختلف عن سجلات التاريخ المحلية. قبول HTTP أو طباعة QR ليس شهادة أصالة.

### ب. المستورد وبوابة الخروج
`QrLocalImporter` → الكاميرا → `searchImportedGoods` من `useExitGate` → `POST support_org/read_qr_exitgate` مع `url` و`x_coordinate` و`y_coordinate` → وضع البيانات المسترجعة في حالة مشتركة → الانتقال إلى `AchievementDocument` عند نجاح HTTP وفق الفرع المفحوص. الدالة `searchImportedGoods` نفسها لا تضيف إلى `qrStore`.

`AchievementDocument` عندما يُعطى رقمًا قد يستدعي `POST support_org/return_doc_qrcode_export` بجسم `{doc_number:String(value)}`، ويعرض استمارة الناقل وسجل `read_doc`.

### ج. الشهادة الصحية
`QRHealthCertificate` → `POST BorderPort_HS/read_doc_health`، مع تخزين بيانات طباعة في `sessionStorage["hc_print"]`. تفسّر الواجهة HTTP 402 كوثيقة منتهية الصلاحية، لكن ذلك لا يثبت قانون الصلاحية العام أو كيف يطبّقه الخادم.

### د. قراءات السيطرات والسجلات
`QRCheckpoints` يعرض اسم الجهة ووقت القراءة والإحداثيات. يستقبل `props.items` أو يستخدم بدائل `history.state.read_doc` ثم `sessionStorage["qr_read_doc"]` ثم `route.query.read_doc`. **لا يتصل بخادم API بنفسه**.

`QrControlScan` يعرض سجلًا يتضمن رقم الوثيقة، اسم الموظف، الهاتف، السيطرة، نوع المنتج، الوقت، وملاحظة الرفض. المنطق الفعلي في `useLocalCompany`.

## 4. فهرس نقاط API ذات الصلة

| الواجهة/المصدر | طريقة HTTP | المسار النسبي | وظيفة الواجهة المؤكدة |
|---|---|---|---|
| `QRLocal`, `QRImported` | POST | `local_form/read_doc_company` | إرسال قراءة وثيقة الشركة |
| `QRDocument` | POST | `local_form/refuse_doc_company` | إرسال قرار رفض وسببه وإحداثياته |
| `QRDocument` | POST | `BorderPort_HS/path-document-file` | رفع صورة PNG منشأة من عرض الوثيقة |
| `useExitGate` | POST | `support_org/read_qr_exitgate` | قراءة QR في بوابة الخروج |
| `useExitGate` | POST | `support_org/paginate_qrcode_reader_import` | سجل قراءات المستورد |
| `useExitGate` | POST | `support_org/return_doc_qrcode_export` | استرجاع استمارة الناقل |
| `useExitGate` | POST | `support_org/download_qrcode_readers_import` | تنزيل سجل Excel |
| `useExitGate` | POST | `BorderPort_HS/return_doc_hc_by_docnumber` | استرجاع شهادة صحية برقم الوثيقة |
| `useLocalCompany` | POST | `local_form/paginate_qrcode_reader2` | سجل قراءات المحلي في QrControlScan |
| `useLocalCompany` | POST | `local_form/return_doc_qrcode` | تفاصيل الوثيقة للمعاينة |
| `useLocalCompany` | POST | `local_form/download_qrcode_readers2` | تصدير Excel |
| `QRReadings` | POST | `local_form/pagination_qrcode_reader` | سجل قراءات عبر شاشة أخرى |
| `QRReadings` | POST | `local_form/download_qrcode_readers` | تصدير عبر الشاشة الأخرى |
| `QRHealthCertificate` | POST | `BorderPort_HS/read_doc_health` | قراءة الشهادات الصحية |
| `DisableDocument` | POST | `local_form/reset_company_qrcode` | إجراء إعادة ضبط/تعطيل وثيقة وفق تسمية الواجهة |
| `EntranceGateView` | POST | `carrier_register/scrape_search_goods_gateway_register` | جلب بيانات حمولة مسجلة عند الدخول |
| `EntranceGateView` | POST | `carrier_register/gateway_decision` | إرسال قرار البوابة مع مرفقات |
| `index` | POST | `local_form/company_verify_login` | بدء دخول صاحب الشركة برقم الهاتف |
| `index` | POST | `local_form/company_verification` | التحقق من رمز الشركة |
| `index` | PUT | `local_form/company_item_reduce` | تحديث بيانات/عنصر شركة |

**تنبيه:** هذا فهرس للشيفرة التي روجعت، وليس وثيقة OpenAPI رسمية. اختلاف `paginate_qrcode_reader2` عن `pagination_qrcode_reader` حقيقي في نصوص الواجهة، وقد يعكس وحدات أو أدوارًا مختلفة. لا ينبغي توحيدهما بالتخمين.

## 5. إنشاء الوثائق والرموز والطباعة

- `AchievementDocument`: يعرض رقم الوثيقة `doc_id` والتاريخ والوقت، المكتب الكمركي، السائق والعجلة والعربة والمحافظة والوزن والوجهة والمخلص والشركة والوصل والمبلغ ونوع الحمولة والملاحظات وقراءات السيطرات.
- يختار مادة QR وفق `qr_code || doc_id || doc_number`، ثم يرسم QR محليًا باستخدام `toDataURL`. عند إخفاق الرسم قد يستدعي `https://quickchart.io/qr?text=...`، ما قد يرسل محتوى QR إلى طرف خارجي عند تحميل الصورة.
- `ShipmentDoc`: يعرض `qr_code` إن كان متاحًا، وفي بعض غيابه يولّد رمزًا معلوماتيًا من رقم الموافقة أو العجلة أو اسم السائق. لا دليل أنه رمز تحقق حكومي رسمي.
- الطباعة في الواجهتين تنسخ HTML/CSS إلى نافذة جديدة مع إعداد A4؛ لا يعني ذلك إنشاء ملف حكومي موقّع أو PDF معتمد. استخدام `height:296mm` و`overflow:hidden` في نموذج الناقل قد يقص المستند الطويل.
- `QRDocument`: قد يلتقط صورة PNG لعنصر المستند ويرفعها إلى `BorderPort_HS/path-document-file` في سياق علم `auto_send`. هذا **علم سير عمل محلي**، وليس حالة إصدار رسمية.

## 6. الهوية والصلاحيات

- لدى صاحب الشركة مسار دخول مكون من رقم هاتف (`company_verify_login`) ورمز (`company_verification`) ويحفظ `company_owner_token` في localStorage.
- لدى الموظف سياق مصادقة مستقل، لكن نسخة الواجهة تُظهر استعمال Axios مشترك؛ إن توفر توكن موظف، فقد يستبدل ترويسة `Authorization` الخاصة بطلب صاحب الشركة.
- عند HTTP 401 قد ينفّذ المعالج المشترك خروج الموظف وصاحب الشركة معًا؛ هذا خطر التباس جلسات وعيب فصل سياق مستخدمين.
- أزرار المعاينة والتنزيل والرفض محكومة في الواجهة بامتيازات نصية مثل `return_doc_qrcode`, `download_qrcode_readers2`, `refuse_doc_company`. **إخفاء الزر لا يثبت صلاحية أو منعًا داخل الخادم**.
- في `QRLocal`، يتجه غياب التوكن إلى `{name:"Login"}` بينما اسم المسار المرصود في Router هو `LoginView`، ما يستحق إصلاحًا.

## 7. سجلات المتصفح والتحقق من الروابط

- `qrStore` يحفظ مصفوفة في `localStorage['qr_readings']` باستخدام `unshift`. لا يوجد حدّ عدد أو انتهاء آلي أو تحقق من نوع المصفوفة أو إظهار خطأ فشل الحفظ.
- السجل المحلي قد يشمل الرابط الأصلي وبيانات الرد وإحداثيات الموقع وعلم `auto_send`. لا يُحذف المفتاح في وظائف تسجيل الخروج التي فُحصت.
- `QRDocument` إذا لم يجد ID المعاينة المطلوبة قد يعرض `x[0]` (عنصرًا آخر من السجل)، وهو خلل ربط واجهة بالوثيقة الصحيحة.
- `QRCheckpoints` قد يقرأ `read_doc` من Session Storage أو URL دون مقارنة معرف الوثيقة المطلوبة؛ يمكن عرض بيانات غير موثوقة في شاشة العميل، ولا يعني أن السجل الرسمي عُدّل.
- في `useLocalCompany` تنشأ ثلاثة إدخالات `QRCODE:...` تجريبية عند غياب `qr_readings`؛ يجب عدم تفسير كل صف في تخزين المتصفح كسجل صادر من الخادم.

## 8. مؤشرات هندسية مرتبة حسب الأولوية

| الأهمية المقترحة | الدليل في المصدر | المشكلة/الأثر المحتمل | ما لا يثبته الدليل |
|---|---|---|---|
| عالية | `QRLocal` يطبع Bearer token | تسرب جلسة عبر سجلات Console/بيئات تشخيص | لا يثبت أن طرفًا ثالثًا اطلع عليه |
| عالية | `QRLocal`, `QRImported`, `DisableDocument` تعيد POST تشخيصي بعد خطأ | احتمال تكرار طلب غير idempotent | لا يثبت تكرار الكتابة بالخادم |
| عالية/متوسطة | Axios مشترك للموظف والشركة | احتمال استخدام هوية خاطئة أو تسجيل خروج مزدوج | لا يثبت تجاوز صلاحيات backend |
| عالية في البيئات المشتركة | `qr_readings` يحتفظ برد وإحداثيات | بقاء بيانات حساسة بعد الخروج | لا يثبت طبيعة كل رد واقعي |
| متوسطة | fallback `QRDocument` و`QRCheckpoints` | عرض وثيقة أو سجل قراءة غير مطابق | لا يغير سجلات backend |
| متوسطة | QR من `doc_id`/`doc_number` عند غياب QR حقيقي | التباس بين رمز معلوماتي ورمز تحقق | لا يثبت التزوير الحكومي |
| متوسطة | fallback خارجي `quickchart.io` | احتمال إرسال نص QR لطرف ثالث | لا يثبت حدوث الطلب بالفعل |
| متوسطة | النجاح مستدل عليه برسالة تحتوي `تم` / HTTP 200 | تصنيف غير دقيق لحالات الرفض/انتهاء الصلاحية | لا يثبت قبول الخادم للوثيقة |
| منخفضة/متوسطة | `QRCheckpoints` يعرض UTC في بعض الحالات والوقت المحلي في غيرها | اختلاف الساعة لنفس اللحظة | لا يثبت تلاعبًا بتاريخ الخادم |
| منخفضة | إظهار موقع بإحداثي واحد والفتح باثنين | رابط خرائط غير فعال | لا يثبت فساد الإحداثيات بالخادم |
| منخفضة/متوسطة | ارتفاع A4 ثابت مع قص المحتوى | فقدان حقول في نسخة مطبوعة طويلة | لا يثبت فقدان بيانات أصلية |

## 9. طبقة HuaweiCloudWAF

عندما نزل المستخدم ملف `QRCheckpoints.js` عبر curl على iSH ظهر HTML يحتوي `meta http-equiv="Server" content="HuaweiCloudWAF"`. تلك **صفحة تحدٍ أمني** وليست كود وحدة QRCheckpoints. تجمع بصمة المتصفح عبر FingerprintJS2 وتستخدم CryptoJS AES-CBC لتوليد Cookie `wafatclconfirm` محددة بمدة 30 دقيقة في الشيفرة المعروضة، وتكشف بعض مؤشرات التشغيل الآلي.

ليس مفتاح AES الموجود هناك مفتاح إصدار QR الحكومي، ولا يجوز قياس صحة توقيع الوثائق منه. أداة Star Cyber Audit تصنّف هذه الاستجابة كـWAF بدل تحليلها على أنها JS، ولا تتجاوز الحماية.

## 10. ما كشفته عملية iSH الفعلية

ثبت بالصور أن المستخدم:
- ركب مجلد Files `/mnt/star-audit` بواسطة `mount -t ios . /mnt/star-audit` بعد إلغاء سابق للاختيار.
- نفّذ `sh run.sh` داخل المجلد وظهرت `Star Cyber Audit complete`.
- ظهرت `JavaScript analyzed: 10 / 10 total files` و`33` مسارًا مختلفًا.
- تشكلت الملفات `reports/analysis.json`, `reports/api_paths.txt`, `reports/inventory.csv`, `reports/report.html`, `reports/review_flags.txt`.

نجح أيضًا اختبار SSH المحلي داخل iSH بـ`star@127.0.0.1:2222`، لكن **Moshi** لم ينجح وقت الاختبار بسبب timeout على iOS؛ لا توجد جلسة ChatGPT للتحكم المباشر في هاتف iSH. Remote Desktop Commander كان يعرض حاسوب Windows بوضع Offline عند آخر فحص.

## 11. ما الذي بقي مجهولًا؟

1. طريقة إنشاء `qr_code` على الخادم: هل هو URL، رقم، قيمة موقّعة، أو مزيج؟
2. مصدر الحقيقة الرسمي لجدول `read_doc`: متى تسجّل القراءة، وبأي هوية، وهل يُمنع التكرار؟
3. كيف يتحقق Backend من ملكية الوثيقة والصلاحيات وصحتها وإلغائها وانتهائها؟
4. كيف تتعامل واجهة `return_doc_qrcode` مع الأرقام المختلفة في الخادم، وهل يوجد تحقق ترابط للرقم/النوع؟
5. هل تسجيل دخول صاحب الشركة والموظف مفصول فعليًا في جميع مسارات Backend؟
6. ماذا تعني الاستجابة 402 أو الحقول `is_main`, `company_type`, `hash_id` وفق عقد الخادم الرسمي؟
7. ما وضع حماية بيانات QR والإحداثيات في سياسة الاحتفاظ والمراجعة الرسمية؟

## 12. المرحلة القادمة المقترحة (من دون التأثير على الإنتاج)

1. نقل `reports/analysis.json` و`reports/inventory.csv` من iSH إلى المحادثة، أو تشغيل نسخة محدثة على الملفات العامة التي جُمعت لاحقًا.
2. جمع نسخة محددة الإصدار من `useLocalCompany`, `EntranceGateView`, `QRHealthCertificate`, `DisableDocument`, `QRReadings` وتثبيت SHA-256 لها؛ حتى لا تختلط إصدارات منشورة مختلفة.
3. بناء «مصفوفة عقود API» لكل نقطة: المدخلات، الاستجابة المتوقعة، الأخطاء، حالة المصادقة، والفروق بين واجهة العميل وقواعد الخادم (مجهولة حتى تُوثق).
4. مراجعة الدوال عالية المخاطر في **مختبر نسخ تجريبية**: تكرار POST عند الفشل، تبادل الجلسات، سقوط المعرّف إلى سجل آخر، انتهاء الصلاحية المحلي، والتوقيت.
5. إذا توفرت صلاحية رسمية ومصدر Backend، إجراء مراجعة إعدادات وتسجيلات خادم واختبار تحقق آمن على بيئة مرحلية أو سجلات منقحة.

## النتيجة النهائية

وصلنا إلى **خريطة وظيفية واضحة نسبيًا للواجهة الأمامية** للمنصة، وحددنا ثغرات تصميم محتملة وأخطاء واجهة مثبتة. **لم نصل بعد إلى إثبات أصالة أو تزوير أو تجاوز حماية وثيقة حكومية**؛ ولتحقيق ذلك يلزم مصدر Backend مخول، لا مجرد الصور التي يصنعها المتصفح أو النصوص التي يحفظها `localStorage`.