# نتائج البحث في الملفات الأصلية — إجابة الأسئلة الثمانية لبوابة أصحاب الشركات

**مراجعة ساكنة، 9 نوفمبر 2026**  
المستودع: `abdulstarzeki001-sketch/Star-Cyber-Audit-iSH` — **Private**؛ لم تُنفَّذ أي طلبات إلى واجهات API الحكومية.  
المادة: النسخ الأصلية من حزم JavaScript، وملف التفريغ النصي التاريخي لصور Network المؤرخة في **21 يناير 2026**، والتقارير السابقة.  
**تنبيه لدرجة الجزم:** الأكواد الأمامية تكشف **شكل الطلب وما يتوقعه العميل من Response**؛ لا تكشف بالضرورة **الجسم الذي أعاده الخادم في الجلسة**، أو تنفيذ الخادم وإعدادات HTTP التي يرسلها.

## الملفات الجديدة التي عُثر عليها في مكتبة المستخدم وأُرشفت كما هي

| الملف الأصلي | الحجم بالبايت | مكان الأرشفة الخاص |
|---|---:|---|
| `index-d1j-jb9c(3).js` — مدخل بناء يناير | 1,378,888 | `research/private-evidence/2026-11-09/jan-2026-bundle/index-d1j-jb9c(3).js` |
| `companyownerview-dwbcwxr4.js` — مكوّن بناء يناير | 38,636 | `research/private-evidence/2026-11-09/jan-2026-bundle/companyownerview-dwbcwxr4.js` |
| `index-ccmhdhtn.js` — المدخل اللاحق الذي كان مفقودًا | 1,380,214 | `research/private-evidence/2026-11-09/nov-2026-bundle/index-ccmhdhtn.js` |

حفظت الملفات **دون إصلاحات أو تعديلات**؛ تمت إعادة إضافة نهاية السطر الموجودة في المصدر أثناء إعادة تركيب النص من قارئ المكتبة للتحقق من مطابقة الحجم الأصلي. تُظهر شجرة GitHub أحجام الملفات الثلاثة المذكورة. **لا يعني تطابق الحجم وحده ضمان بصمة التجزئة**؛ استُخدم محتوى المكتبة الأصلي ولم نُجرِ تحويلات للكود.

## ملخص الحالات: ماذا حُسم بعد البحث؟

| السؤال | النتيجة الحالية | درجة الإثبات |
|---|---|---|
| 1. جسم Response الفعلي لـ`return_company_doc` | **غير متوفر حرفيًا**؛ اكتشفنا بنية JSON التي يتوقعها العميل | مؤكد في الكود، لا في Response خام |
| 2. PDF أم JSON/QR وبيانات طباعة؟ | العميل يستخدم **JSON `data.doc_id`** ويعرض **HTML A4 عبر `ShipmentDoc`** ويطبع بالمتصفح؛ لا يتعامل مباشرة مع PDF لهذا الطلب | مثبت كتنفيذ واجهة |
| 3. إنشاء QR | الواجهة **تعرض `qr_code`** وتحوّل نوعًا من روابط `robot?url=` إلى طلب صورة عبر QuickChart؛ آلية **إنشاء القيمة على الخادم غير متوفرة** | مثبت في العميل فقط |
| 4. توقيع QR والتحقق منه | لا تظهر عملية توقيع أو تحقق مشفّر في مسار عرض هذا المكوّن؛ لا يمكن نفي أو إثبات توقيع **خادمي** | غير مثبت |
| 5. مصادقة صاحب الشركة | وُجد تدفق `company_verify_login` ثم `company_verification` للحصول على `access_token` وإرساله Bearer؛ **سياسات التفويض بالخادم غير موجودة** | تدفق العميل مثبت |
| 6. الملف `index-D1j-Jb9C.js` | **تم العثور على الحزمة الأصلية وتحليل وظائفها المركزية وأرشفتها** | مثبت |
| 7. الملف `CompanyOwnerView-DWbcwxR4.js` | **تم العثور على ثلاث نسخ متطابقة نصيًا من قراءة المكتبة**؛ مقارنة بإصدارات سابقة | مثبت |
| 8. أصل ترويسات CORS المختلفة | لا يمكن الجزم هل هي من Response واحد، أم طلبات/لقطات مختلفة؛ **لا توجد HAR خام تربط السطور بمصدر واحد** | غير محسوم |

