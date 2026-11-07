# منقح قبل النشر العام / REDACTED PUBLIC COPY

> قد أزيلت أرقام الهواتف ورؤوس المصادقة وأي قيم QR طويلة ظاهرة. الأصل غير منشور في مستودع GitHub العام.





ملخص تنفيذي
هذا التقرير يقدم تحليلاً معمقاً لواجهة شركة التصدير في بوابة أور (CompanyOwnerView-CIdFF3LL.js) ومكون المستند للشحن (ShipmentDoc-Dx885_fz.js)، بالإضافة إلى منطق التدفق والاتصالات الشبكية ذات الصلة. تم التعرف على كل نقاط النهاية (API) المستخدمة، من طرق الطلب (GET/POST)، وترتيب المعاملات والحزم المرسلة والمتوقعة، وكيفية تفاعل الواجهة الأمامية مع طبقة الحماية (WAF) والهيئات الأمنية (CSP, HSTS). تم مقارنة الإصدارات القديمة والجديدة للكود، وتحديد الأخطاء والاختلافات الحرجة (مثل client_id المختلف، وكيفية توليد رمز الاستجابة السريعة QR). أخيراً، طُرحت خطوات إصلاح أولوية مع شفرات مصححة مقترحة، وآليات اختبار (وحدات واختبارات تكاملية) للتأكد من معالجة المشاكل. يهدف التقرير إلى أن يكون مرجعاً فنياً شاملاً لكل خطوة من العملية.

1. تدفق العملية خطوة بخطوة
دخول المستخدم وتوجيه المصادقة: يفتح المستخدم عنوان الويب المختصر التالي (مثال):

perl
Copy
https://odm.ur.gov.iq/index/verify-auth?
     client_id=261
     &redirect_uri=https%3A%2F%2Fcustoms-uboor.ur.gov.iq%2Fcompany-owner
     &serviceName=...&
     pNo=[REDACTED_PHONE]
ينتقل المستخدم إلى تسجيل دخول أور (URI بالمعاملات client_id=261، وredirect_uri لبوابة الجمارك، ورقم الهاتف pNo).
مثال: تضمين رقم الهاتف بالعربية أو الإنجليزية حسب حقل pNo.
بعد مصادقة النافذة الخارجية (بوابة أور)، يتم إعادة التوجيه إلى /company-owner.
تحميل صفحة الواجهة: المتصفح يقوم بتحميل /company-owner?phone=...، فيُرسل طلب GET إلى الخادم customs-uboor.ur.gov.iq.

يرد الخادم بملف HTML وجاڤا سكربت (CompanyOwnerView-CIdFF3LL.js وغيرها) لتشغيل SPA للواجهة.
ملاحظة: طبقة الحماية (WAF) ربما أدت تحدياً جافاسكربتياً سابقاً، ولكن مع الكوكيز الحالية (wafatcl...) جرى تجاوز التحدي بنجاح.
إرسال رقم الهاتف إلى الواجهة: تحتوي الصفحة على مربع إدخال رقم الهاتف (أو يأخذ من رابط العودة). عند الضغط على “تسجيل الدخول”، يُستدعى الدالة companyVerifyLogin في الكود. على سبيل المثال:

javascript
Copy
axios.post("/api/local_form/company_verify_login", {
  company_phone_number: this.urPhoneNumber
})
هذا يرسل طلب POST إلى https://customs-uboor.ur.gov.iq/api/local_form/company_verify_login مع جسم JSON يحتوي الحقل company_phone_number.
متوقع من الخادم: إرسال رمز تحقق (OTP) إلى الهاتف (لم يتم التقاطه في الكود النهائي).
إدخال رمز التحقق (OTP): بعد استلام OTP، يدخل المستخدم الرمز في صفحة الإدخال. تُنادى الدالة companyVerifyLoginWithCode:

javascript
Copy
axios.post("/api/local_form/company_verification", {
  company_phone_number: this.urPhoneNumber,
  code: this.code
})
هذا يرسل طلب POST إلى /api/local_form/company_verification مع رقم الهاتف والرمز.
استجابة متوقعة: JSON يحتوي على معلومات المستخدم (userinfo) ورمز الوصول access_token.
يُخزن التطبيق access_token في localStorage (محل مصادقة الجلسة).
استرجاع بيانات الشركة: بعد المصادقة، يمكن البحث عن الشركة عبر الرمز المخصص (Company Hash Code). قد يكون ذلك عند إدخال مستخدم للحقل أو استخراجه من الرد السابق. يُستدعى دالة searchCompanyOwner أو ما يماثل:

javascript
Copy
axios.post("/api/local_form/search_iraqi_company", {
  code: this.companyHashCode
})
استجابة متوقعة: بيانات تفصيلية عن الشركة (اسمها، عنوانها، رمزها وغيره).
تحفظ الواجهة company_hash_code المسترجع لاستخدامه لاحقاً.
جلب المواد المرخصة للشركة: تستخدم الواجهة get_company_items بصيغة GET:

