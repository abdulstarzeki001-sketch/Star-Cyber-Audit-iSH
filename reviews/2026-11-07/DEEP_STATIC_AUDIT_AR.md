# تدقيق ثابت معمّق — Star Cyber Audit / UBOOR / DMS

**التاريخ:** 7 نوفمبر 2026 · **الحالة:** تدقيق مصادر مكتمل للمرحلة الأولى؛ ليست نتائج اختبار اختراق حية.

## نطاق التدقيق والتحقق

- **الهدف:** ملفات مشروع [Star-Cyber-Audit-iSH](../../README.md) وأرشيفات JavaScript المرتبطة بواجهات UBOOR وDMS.
- **الجرد المتحقق عبر GitHub:** 71 ملفًا في فرع `main`، منها 27 ملف JavaScript (بما فيه Cloudflare Worker) و5 CSS و5 HTML و2 Python و2 Shell. وجود ملفات متعددة من نسخ تاريخية/مكررة لا يعني تطبيقًا واحدًا جاهزًا للعمل.
- **فحص الشيفرة:** مراجعة `index-gleMzSil.js` (Vite)، `QRLocal`، `QRDocument`، `qrStore`، `useExitGate`، `AchievementDocument`، `CompanyOwnerView`، `QrCodeReaderCustoms`، وحدات DMS `6439/2752/index`، `LoginView`، أداة `analyze.py`، وواجهة Cloudflare.
- **المسارات:** 33 مسار UBOOR نصيًا عبر `index-gleMzSil` و`QRLocal` و`QRDocument` و`useExitGate` في النسخ التي راجعتها؛ `/api/verify/` من DMS مسار منفصل. ليست كل هذه المسارات مثبتة كخدمات فعّالة حاليًا.
- **اختبارات موجودة:** أحدث نتيجة اطلعت عليها لـ[GitHub Actions](https://github.com/abdulstarzeki001-sketch/Star-Cyber-Audit-iSH/actions/runs/42373159584) هي `success`. تغطي 3 حالات Unit في `tests/test_audit.py`، ولا تشمل الحالات الجديدة أدناه.

**ما لم يحدث:** لم يُرسل هذا التدقيق POST/GET إلى خادم حكومي، ولا جرت محاولة دخول أو تجاوز مصادقة/WAF، ولا فحص بيانات عملاء، ولا إثبات صلاحيات خادم أو توقيع وثائق. الدليل هو **منطق الواجهة فقط**. تأثير أي نتيجة على Backend **غير مثبت**.

## ملخص الأولويات

| المستوى | عدد الملاحظات | الوصف |
|---|---:|---|
| مرتفع | 4 | بيانات جلسة في Console، POST تشخيصي مكرر، خلط هويات، عرض سجل محلي بديل |
| متوسط | 11 | حدود عرض QR وDMS، فصل الجلسات، حفظ البيانات، ومشكلات تغطية أداة التدقيق |
| منخفض | 2 | مؤقت OTP في UI، وتقوية CSP |

> الترتيب يعبّر عن **أولوية إصلاح هندسية مشروطة**، وليس نتيجة CVSS أو ثغرة خادم مؤكدة.

## النتائج المفصلة

### SA-01 — طباعة التوكن في console (High)

- **المصدر:** [QRLocal](../../research/source-archive/2026-11-07/uboor/QRLocal-5TAaXbzM.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `console.debug("[QRLocal] auth token:",y.token)`.
- **التفسير والحدود:** إفشاء رمز جلسة داخل سجل المتصفح أو منصة تجمع Console إذا كانت موصولة؛ لا دليل على أن طرفًا آخر حصل عليه.
- **الإصلاح:** احذف طباعة الرمز وبيانات POST الخام؛ اكتفِ بمعرّف طلب اصطناعي ورمز HTTP.
- **الثقة:** Confirmed code pattern; impact unverified.

### SA-02 — إعادة تنفيذ POST في مسار الاستثناء (High)

- **المصدر:** [QRLocal](../../research/source-archive/2026-11-07/uboor/QRLocal-5TAaXbzM.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `catch ... fetch(.../local_form/read_doc_company,{method:"POST"...})`.
- **التفسير والحدود:** قد تتكرر عملية مسح أو تسجيل إذا نجح POST الأول خادميًا ثم فشلت معالجته محليًا؛ لا تأكيد لتكرار الفعل في الخادم.
- **الإصلاح:** احذف طلب التشخيص؛ استخدم تسجيل الأخطاء دون إعادة الإرسال أو مفتاح idempotency بدعم الخادم.
- **الثقة:** Confirmed code pattern; server effect unverified.

### SA-03 — احتمال خلط توكن الموظف وصاحب الشركة (High)

- **المصدر:** [Shared Axios client](../../research/raw-uploads/2026-11-07/index-gleMzSil(1).js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `interceptors.request.use ... t.headers.Authorization='Bearer ${nu().token}'`.
- **التفسير والحدود:** طلبات صاحب الشركة تمر عبر نفس عميل API الذي يستطيع كتابة توكن الموظف؛ قد يؤدي إلى خطأ 401/403 أو إسناد هوية غير مقصود، ولا يثبت تجاوز صلاحيات.
- **الإصلاح:** عميل Axios منفصل لكل هوية، أو الحفاظ على Authorization الصريح وعدم استبداله؛ لا تخلط تدفق logout.
- **الثقة:** Confirmed code pattern; role impact unverified.

### SA-04 — عرض سجل غير مطلوب عند غياب معرف المعاينة (High)

- **المصدر:** [QRDocument](../../research/source-archive/2026-11-07/uboor/QRDocument-BJwpoEJY.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `a.value=AA||x[0]||null`.
- **التفسير والحدود:** إذا لم تتطابق قيمة ID في الرابط، تعرض الواجهة أول سجل محلي بدل رسالة عدم العثور؛ قد تسبب التباسًا في المستندات.
- **الإصلاح:** مع وجود ID: اعرض المطابقة الدقيقة فقط، وإلا "المستند غير موجود"؛ اربط السجل بهوية الجلسة.
- **الثقة:** Confirmed code pattern; client display only.

### SA-05 — سجلات QR في localStorage دون عزل أو مدة احتفاظ (Medium)

- **المصدر:** [qrStore](../../research/source-archive/2026-11-07/uboor/qrStore-B8bgApfd.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `JSON.parse(localStorage.getItem("qr_readings")); a.unshift(t)`.
- **التفسير والحدود:** قد تبقى بيانات نتائج المسح بين جلسات المستخدم على نفس المتصفح، وقد يتضخم التخزين؛ لا يعني أن الخادم يسمح بقراءة سجلات الغير.
- **الإصلاح:** إيقاف حفظ البيانات الحساسة؛ أو تقليل الحقول، تحديد TTL وعدد السجلات وتقسيم التخزين بحسب الحساب ومسحه عند الخروج.
- **الثقة:** Confirmed local data behavior.

### SA-06 — QR بصري بديل من رقم الوثيقة وخدمة خارجية (Medium)

- **المصدر:** [AchievementDocument](../../research/source-archive/2026-11-07/uboor/AchievementDocument-DEzIzJ3I.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `o.qr_code||o.doc_id||o.doc_number ; quickchart.io/qr?text=`.
- **التفسير والحدود:** يمكن إنشاء صورة QR من معرّف عادي، وإرسال قيمته لخدمة خارجية عند فشل التوليد المحلي. ذلك لا يؤكد توقيعًا رسميًا.
- **الإصلاح:** اعرض QR المعتمد المعاد من الخادم فقط، مع تمييز واضح عند غيابه؛ تجنب مولدات QR الخارجية للبيانات الحساسة.
- **الثقة:** Confirmed code pattern; verification meaning unsupported.

### SA-07 — الاعتماد على HTTP 200 كإشارة نجاح كافية (Medium)

- **المصدر:** [Exit gate](../../research/source-archive/2026-11-07/uboor/useExitGate-BvHNutwH.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `if(r.status===200){ w(...); ... return !0 }`.
- **التفسير والحدود:** قد تظهر رسالة نجاح رغم وجود رفض منطقي في جسم الاستجابة إذا كان الخادم يعيد HTTP 200 مع success:false.
- **الإصلاح:** طبّق تحققًا وفق عقد API الرسمي (مثل success/status/document) وتحقق من البيانات المطلوبة قبل التنقل.
- **الثقة:** Confirmed code pattern; backend contract unknown.

### SA-08 — نتيجة /api/verify/ لا تتأكد من حالة HTTP (Medium)

- **المصدر:** [DMS /qrpubliclink](../../research/raw-uploads/2026-11-07/6439.3d46893d(1).js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `x.onload ... JSON.parse(x.responseText); s.doc=d.document||null`.
- **التفسير والحدود:** وجود document في JSON يكفي لإظهار Valid بصرف النظر عن HTTP status في هذا المكون؛ لا يثبت إمكان تزييف رد فعلي من الخادم.
- **الإصلاح:** تحقق من حالة HTTP ومن معيار صحة موثّق قبل عرض Valid؛ تعامل مع الردود غير المتوقعة كغير مؤكدة.
- **الثقة:** Confirmed code pattern; backend contract unknown.

### SA-09 — خطأ 401 يطلق إنهاء جلستين مختلفتين (Medium)

- **المصدر:** [Owner/employee sessions](../../research/raw-uploads/2026-11-07/index-gleMzSil(1).js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `if(s===401){ e.logout(); n.logoutOwner(); }`.
- **التفسير والحدود:** انتهاء صلاحية توكن إحدى الجلستين يُخرج المستخدم من الأخرى، ويعقّد التشخيص.
- **الإصلاح:** افصل معالجة 401 حسب نوع الجلسة التي أرسلت الطلب، ولا تنفذ logout عامًا.
- **الثقة:** Confirmed code pattern; client-side only.

### SA-10 — مسار تسجيل الدخول قد يستخدم اسم Route غير موجود (Medium)

- **المصدر:** [QRLocal routing](../../research/source-archive/2026-11-07/uboor/QRLocal-5TAaXbzM.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `I.push({name:"Login"}) vs route name "LoginView"`.
- **التفسير والحدود:** قد يفشل الانتقال عند انعدام جلسة المستخدم إذا لم توجد خريطة بديلة للاسم.
- **الإصلاح:** استخدم اسم route المعرف فعلاً واختبر سيناريو الوصول بدون توكن.
- **الثقة:** Confirmed code pattern; no live route test.

### SA-11 — QR احتياطي من بيانات السيارة أو السائق (Medium)

- **المصدر:** [CompanyOwnerView](../../research/raw-uploads/2026-11-07/company-owner-vite/companyownerview-cjdszkn6.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `license_approval_number||vehicle_number||driver_name ... quickchart.io/qr`.
- **التفسير والحدود:** قد ينتج QR بصري يوهم بأنه رمز مستند، وينقل معلومة واردة في الرمز إلى طرف خارجي.
- **الإصلاح:** لا تصنع رمزًا يوحي بالاعتماد الرسمي من حقول نصية؛ أظهر بوضوح غياب QR المعتمد.
- **الثقة:** Confirmed code pattern; no server validity inference.

### SA-12 — إرسال لقطة PNG آليًا إلى Backend (Medium)

- **المصدر:** [QRDocument](../../research/source-archive/2026-11-07/uboor/QRDocument-BJwpoEJY.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `auto_send ... BorderPort_HS/path-document-file`.
- **التفسير والحدود:** قد ترسل الصفحة لقطة تحتوي بيانات مستند عند تشغيل auto_send؛ قواعد الصلاحيات والاحتفاظ غير ظاهرة في هذه الملفات.
- **الإصلاح:** وثّق شروط تشغيل auto_send، واحصره بصلاحيات محددة في الخادم، وقلل البيانات المعاد إرسالها.
- **الثقة:** Confirmed code pattern; upload authorization not tested.

### SA-13 — تصنيف خاطئ لأجزاء Webpack صالحة (Medium)

- **المصدر:** [Star Cyber Audit analyzer](../../analyze.py) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `classify() only matches export/import/const/function tokens; 6439.js and 2752.js are classified UNKNOWN_NOT_VERIFIED`.
- **التفسير والحدود:** نتائج الفحص المحلي قد تفوّت ملفات JavaScript فعلية رغم وجود امتداد .js.
- **الإصلاح:** اقبل ملفات .js المعروفة بعد رفض HTML/JSON/WAF، وأضف عينات اختبار Webpack.
- **الثقة:** Confirmed scanner design gap.

### SA-14 — المسح لا يجتاز المجلدات الفرعية (Medium)

- **المصدر:** [Star Cyber Audit analyzer](../../analyze.py) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `directory.iterdir() / sorted(directory.iterdir())`.
- **التفسير والحدود:** عند إعطائه مجلد جذر المشروع، لا يفحص ملفات JS الموجودة في research/*/* أو تحت مجلدات أخرى.
- **الإصلاح:** استخدم rglob مع استثناء .git/node_modules وإضافة حد للحجم/عدد الملفات.
- **الثقة:** Confirmed scanner design gap.

### SA-15 — قواعد API ثابتة لا تتعرف على DMS (Medium)

- **المصدر:** [Star Cyber Audit analyzer](../../analyze.py) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `PAT_API only matches local_form|support_org|BorderPort_HS|carrier_register`.
- **التفسير والحدود:** يتجاهل مسار DMS /api/verify/ والمسارات التي تُركّب في runtime أو تظهر باسم مختلف.
- **الإصلاح:** وسّع أنماط API وأضف اختبار /api/verify/ مع الإبلاغ عن التغطية واحتمال false positives.
- **الثقة:** Confirmed scanner design gap.

### SA-16 — مؤقت OTP مدته 60 ثانية في المتصفح فقط (Low)

- **المصدر:** [OTP UI](../../research/raw-uploads/2026-11-07/batch-042044/loginview-czys-bdx(20261107-042043).js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `l.value=60; loginWithOtp(); sendOtp()`.
- **التفسير والحدود:** إغلاق واجهة إعادة الإرسال ليس دليلًا على انتهاء صلاحية رمز OTP لدى الخادم أو حماية ضد الإساءة.
- **الإصلاح:** تعامل مع سياسة انتهاء OTP وrate limiting كقرار خادمي؛ اختبر UI وفق رسائل الخادم.
- **الثقة:** UI behavior confirmed; backend policy not tested.

### SA-17 — CSP يسمح بالنصوص البرمجية inline (Low)

- **المصدر:** [Cloudflare Worker](../../site/worker.js) (شيفرة مجمّعة؛ قد تكون معظمها في سطر واحد).
- **الدليل من الواجهة:** `script-src 'unsafe-inline'; style-src 'unsafe-inline'`.
- **التفسير والحدود:** يعتمد أمان إدخال بيانات المستخدم على استخدام textContent الحالي؛ أي إدخال HTML غير آمن مستقبلاً يزيد مخاطر XSS.
- **الإصلاح:** انقل الشيفرة إلى ملف/وحدة خارجية واستخدم سياسة CSP أقوى، واحتفظ باستخدام textContent.
- **الثقة:** Observed in Worker source; no injection demonstrated.

## خريطة التدفقات المستنتجة من الشيفرة

```text
UBOOR / Vue/Vite (واجهة A)
  login employee -> employee token -> shared Axios client
  company_verify_login -> company_verification -> company_owner_token
  QRLocal scanner -> POST local_form/read_doc_company -> qrStore(localStorage)
                                               -> QRDocument preview
  Exit gate -> POST support_org/read_qr_exitgate -> AchievementDocument
  CompanyOwnerView -> return_company_doc -> ShipmentDoc/QR rendering

DMS / Webpack (واجهة B مختلفة)
  /qrpubliclink?code=... -> GET /api/verify/<code> -> response.document
  /ReadQrWithUR -> شاشة مرتبطة بمسار QR (منطقها ليس تحققًا مستقلًا هنا)
```

هنا لا توجد أدلة تسمح بدمج رموز UBOOR وDMS أو افتراض أنهما يستخدمان قاعدة تحقق واحدة.

## خطة الإصلاح المقترحة

1. **P0 — حماية البيانات:** حذف `console.debug(token)` وطلب `fetch(... POST ...)` التشخيصي. مراجعة أي logging مركزي موجود في التطبيق.
2. **P0 — عزل الأدوار:** إنشاء `employeeClient` و`ownerClient` لكل منهما التوكن و401/logout خاص به، مع اختبارات طلب موظف وطلب صاحب شركة متزامنين.
3. **P1 — صحة المعاينة:** منع fallback إلى `x[0]` إذا كان ID محددًا وغير موجود، وتقليل أو إيقاف `qr_readings` مع TTL وتجزئة بحسب هوية المستخدم.
4. **P1 — معنى QR:** عرض صورة رمز QR الصادرة عن النظام المعتمد فقط؛ وسم أي رمز تجريبي بشكل صريح، وتجنب QuickChart للنصوص الحساسة.
5. **P1 — عقد الاستجابة:** تحقق صريح من حالة HTTP وحالة نجاح الوثيقة وفق عقد الخادم بدل الاكتفاء بـ200 أو وجود حقل `document`.
6. **P1 — إصلاح أداة التدقيق:** إدخال ملفات Webpack في التصنيف، وفحص المجلدات المتداخلة، ودعم `/api/verify/`، وإضافة اختبارات regression.
7. **P2 — الامتثال:** المستودع عام ويحتوي أصولًا Frontend لجهات خارجية. راجع حق إعادة توزيعها، واحتفظ بمحتوى حساس أو شخصي في مخزن خاص فقط.

## اختبارات قبول مقترحة (دون استخدام خادم حكومي)

- محاكاة خطأ POST: يتم إرسال POST مرة واحدة فقط ولا يسجّل Console أي توكن.
- وجود توكن مالك وتوكن موظف في واجهة تجريبية: كل طلب يحمل توكن الدور الصحيح.
- فتح `/QRDocument?id=missing`: يعرض «المستند غير موجود» بدلاً من سجل آخر.
- `localStorage.qr_readings` تالف أو قديم: لا ينهار التطبيق ولا يعرض بيانات مستخدم سابق.
- JSON من DMS يحوي `document` لكن status فشل: لا تظهر كلمة `Valid` مطلقًا.
- إدخال ملف `6439.3d46893d.js` إلى المحلل: يُصنّف JavaScript، ويستخرج `/api/verify/`.
- تشغيل المحلل على مجلد يحتوي ملف JS داخل مجلدين فرعيين: يَظهر الملف في التقرير.
- الصفحة في Cloudflare: استيراد `analysis.json` لا يرسله إلى الخادم (تحقق عبر Network tab في بيئة اختبار).

## حدود التحقق والمراجع

- المراجعة مبنية على ملفات GitHub المحفوظة في **7 نوفمبر 2026** وعلى اختبارات GitHub Actions الحالية.
- لم يتم تقييم شفرة Backend ولا عقود APIs الرسمية ولا قيود IAM، وبالتالي لا توجد دعوى عن ثغرات خادمية.
- بعض أسماء الحزم بين `index-gleMzSil`، `index-D1j-Jb9C`، `index-CSEaOmaL` و`index.801a60b0` تدل على إصدارات/أنظمة منفصلة؛ لا يُفترض تكافؤها.
- **حالة التقرير:** نتائج ثابتة قابلة لإعادة الفحص من الشيفرة المرفوعة؛ يُرجى التمييز بين السلوك الظاهر والتأثير المحتمل.