## الإجابة 1 — ما Response الفعلي لـ return_company_doc؟

**مصدر الكود:** `index-d1j-jb9c(3).js`، داخل Pinia `localCompanies.actions.returnCompanyDoc(t)` قرب **موضع الحرف 586,548** (ملف مصغّر؛ السطر وحده طويل).

العميل يرسل:

```javascript
// تمثيل مقروء للدالة الأصلية وليس نسخًا حرفيًا لرموز التصغير
const result = await api.post(
  `local_form/return_company_doc/${companyHashCode}`,
  null,
  { headers: { Authorization: `Bearer ${companyOwnerToken}` } }
);

if (result.status === 200 || result.status === 201) {
  const doc = result.data.data;
  if (doc?.doc_id) return doc;
  return null; // رسالة: الاستجابة موجودة لكن البيانات غير مكتملة
}
```

**هذه حقائق واضحة من الكود:**
- `POST` مع **body = null**، وBearer token خاص بصاحب الشركة.
- يقبل Status **200 أو 201**.
- يستخرج `response.data.data` (كائن `data` داخل JSON).
- يتطلب وجود `doc_id` داخل ذلك الكائن لكي يعتبره صالحًا للعرض.
- في حالة غياب `doc_id` يعرض «تم الرد بنجاح ولكن بيانات الوثيقة غير مكتملة» ويُرجع `null`.

**لكن لا نستطيع إعادة بناء Response حقيقي**؛ صور Network لا تعرض جسمه. المتاح أن ترويسة الاستجابة كانت `Content-Type: application/json` والحالة `200` في الصورة رقم 66 من الملحق. ولا يمكن الجزم بأن رد يناير تضمّن بالفعل الحقل `doc_id`، أو معرفة قيمته وسائر الحقول من دون صورة/نسخة Response.

## الإجابة 2 — PDF أم JSON مع QR/بيانات طباعة؟

من مكوّن `CompanyOwnerView-DWbcwxR4.js`:

- يمرر نجاح `returnCompanyDoc` كائن الوثيقة إلى مكوّن `ShipmentDoc`.
- يستعرض `doc_id` و`date_str` أو `current_date` و`time_str`، إضافة إلى معلومات السائق والمركبة والحمولة والأصناف.
- زر «طباعة الوثيقة» يفتح نافذة HTML جديدة ويجمع CSS والطباعة بواسطة `window.print()`، مع `@page { size: A4; margin: 0; }`.
- **لا تستخدم دالة `returnCompanyDoc`** `responseType:"blob"` أو `pdf_base64` أو قارئ PDF.

إذن **مسار العميل هو JSON بيانات وثيقة → معاينة HTML → طباعة / Save as PDF من المتصفح**. لا يوجد دليل في هذه الملفات على أن هذا المسار استلم PDF بحد ذاته، رغم أن واجهات أخرى بالمشروع قد تستخدم PDF أو `pdf_base64` بشكل مستقل.

## الإجابة 3 — كيف ينشئ الخادم قيمة QR؟

**السؤال بصيغته الخادمـية لا يملك جوابًا مثبتًا من الملفات المتاحة.** ما هو مثبت في مكوّن `ShipmentDoc` المضمن بمكوّن يناير:

```javascript
const qrValue = doc?.qr_code || doc?.response?.qr_code;
```

منطق عرض QR الظاهر:
1. `data:image...` → يستخدمها كما هي.
2. سلسلة تبدأ `https://customs-uboor.ur.gov.iq/robot?url=` → يأخذ النص بعد `url=`، ثم يطلب `https://quickchart.io/qr?text=...` مع `size=200`.
3. رابط `http(s)` عادي → يستخدمه كمصدر الصورة.
4. قيمة Base64 طويلة تطابق شروط الواجهة → يعرضها `data:image/png;base64,...`.
5. عند وجود `qr_code` لكن لا يطابق الأشكال السابقة: يستخدم نصًا احتياطيًا من رقم الإجازة أو المركبة أو اسم السائق، إن توفر، لإنشاء **صورة QR فقط** بواسطة QuickChart.