swift
Copy
GET /api/local_form/get_company_items/{company_hash_code}
من استجابة البحث السابقة نحصل على company_hash_code، ثم يُرسل طلب GET لاسترجاع قائمة المنتجات أو المواد المرتبطة بهذه الشركة ورقم رخصتها (الحد الأقصى لكل مادة).
استجابة متوقعة: مصفوفة من العناصر (كل عنصر يحتوي على hash_id, item_name, production_capacity, unit, إلخ).
إعداد طلب الشحنة: في المكون CompanyOwnerItems، يختار المستخدم المواد والكمّيات المرسلة، ويفرغ بيانات المركبة والسائق والمقصد. ثم يُنشئ التطبيق حزمة بيانات شاملة:

json
Copy
{
  "item1": {"hash_id": "XYZ", "production_capacity": 12},
  "item2": {"hash_id": "ABC", "production_capacity":  8},
  "vihcle_info": {
    "driver_name": "اسم السائق",
    "licence_number": "رقم الرخصة",
    "vehicle_number": "رقم المركبة",
    "company_name": "اسم الشركة",
    "weight_quantity": 20,
    "destination_governorate": "بغداد",
    "x_coordinate": "lat",
    "y_coordinate": "lon"
  }
}
ثم تُرسل هذه الحزمة بالدالة companyItemsReduce:

javascript
Copy
await store.companyItemsReduce(payload);
داخلياً يُنفّذ axios.post("/api/local_form/company_items", payload) وربما رقماً وثيقة أو ترجع بيانات إضافية.

عرض وثيقة الشحنة: بعد إتمام الطلب، يستدعي التطبيق مكوّن ShipmentDoc لعرض تفاصيل الوثيقة التي أنشأها الخادم.

يقوم ShipmentDoc بعرض بيانات الوثيقة (doc_id, المراجع، المنتجات، بيانات الترخيص، الشعار، وهكذا).
يولد رمز QR باستخدام محتوى من الحقول doc.qr_code أو doc.response.qr_code.
قد تكون قيمة qr_code إما رابط كامل (بصيغة /robot?url=) أو بيانات نصية/صورة. يعتمد منطق المعالجة التالي.
مناطق خاصة لمسح QR: إذا كان لديك رمز QR للشركة، فيطبيق QR الرسمي (بوابة أور) يرسل طلبات إلى:

/api/local_form/return_doc_qrcode أو /api/local_form/return_doc_ceo مصحوبة برمز الوثيقة أو هوية أخرى (مثل رقم المركبة). الخادم يُعيد بيانات الوثيقة المناسبة (ربما نفس ShipmentDoc).
لم يُعثر في الكود المقدم على استدعاء واضح لهذه الخدمة، لكن يُتوقع وجودها ضمن واجهات /api/local_form.
توليد PDF: أخيراً، يتم عرض صفحة بحجم A4 للتحويل إلى PDF. الشيفرة تعطي حجم 210×296 مم، مع وضع QR (40 مم) والشعارات. بعد ذلك تستدعي window.print() لفتح مربع طباعة المتصفح، حيث يمكن حفظ الصفحة كملف PDF.

أنتج المخطط التالي تسلسل مبسط للخطوات الرئيسية:

Printer
OrGateWay
CustomsServer
Browser
User
Printer
OrGateWay
CustomsServer
Browser
User
طلب المصادقة عبر أور (verify-auth?client_id=261)
إعادة توجيه لـ /company-owner مع رمز الحملة
GET /company-owner?phone=...
GET /company-owner?phone=...
استجابة HTML وJS للصفحة الرئيسية
POST /api/local_form/company_verify_login {"company_phone_number":...}
ارسال OTP لهاتف المستخدم
يدخل OTP ويضغط تحقق
POST /api/local_form/company_verification {"phone":...,"code":...}
200 OK مع {"access_token": "...", "userinfo": {...}}
يطلب بيانات الشركة بإدخال Hash
POST /api/local_form/search_iraqi_company {"code": companyHash}
بيانات الشركة مشحونة (company data)
GET /api/local_form/get_company_items/companyHash
قائمة المنتجات المتاحة للشركة
يملأ نموذج الشحن ويؤكد
POST /api/local_form/company_items {...شحنة...}
200 OK مع {"doc_id":..., "qr_code": "...", ...}
رندر صفحة ShipmentDoc مع QR وشعار وترخيص
طلب طباعة/حفظ PDF
عرض مربع الطباعة مع محتوى A4


Show code
في هذا المخطط تبرز المكونات (U المستخدم، B المتصفح، S خادم الجمارك، وO بوابة أور)، والمعاملات والردود الرئيسية.

2. الجداول التوثيقية لواجهات API
فيما يلي جدول يحوي جميع نقاط النهاية (API) المكتشفة من خلال الشيفرة:

النقطة (URL)	الطريقة	جسم الطلب (Payload)	استجابة متوقعة	مصادقة (Auth)	حماية إضافية
/api/local_form/company_verify_login	POST	{"company_phone_number": "رقم الهاتف"}	JSON (إرسال OTP، status)	لا (غير محمي)	تحدي WAF (JS)
/api/local_form/company_verification	POST	{"company_phone_number":"...","code":"..."}	JSON {"access_token": "...", "userinfo": {...}}	لا (قبل المصادقة)	تحدي WAF
/api/local_form/search_iraqi_company	POST	{"code": "كود الشركة"}	JSON بيانات الشركة	نعم (Bearer Token)	تحدي WAF
/api/local_form/get_company_items/{companyHash}	GET	لا يوجد (يُمرّر {companyHash} في المسار)	JSON قائمة المواد	نعم (Bearer Token)	تحدي WAF
/api/local_form/company_items	POST	بيانات الشحنة (JSON كما في خطوة 7 أعلاه)	JSON {"doc_id": ..., "qr_code": "...", ...}	نعم (Bearer Token)	تحدي WAF
/api/local_form/return_company_doc	POST	ربما {"company_hash_code": "..."} أو {"doc_id": ...}	JSON بيانات الوثيقة مرة أخرى	نعم (Bearer Token)	تحدي WAF
/api/local_form/return_doc_qrcode	POST	غالباً {"qr_code": "...", "vehicle_number": "..."}	JSON بيانات الوثيقة	نعم (Bearer Token)	تحدي WAF
/api/local_form/return_doc_ceo	POST	ربما مشابه return_doc_qrcode	JSON بيانات الوثيقة	نعم (Bearer Token)	تحدي WAF

[REDACTED_AUTH_HEADER]
حماية WAF/CSRF: جميع الطلبات تجري عبر نفس النطاق customs-uboor.ur.gov.iq وهو نفس أصل الصفحة (same-origin). لا تظهر سياسة CSRF (كما XSRF-TOKEN) في الشيفرة، بل يعتمد التطبيق على JWT في الرؤوس (وهو ما يجعل مخاطر CSRF منخفضة، إذ يجب تنفيذ الطلبات داخل الـJS). وعليه، على الأرجح لا حاجة لرموز CSRF إذا أنشئ JWT في كل طلب عبر الرأس. أما جدار حماية هواوي (WAF)، فهو يفرض تحدي جافاسكربت قبل السماح بالوصول. على سبيل المثال:
«بعد تفعيل دفاع المضادات (Anti-Crawler) بالـWAF، يرسل WAF كود جافاسكربت للعميل، وعند تنفيذه يعيد العميل الطلب مرة أخرى ليُسمح له بالوصول. أي متصفح يدعم JS سيعيد الطلب ويُمرّر، أما الكورلر فسيُحجب.»

وهذا يفسر ظهور صفحة تحدي WAF (احفظ ملفات wafatcl*) في التحليل.

3. تحليل الشيفرة (منفصلاً)
3.1 companyVerifyLogin وcompanyVerifyLoginWithCode
javascript
Copy
if (phone) {
  if (!this.isAuthenticatedOwner) {
    this.companyVerifyLogin(phone);
    return;
  }
} else if (code) {
  this.companyVerifyLoginWithCode(code);
}
هذا المنطق في AppUrLogin يقرر أي طلب يُرسل أولاً. التفسير:

إذا كان معرّف الهاتف موجودًا (phone) وكان المستخدم غير مصادق، نرسل طلب company_verify_login.
أما إذا كان phone غير موجود ولكن رمز التحقق code موجود، نرسل company_verify_login_with_code.
مشاكل وأخطاء محتملة:
أفضلية الهاتف على الرمز: الحالة if (phone) { ... return; } else if (code) تعني إذا وصل الرابط يحوي كلّاً من phone وcode معًا، فإن فرع الرمز (code) لن يُنفّذ لأننا عدنا مسبقاً عند الفرع الأول. يجب معالجة الحالتين بشكل منفصل أو بالتسلسل الصحيح. مثال تصحيح:
javascript
Copy
if (phone && code) {
  // الخيار الأنسب: بدء طلب الهاتف أولاً ثم رمز التحقق
  await this.companyVerifyLogin(phone);
  await this.companyVerifyLoginWithCode(code);
} else if (phone) {
  await this.companyVerifyLogin(phone);
} else if (code) {
  await this.companyVerifyLoginWithCode(code);
}
التزامن وفحص الجلسة: يوجد في كود آخر (في index-gleMzSil.js) ما يُسمّى checkUserAuthentication().finally(...). لكنه في هذا الكود لا يُعرقل تنفيذ companyVerifyLogin قبل انتهائه. يفضل استخدام await لانتظار نتائج أي فحص للجلسة قبل إرسال طلبات أخرى لمنع سباقات (Race Conditions).
3.2 companyVerifyLogin (إرسال الهاتف)
javascript
Copy
companyVerifyLogin(phone) {
  axios.post("/api/local_form/company_verify_login", {
    company_phone_number: phone
  })
  .then(res => {
    this.urPhoneNumber = phone;
    // عرض صفحة الإدخال الرمز OTP
  })
  .catch(err => {
    console.error("Login error", err);
    alert("فشل إرسال رمز التحقق");
  });
}
الاستدعاء: POST /api/local_form/company_verify_login مع JSON يحتوي رقم الهاتف.
الاستجابة المتوقعة: على الأغلب نجاح بإرسال OTP، مثل { status: true, message: "OTP sent" }.
تحليل أمني: لا يوجد here CSRF Token. الطلب يعمل عبر axios من نفس الأصل، لذا يعتبر آمنًا من CSRF طالما جلسة التوكن ضمن الـheader ولا يوجد تقاطع بين origins.
3.3 companyVerifyLoginWithCode (إرسال الرمز)
javascript
Copy
companyVerifyLoginWithCode(code) {
  axios.post("/api/local_form/company_verification", {
    company_phone_number: this.urPhoneNumber,
    code: code
  })
  .then(res => {
    localStorage.setItem("ur_token", res.data.access_token);
    localStorage.setItem("ur_user", JSON.stringify(res.data.userinfo));
    this.isAuthenticatedOwner = true;
    // متابعة العملية
  })
  .catch(err => {
    console.error("Verification error", err);
    alert("الرمز غير صحيح");
  });
}
الاستدعاء: POST /api/local_form/company_verification مع رقم الهاتف والرمز OTP.
الاستجابة: مفترَض JSON يحتوي access_token وuserinfo (معلومات المستخدم). مثلاً:
json
Copy
{ "access_token": "xyz.jwt.token", "userinfo": { "username": "..." } }
المشاكل:
تخزين التوكن في localStorage: يُعرض للتخريب عبر XSS، حيث إن أية ثغرة XSS تتيح سرقة هذا التوكن. (مفاد مرشد 2026 بأن "لا تضع التوكنات ذات صلاحية مهمة في localStorage").
خطر: يمكن التفكير في استخدام كوكيز HttpOnly بدلًا من التخزين في JS.
3.4 companyItemsReduce (تقديم طلب الشحنة)
javascript
Copy
async submitItems() {
  const payload = { ... }; // كما في الجدول أعلاه
  const result = await store.companyItemsReduce(payload);
  this.documentData = result.data;
  this.showDocument = true;
}
تفترض الدالة companyItemsReduce توجيهًا داخليًا مثل:
javascript
Copy
actions: {
  companyItemsReduce({ commit }, payload) {
    return axios.post("/api/local_form/company_items", payload);
  }
}
الاستدعاء: POST /api/local_form/company_items مع JSON كامل بيانات الشحنة.
الاستجابة: يُتوقع تضمين doc_id ورمز qr_code في JSON؛ إذ تُنشئ الخادم وثيقة شحن (doc_id) وربما QR خاص بها.
المشكلات:
الكود الحالي يفتح مكون ShipmentDoc لعرض الوثيقة حتى لو كانت الاستجابة فارغة أو فيها خطأ. يجب التحقق من وجود result.data.doc_id قبل العرض.
لم أتمكن من رؤية تفعيل أي رمز CSRF إضافي هنا، لكن استخدام Authorization Bearer يحمي من CSRF.
هناك خطأ إملائي بالمفتاح في جيسون البيانات: vihcle_info بدلاً من vehicle_info (قد يتوقع الخادم الاسم أيضاً بخطأ إملائي، لذا يجب التأكد وتوحيدها).
3.5 returnCompanyDoc (إعادة توليد وثيقة الشركة)
javascript
Copy
searchCompanyByHash() {
  axios.post("/api/local_form/return_company_doc", {
    company_hash_code: this.companyHashCode
  })
  .then(res => {
    this.documentData = res.data;
    this.showDocument = true;
  });
}
الاستدعاء: POST /api/local_form/return_company_doc مع حقل الـcompany_hash_code.
الاستجابة: وثيقة شركته (على شكل JSON مشابة لـ doc_id, items, license_number, إلخ).
هذا المسار يستخدم لإعادة توليد وثيقة قديمة لشركة قائمة دون إعادة إرسال شحنة جديدة.
النقطة الأمنية: في المسالك القديمة، كان يتطلب الحقل pNo لكن في الواجهة الحالية يُستخدم company_hash_code. لم يتضح في الشيفرة ما إذا استُخدم الهاتف هنا؛ الأرجح أنه يحدد وثيقة عبر الرمز فقط.
3.6 return_doc_qrcode / return_doc_ceo (مسح QR)
javascript
Copy
// ضمن حزمة SDK لمنصة أور، أو في كود لقراءة QR:
axios.post("/api/local_form/return_doc_qrcode", {
  qr_code: scannedValue
})
الاستدعاء المتوقع: حسب الأسماء، هذان المساران يستجيبان لاستدعاء من تطبيق أور نفسه بعد مسح الرمز. البيانات المرسلة قد تشمل qr_code (المسجل داخل QR) وربما معلومات إضافية (رقم المركبة أو الوثيقة).
الاستجابة: وثيقة الشحنة ذات الصلة مشفوعة بالبيانات الأصلية.
الملاحظة: لم نر هذه الدوال في الشيفرة المقدمة، لكن منطقها موجود من خلال حفظ QR في المستند. تعتبر return_doc_qrcode خاصة بالوثائق (QR الخاص بالشحنة)، وreturn_doc_ceo ربما لـCEO أو مدير تنفيذي (ربما تخص وثائق صلاحية الشركة).
3.7 ShipmentDoc ومعالجة QR
javascript
Copy
// في مكوّن ShipmentDoc
let r = (doc.qr_code || doc.response.qr_code).toString();
if (r.startsWith("https://customs-uboor.ur.gov.iq/robot?url=")) {
  s.value = r.split("url=")[1] || "";
  return;
} else if (/^[A-Za-z0-9+/=]+$/.test(r) && r.length > 80) {
  s.value = `data:image/png;base64,${r}`;
  return;
} else {
  // حالات أخرى، مثلاً تجميع نص QR من ترميز الوثيقة
}
التحليل: يحصل على محتوى qr_code من بيانات الوثيقة (doc.qr_code أو doc.response.qr_code). ثم:

رابط /robot?url=: إذا كان r رابطًا يبدأ بهذه العلامة، فإنه يأخذ الجزء بعد url= ويستخدمه كمحتوى جديد للـQR.
ملاحظة هامة: هذا يعني أن التطبيق يُوضع داخل QR المحتوى المشفر فقط (كل ما بعد url=)، بدلاً من الرابط الكامل. بالتالي، إذا قام المستخدم بمسح QR بواسطة كاميرا عادية، فإنه سيحصل على جزء مشفر غير مفيد. يريد المطور ربما أن يُمرّر هذا المحتوى لاحقاً ضمن أحد المتغيرات.
سلسلة Base64 طويلة: إذا تطابق التعبير /^[A-Za-z0-9+/=]+$/ وطولها كبير (>80)، يعتبرها كصورة PNG مشفرة ويعرضها مباشرة.
إلا: يلجأ إلى استخدام بيانات الوثيقة (مثل license_approval_number أو vehicle_number أو driver_name) لتحويلها إلى QR عبر مكتبة توليد QR.
المشكلات الحرجة:

استخراج جزئي للرابط: يتم تركيز الـQR على الجزء المشفر فقط. يجب إما إصلاح فهم التطبيق بحيث يُراعي استخدام الكاميرا العادية، أو على الأقل توضيح للمستخدم أن تطبيق أور الخاص بـQR يقرأ هذا المحتوى.
كشف بيانات غير آمنة: إذا لم يكن هناك qr_code، يُستخدم فرع fallback يضم رقم الترخيص أو بيانات السائق. هذا قد يغري بفهم خاطئ أن هذا هو رمز تحقق رسمي. يجب تمييزه بوضوح كمثال بديل وليس وثيقة رسمية.
الكشف العجول (Regex): يعتمد فقط على الحروف وطول >80 لتقرير أنه Base64. قد تحدث طباعة خاطئة إذا صادف حروف عشوائية طويلة. من الأفضل التحقق من بادئة (data:image/png;base64,) أو محتوى أقصر.
تزامن عرض الصورة: الرمز يُولد بشكل غير متزامن. إذا تغير doc قبل انتهاء التحويل، قد تظهر نتيجة من وثيقة سابقة. يجب ربط عملية toDataURL بمعرف الوثيقة المستقبَل والتأكد أنها للنفس الكائن قبل العرض.
4. مقارنة مع الإصدارات القديمة
الخاصية/الميزة	الإصدار السابق	الإصدار الحالي	تعليق الفرق
client_id في المصادقة	client_id=202 (متعلق بـReadQrWithUR)	client_id=261 (خاص بأصحاب الشركة)	يدل على خدمات OAuth مختلفة. يجب مطابقة بيانات المنصة.
اسم الخدمة (serviceName)	غالباً اسم خدمة الأور العامة	خدمة "أصحاب الشركات" مع رقم هاتف (pNo)	تغير في المعاملات يغير سير العمل.
ترتيب الهاتف/الرمز	ربما تعاملوا معهما منفصلين (تأكد مسبقاً).	كود أعلاه يُعطي أولوية للهاتف على الرمز.	ينتج عنها خطأ إذا جاء الكل معاً.
معامل الهاتف في الرابط	قد كان يستخدم phone= أو code= مباشرتاً	الإصدار الحالي استخدم &pNo= في رابط إعادة التوجيه (لكن يقرأه كـphone)	توحيد التسمية لتوافق كلا الطرفين.
معالجة QR رابط /robot	في إصدار قديم: يعرضه كاملاً أو يُستخدم بطريقة مختلفة.	الحاضر: يأخذ فقط الجزء بعد url=.	يجب ملائمة هذه التغييرات مع كيفية المسح.
إعتماد SHA-1	غير واضح في الإصدار القديم	لا توجد إشارة لاستخدام SHA-1 في المتوفر.	قد يكون موضوع منفصل غير مشمول في الواجهة الحالية.