التفريغ التاريخي يُظهر بالفعل `quickchart.io/qr?text=gAAAAA...`؛ الجزء بعد `text=` **مقطوع في الصور**. هذه الخدمة تولّد **صورة QR للنص المرسل إليها**؛ لا تُثبت عملية توقيع أو تحقق رسمي. **مصدر بناء القيمة الأصلية `qr_code` داخل Backend غير معروف**.

**نقطة خصوصية:** النص الذي يُرسل في Query String إلى QuickChart يصل إلى طرف ثالث؛ يجب تقييم حساسيتـه قبل استخدام هذه الآلية في خدمات رسمية.

## الإجابة 4 — هل QR موقّع رقميًا وكيف يُتحقق منه؟

لا يوجد في مكوّن `ShipmentDoc` التابع لمسار بوابة صاحب الشركة تنفيذ ظاهر لـ`crypto.subtle.sign` أو `crypto.subtle.verify` أو مفاتيح تحقق؛ تعامل الواجهة مع `qr_code` هو **عرض/إحالة/ترميز صورة**. عدم رؤية التوقيع في **العميل** لا يثبت عدم وجود توقيع في الخادم أو في بوابة مسح مستقلة.

محتوى `gAAAAA...` المقتطع **قد يشبه** تمثيلات توكنات مشفرة شائعة، لكن بداية النص وحدها **لا تثبت** خوارزمية بعينها، ولا أن النص يحمل توقيعًا أو شهادة رقمية أو مستندًا موثقًا. التحقق الرسمي لا يمكن إثباته دون عقد API أو توثيق من الجهة المالكة ومسار تحقق مرخص له؛ لا يجوز استنتاجه من نجاح تحميل PNG.

## الإجابة 5 — آلية المصادقة لصاحب الشركة: ما الذي ثبت؟

**من مدخل يناير `index-d1j-jb9c(3).js`:**

```text
/company-owner?phone=...         (الرقم موجود في URL)
   |
   +-- POST local_form/company_verify_login
   |      body: {company_phone_number}
   |
   +-- واجهة UR verify-auth
   |      client_id=261
   |      redirect_uri=/company-owner
   |
   +-- /company-owner?code=...
   |
   +-- POST local_form/company_verification
   |      body: {code}
   |      result expected: userinfo + access_token
   |
   +-- حفظ owner access_token + userinfo في localStorage
   |
   +-- POST search_iraqi_company           [owner Bearer]
   +-- GET get_company_items/{hash_id}     [owner Bearer]
   +-- PUT company_item_reduce             [owner Bearer]
   +-- POST return_company_doc/{hash}      [owner Bearer]
```

الأسماء الدقيقة لدوال المتجر:
- `companyVerifyLogin(t)` → يرسل `{company_phone_number:t}` إلى `local_form/company_verify_login`؛ الاستجابة لا تثبت وحدها هوية المالك.
- `companyVerifyLoginWithCode(t)` → POST `local_form/company_verification` مع `{code:t}`، ويستخرج `n.data.userinfo` و`n.data.access_token` عند HTTP 200.
- `checkUserAuthentication()` → يقرأ `company_owner_token` و`is_authenticated_owner` و`company_user_info_owner` من `localStorage` ويضبط حالة الواجهة؛ **لا يرسل طلب تحقق خادمي في هذه الدالة**.
- مكوّن `AppUrLogin` ينتقل إلى `https://ur.gov.iq/verify-auth?client_id=261&redirect_uri=...&pNo=...`.

**نتيجة مؤكدة:** توجد آلية اعتماد *عميل* مبنية على تحقق رمز والاحتفاظ بـBearer.  
**ما لا نعرفه:** هل Backend يربط التوكن بصاحب الشركة في كل طلب؟ مدة التوكن، ومحتواه، وآلية التحقق من مالك `hash_id` و`company_hash_code`، وهل يوجد تفويض موارد مستقل. لا تساوي `isAuthenticatedOwner=true` المحلية صلاحية خادمية.

**ملاحظة مراجعة برمجية:** معترض Axios العام يكتب `Authorization` من `UserAuth.token` عند وجوده، رغم أن طلبات المالك تمرر Bearer خاصًا بها. في جلسة تحتوي توكني موظف ومالك معًا قد يحدث **تداخل ترويسة Authorization**. هذه فرضية خلل في المتصفح تتطلب اختبارًا محليًا بحسابات تدريب؛ **ليست دليل تجاوز Backend**.

## الإجابة 6 — تم العثور على index-D1j-Jb9C.js وتحليل الوظائف

**الحالة الجديدة: موجود في مكتبتك ومؤرشف في GitHub الخاص كما هو** باسم `index-d1j-jb9c(3).js` (1,378,888 بايت).

لا نكتفي بخريطة Assets؛ داخل هذا الـbundle توجد دوال Pinia المسؤولة فعليًا عن:
- `companyVerifyLogin`، `companyVerifyLoginWithCode`.
- `searchCompanyOwner`، `getOwnerCompanyItems`.
- `companyItemsReduce`، `returnCompanyDoc`.
- `checkUserAuthentication` و`logoutOwner`.
- عنوان API الأساسي `https://customs-uboor.ur.gov.iq/api/`.
- معترضات HTTP لبيانات Authorization والتعامل مع 401 و403 و404 و422 و500.

أكدنا أيضًا أن خريطة الأصول في هذا الملف تشير إلى **`CompanyOwnerView-DWbcwxR4.js`**، فيطابق اسم المورد الذي ظهر في صور يناير.

## الإجابة 7 — مقارنة DWbcwxR4 مع إصدارات CompanyOwnerView الأخرى

**تم فحص 3 نسخ مكتبية** من `companyownerview-dwbcwxr4` (الأصل ونسختان مرقمتان)، ووجدنا نفس المحتوى النصي في قراءتها.

**مقارنة يناير مع `companyownerview-cjdszkn6.js` المؤرشف سلفًا:**
- **كود المكوّن بعد سطر الاستيرادات الأول متطابق حرفيًا عند تجاهل نهاية السطر الأخيرة**.
- الاختلاف الأساسي هو أسماء اعتماد Vite ذات بصمات مختلفة مثل `Card-...` و`Badge-...` واسم ملف `index-...` الذي يستورد منه المكوّن.
- لذلك **سلوك مكوّن البوابة، توليد معاينة ShipmentDoc، الاختيار، والطباعة وQR مطابق في جسم هذا الملف**. لكن هذا لا يضمن تطابق سلوك *الأصول المستوردة أو الخادم*.

**مقارنة مع `CompanyOwnerView-CIdFF3LL.js` في الأرشيف الأقدم:**
- يستورد `ShipmentDoc-Dx885_fz.js` كملف منفصل بدل تضمين مكوّن `ShipmentDoc` داخل نفس حزمة العرض.
- يظهر نفس الاستخدام العام لدوال `companyVerifyLogin` و`searchCompanyOwner` و`companyItemsReduce` و`returnCompanyDoc`.
- يتضمن مسار واجهة إلى `CompanyOwnerCeoLoads` في البناء الأقدم.
- تحميل هذه المكونات من **builds مختلفة** لا يسمح باستبدال أحد ملفات `index` بالآخر مباشرة من دون مطابقة خريطة الاعتمادات.

### يوجد أيضًا مسار ثانٍ للوثيقة

في مكوّن `CompanyOwnerItems`:
- يطلب من المستخدم اختيار كميات أصناف، وبيانات الشحنة/السائق/العجلة.
- يبني `item1`, `item2` ... يحوي كل عنصر `hash_id` و`production_capacity`.
- يضيف حقلًا أصليًا اسمه **`vihcle_info`** (هكذا كُتب في المصدر، لا نصححه بصمت).
- يستدعي `PUT local_form/company_item_reduce` ويعرض نتيجة الطلب أيضًا في `ShipmentDoc`.

**لا تخلط** بين مسار إرسال طلب الشحنة `company_item_reduce`، ومسار إعادة الحصول على الوثيقة `return_company_doc`. كلاهما قد يعرض `ShipmentDoc`، لكن الاستجابتين ليستا بالضرورة بنفس البنية.

## الإجابة 8 — هل CORS `*` و`localhost:5173` تخص Response واحد؟