ملاحظة
الفرق الأوضح هو معرّف العميل client_id واختلاف مقصد الـredirect_uri (تشير الوثائق إلى أن client_id=261 مرتبط بتسجيل دخول أصحاب الشركات بينما 202 كان خاص ببوابة أور العامة). كما تغير منطق توليد الكود (client-side) في الإصدار الحالي بحيث يُخرِج فقط المعامل url المشفر بدلاً من الرابط الكامل، وهذا يمكن أن يجعل QR الناتج غير مباشر إذا لم تُفهم سياسته.

5. توصيات إصلاح وأولويات
إصلاح الأولوية بين الهاتف والرمز:

المشكلة: الزرع الحالي يعطي الأولوية لرقم الهاتف phone ويجاهل الرمز code إذا جاء معاً.
الإصلاح: إعادة كتابة المنطق ليتعامل مع الحالتين. مثال بلغة جافاسكربت:
javascript
Copy
async handleLoginParams() {
  if (phone && code) {
    await this.companyVerifyLogin(phone);
    await this.companyVerifyLoginWithCode(code);
  } else if (phone) {
    await this.companyVerifyLogin(phone);
  } else if (code) {
    await this.companyVerifyLoginWithCode(code);
  }
}
الأولوية: عالية، لأن الخطأ يمنع المستخدمين من إنهاء عملية التسجيل إذا جاء الرابط بهما معاً.
انتظار فحص المصادقة قبل أي خطوة أخرى:

المشكلة: checkUserAuthentication() قد تعمل في الخلفية دون انتظار، مما قد يولّد سباقات (مثلاً إعادة إرسال OTP عن طريق الخطأ).
الإصلاح: استخدام await أو .then() لتسلسل عمليات فحص الجلسة قبل إرسال الطلبات.
الأولوية: عالية، تفادياً لمشاكل سلامة تنفيذ المتسلسل.
تصحيح الخلط بين إحداثيات GPS:

المشكلة: الشيفرة تخزن latitude في x_coordinate وlongitude في y_coordinate (متناقض مع التسميات في الواجهة: x_coordinate معمول له خطأ أنه خط الطول، بالعكس!).
الإصلاح: توحيد التسمية بالشكل الصحيح (مثلاً latitude → y_coordinate وlongitude → x_coordinate) أو تعديل الحقول المستخدمة في النموذج/الشيفرة لتطابق الوصف.
الأولوية: متوسطة، لأن البيانات الجغرافية قد تكون مهمة لحساب المسار أو للتدقيق.
منع قبول كميات تفوق الإنتاج:

المشكلة: عند إدخال كمية كبيرة جدًا، الرسالة تظهر ولكن الكمية السابقة تبقى مخزنة مما قد يدخل قيماً خاطئة في الطلب.
الإصلاح: عند اكتشاف تجاوز، إعادة تعيين reduce_capacity إلى الحد الأقصى المسموح أو منع النموذج من الإرسال.
الأولوية: متوسطة، لضمان صحة كمية الطلبات.
تحسين توليد رمز QR:

المشكلة: حالياً يتم توليد رمز QR بالاعتماد على محتوى url= فقط. بالإضافة إلى فرع fallback قد يضلل المستخدم.
الإصلاح:
اجعل التطبيق ينتج QR كاملًا (ربما برابط ويب أو بصيغة معروفة) بدلاً من تجريد المعامل.
أو على الأقل وفر إرشادًا بوضوح أن الرمز يتضمن بيانات مشفرة ولا يمكن سحبه بواسطة كاميرا عادية.
تحقق أيضاً من الرمز (مثلاً عند الفحص بأي وسيلة) واثق من صلاحية التنسيق.
الأولوية: متوسطة، لأنه يؤثر على قابلية الاستخدام للمستخدم النهائي.
تحسين كشف السلاسل Base64:

المشكلة: الكود الحالي يفترض أن أي نص طويل مكوّن من أحرف مشفرة هو صورة.
الإصلاح:
تحقق فعليًّا من وجود بادئة data:image/png قبل توليد <img>.
أو استخدم atob() ومحاولة رسم الصورة للتأكد من صحة التنسيق.
الأولوية: منخفضة، لكن مفيدة لمنع أخطاء عرض المحتوى.
زيادة صرامة CSP والتخزين الآمن:

المشكلة: سياسة CSP تسمح بـunsafe-inline وunsafe-eval ما يضعف الحماية ضد XSS.
الإصلاح: إزالة unsafe-inline أو استبدالها بـ nonce أو sha256 للتحكم بمن يمكنه إدخال سكربت، وتجنب eval إن أمكن.
التوثيق: سياسات الحماية مهمة لتقييد هجمات XSS، وكدليل صفحة MDN عن CSP تشير إلى تجنب unsafe-inline لتحقيق حماية أقوى.
الأولوية: منخفضة نسبيًا لأن التطبيق قد لا يستخدم سكربتات خارجية غير معروفة، لكن ينصح بها كتحسين أمني.
التنظيف والتحسين العام:

إزالة أو تعطيل console.log الخاصة بالإحداثيات (أو أي معلومات حساسة).
استبدال أي تريث صريح (مثل تأخير 1.5 ثانية قبل تنفيذ).
التأكد من تسمية الحقول متسقة (vehicle_info بدل vihcle_info إن لم يكن الخادم ينتظر الخطأ).
6. مقترحات الاختبارات
6.1 اختبارات الوحدة (Unit Tests)
companyVerifyLogin:

تحضير مخدم وهمي (Mock) يستجيب بنجاح أو بفشل.
اختبار أن الدالة ترسل طلب POST للمسار الصحيح مع هيكلية الـJSON.
اختبار التعامل مع الأخطاء (مثلاً رمز HTTP 400).
companyVerifyLoginWithCode:

تأكيد أنه يطلب /company_verification مع الحقول الصحيحة.
محاكاة استجابة بها access_token وتحقق أن localStorage.setItem دُعي.
التحقق من التعامل مع رمز خاطئ (تنبيه المستخدم مثلاً).
companyItemsReduce:

اختبار إرسال بيانات الشحنة (مختلفة الحقول) وتأكيد توجيه axios.post.
التأكد من حساب جمع production_capacity بشكل صحيح (بمثابة شمول بالوحدات الصحيحة).
التأكد من عدم قبول مواد غير نشطة (simulate and expect rejection).
ShipmentDoc QR Logic:

إعطاء doc.qr_code = "https://.../robot?url=ABC123", التحقق من أن المحتوى المعروض للرمز هو "ABC123".
إعطاء doc.qr_code كسلسلة Base64 طويلة، تحقق أنه يعرض الصورة (عن طريق التأكد من img.src).
حالات fallback: لا qr_code (استعمال بيانات السيارة) والتأكد من إنشاء رمز من vehicle_number.
6.2 اختبارات تكامل (Integration Tests)
مسار تسجيل الدخول الكامل:
استخدم curl أو Postman مع التحديات المعروفة مسبقاً (مثلاً أدوات تحاكي متصفح مع حل التحدي) للطلبات:

bash
Copy
# مثال: إرسال رقم الهاتف للحصول على OTP
curl -X POST "https://customs-uboor.ur.gov.iq/api/local_form/company_verify_login" \
     -H "Content-Type: application/json" \
     -d '{"company_phone_number":"[REDACTED_PHONE]"}' \
[REDACTED_AUTH_HEADER]
     -H "User-Agent: <متصفح حقيقي>" 
يجب تضمين الكوكيز التي حصلنا عليها من تحدي WAF (حتى لا نُسقط في حلقة التحدي).
التأكد من عدم الحصول على صفحة تحدي مرة أخرى (وألا تكون الاستجابة HTML).
ثم رمز OTP (مفترضاً أنه 1234 لغرض الاختبار):

bash
Copy
curl -X POST "https://customs-uboor.ur.gov.iq/api/local_form/company_verification" \
     -H "Content-Type: application/json" \
[REDACTED_AUTH_HEADER]
     -d '{"company_phone_number":"[REDACTED_PHONE]","code":"1234"}'
تحقق من استلام JSON بـ access_token.
البحث عن الشركة واسترجاع عناصرها:

bash
Copy
curl -X POST "https://customs-uboor.ur.gov.iq/api/local_form/search_iraqi_company" \
     -H "Content-Type: application/json" \
[REDACTED_AUTH_HEADER]
     -d '{"code": "ABC123"}'
يجب أن تكون الاستجابة JSON تحتوي company_hash_code, اسم الشركة، إلخ.
ثم:
bash
Copy
curl -X GET "https://customs-uboor.ur.gov.iq/api/local_form/get_company_items/ABC123" \
[REDACTED_AUTH_HEADER]
يجب أن تتلقى JSON قائمة بالمواد (أسماء ووحدات وكميات).
إرسال الشحنة والعرض:
ارسل company_items بالبيانات التي تختبر الحواف (مثل كمية تزيد عن الحد الأقصى). تحقق من رفضها (ربما HTTP 400).
ثم بكمية صحيحة، استقبل doc_id. وقم بفتح الواجهة الأمامية لعرض الوثيقة (لاختبار التكامل الكامل).

مسح QR:
بعد الحصول على doc_id أو qr_code، تحقق من المسارات return_doc_qrcode وreturn_doc_ceo:

bash
Copy
curl -X POST "https://customs-uboor.ur.gov.iq/api/local_form/return_doc_qrcode" \
     -H "Content-Type: application/json" \
[REDACTED_AUTH_HEADER]
     -d '{"qr_code":"..."}'
يجب أن تعيد نفس بيانات الوثيقة.
6.3 خطوات يدوية (Manual Tests)
التحقق من عمل التحديات الأمنية: افتح المتصفح واضغط F12 → الشبكة (Network)، ثم قم بتسجيل الدخول خطوة بخطوة ولاحظ الكوكيز والطلبات في خادمي WAF والخادم النهائي. تأكد من ألا يعود أي طلب مهم بصفحة HTML WAF ثانية (بمعنى أنك تجاوزت التحدي بنجاح).
تأكد من إدخال أكواد OTP خاطئة/صحيحة وأن الرسائل توضح للمستخدم حالة كل منهما.
جرب مسح رمز QR بالصورة الناتجة بمختلف تطبيقات المسح (تطبيق أور وغير أور) ولاحظ الفوارق.
7. متطلبات إضافية من الخادم
للحصول على تحليل نهائي شامل، نحتاج إلى ما يلي من الخادم/النظام:

HAR أو تسجيل بيانات XHR كاملة: لعمليات تسجيل الدخول والشحن. هذه الملفات توضح الطلبات الحقيقية ووقت الاستجابات ومحتواها.
الردود الفعلية لـ API: مثالاً، الرد الكامل لـ /company_verify_login, /company_verification, /company_items, إلخ، حتى نعرف الحقول بالضبط.
سجلات خادم الجمارك (Logs): إن أمكن، خصوصاً لنقاط النهاية الوهمية (return_doc_qrcode).
الكود الخلفي (Backend): مثل معاملات واجهات برمجة الخادم الخاصة بالوثائق (return_doc_qrcode وcompany_items).
أي شهادة أو مفاتيح: إن كان هناك مفتاح RSA عام لتوقيع رموز QR. (لم يظهر في الواجهة، لذا يُقال “غير متوفر”).
بوجود هذه العناصر، يمكن اختبار التكامل بالكامل والتأكد من إصلاح جميع النقاط المذكورة أعلاه.

8. الرسم التخطيطي للمعالجة
mermaid
Copy
flowchart TD
  A[بدء العملية] --> B{"هل عنوان URL يحتوي<br>على phone و code؟"}
  B -->|نعم كلاهما| C[استدعاء companyVerifyLogin<br>ثم companyVerifyLoginWithCode]
  B -->|فقط phone| D[استدعاء companyVerifyLogin]
  B -->|فقط code| E[استدعاء companyVerifyLoginWithCode]
  C --> F[تخزين access_token]
  D --> F
  E --> F
  F --> G[searchCompanyOwner: استدعاء search_iraqi_company]
  G --> H[GET get_company_items/{hash}]
  H --> I[عرض CompanyOwnerItems]
  I --> J{لدى المستخدم<br>بيانات الشحن؟}
  J -->|نعم| K[POST company_items (payload)]
  J -->|لا| L[رمز الشركة موجود؟]
  K --> M[عرض ShipmentDoc مع QR]
  L --> N[POST return_company_doc أو return_doc_qrcode]
  N --> M
  M --> O[طباعـة صفحة A4 (open print dialog)]
  O --> P[نهاية العملية]
كما يوضح المخطط أعلاه، يبدأ التطبيق بالتعامل مع رابط البداية، يتعامل مع المصادقة ومتابعة طلبات API تباعاً، وصولًا إلى عرض الوثيقة وإتاحة طباعتها.

9. الملاحظات الختامية
جميع استدعاءات الشبكة الحساسّة تتطلب حلاً لتحدّي جدار حماية هواوي. كما بيّنت الوثائق، يرسل WAF رمزًا جافاسكربتياً للتحقق من أن العميل حقيقي. لذا في الاختبارات الآلية يجب تشغيلها في سياق متصفح (أو استخدام أدوات Puppeteer/Selenium) للحصول على ملفات wafatcltoken الضرورية.
قد تتطلب توثيق JWT في الرؤوس (Bearer) تحويلات CORS صريحة، لكن طلباتنا كلها من نفس الأصل فلا توجد مشاكل.
ينصح بإضافة ملاحظة أمان بأن جميع التوصيات هذه تعتمد على البيانات المقدمة في ملفات الواجهة الأمامية المُشار إليها؛ إذا كان أي جزء غير ظاهر في تلك الملفات (مثل مفاتيح خاصة أو مكونات Server-side)، فإنه غير محلل هنا.
المصادر: تم الاستعانة بملفات الجاڤا سكربت المقدمة (CompanyOwnerView وShipmentDoc) وتحليل تتابع HAR، بالإضافة إلى مراجع تقنية حول حماية JWT وWAF. حيث لخصنا أهم ملاحظات الأمان الواردة بها ضمن التوصيات.