**لا يمكن حسمها** من الشيفرة أو TXT وحدهما. الدليل النصي يسجل:
- `Access-Control-Allow-Origin: *`.
- `Access-Control-Allow-Origin: http://localhost:5173` في لقطة.
- `Access-Control-Allow-Credentials: true` في بعض صور `get_company_items`.
- ترويسات CORS مختلفة لطلب أيقونات `api.iconify.design`، وهي طلبات طرف ثالث لا تنتمي لخادم الموقع.

توجد احتمالات متعددة: تغيّر Origin بين لقطتين أو بيئتين، خلط نافذتي عرض، ردّان مختلفان، أو وجود ترويستين في رد واحد. لا نمتلك ملفات HAR تربط **كل قيمة بخادم الطلب وRequest ID ووقته ورأسه الفعلي**.

في معيار متصفحات الويب، `Access-Control-Allow-Origin: *` مع طلبات تتطلب `Credentials` لا يسمح عادةً بقراءة الاستجابة في المتصفح؛ هذا **ليس دليلًا تلقائيًا على اختراق**. وإذا ظهرت قيمتان مختلفتان للترويسة نفسها في رد فعلي واحد فقد يرفض المتصفح تفسيرها. يلزم مراجعة Response Headers من نفس السجل دون أي أسرار.

## ملاحظات هندسية مهمة من الفحص

1. **الاستجابة المقبولة من `returnCompanyDoc` تحتاج `data.doc_id`**؛ هذه أوضح إجابة جديدة، لكنها لا تثبت وجود ذلك الحقل في **Response التاريخي**.
2. **الطباعة تتم في المتصفح** باستخدام قالب A4؛ لا تتطلب أن يكون رد API ملف PDF.
3. **قيمة QR قد تُعرض أو تُحوّل إلى صورة بواسطة QuickChart**؛ لا دليل على أن QuickChart يوقّع البيانات أو أن الخادم يستعمل تقنية تشفير محددة.
4. **حراسة الواجهة تعتمد جزئيًا على localStorage**؛ التوثيق والتفويض النهائيان من مسؤولية Backend ولم يُقدّم كوده.
5. **ملفات يناير وملفات اللقطة الأحدث متصلة هندسيًا**، لكن خريطة الاستيراد وأسماء Bundles تختلف، ولا يجوز اعتماد الـbuild الأقدم باعتباره تطابق إصدار نظام حي.
6. **تضارب ترويسات CORS بقي غير محسوم** رغم إعادة التحليل؛ لا يجوز إصدار تقرير ثغرة من هذه الصور وحدها.

## مصادر المشروع المرجعية

- [الأصل: مدخل يناير](../../../research/private-evidence/2026-11-09/jan-2026-bundle/index-d1j-jb9c(3).js)
- [الأصل: مكوّن يناير](../../../research/private-evidence/2026-11-09/jan-2026-bundle/companyownerview-dwbcwxr4.js)
- [الأصل: مدخل البوابة الأحدث](../../../research/private-evidence/2026-11-09/nov-2026-bundle/index-ccmhdhtn.js)
- [مكوّن البوابة الأحدث](../../../research/raw-uploads/2026-11-07/company-owner-vite/companyownerview-cjdszkn6.js)
- [المكوّن الأقدم](../../../research/user-supplied/2026-11-08/CompanyOwnerView-CIdFF3LL.js)
- [الأرشيف التاريخي 73 مدخلاً](../../../research/private-evidence/2026-11-09/UBOOR_ALL_73_IMAGES_COMPLETE_TEXT_2026-11-09%202.txt)
- [مرجع مواقع الشيفرة المصغّرة](SOURCE_ANCHORS.json)

### حدود الاستنتاج

ما زلنا لا نملك **جسم Response الفعلي** للوثيقة ولا مصدر Backend ولا ملف HAR مؤرخًا يضمن ترويسات CORS الدقيقة لكل رد. لذلك لا يمكن إعلان إثبات توقيع QR رسمي، أو تجاوز تفويض، أو ثغرة IDOR/BOLA. **الملفات التي وجدناها حسمت شكل تنفيذ العميل، لا ما لم يرسله المستخدم من بيانات الخادم.**
