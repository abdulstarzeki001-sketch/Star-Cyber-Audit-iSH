# التحليل الثالث: عشرة ملفات اعتماديات لبوابة الدخول، QR، والطباعة

**تاريخ المراجعة:** 8 نوفمبر 2026
**النطاق:** ملفات JavaScript مرفوعة من المستخدم، فحص ساكن عبر قراءة البايتات والمحتوى، دون تشغيل JavaScript حكومي أو الاتصال بواجهات API رسمية أو تمرير رموز وثائق حقيقية.
**سجل البصمات SHA-256 وGit Blob SHA-1:** [manifest.json](manifest.json).
**النتيجة:** ثمانية ملفات لم تكن ضمن الدفعات المفصلة السابقة، وملفان متطابقان بايتًا ببايت مع مراجعات سابقة. جميع الأحجام والتواقيع في manifest.

## 1. `jsQR-CKtgBSaS.js` — قراءة QR من صورة، لا إنشاؤه

- **130,725 بايت؛ SHA-256:** `7b28d8063265694524209c30a0b20471c0ae3f85cf5c260a469907740bcb28a4`.
- حزمة decoder تشمل BitMatrix، locator/extractor، إصلاح أخطاء Reed–Solomon، تفسير المحتوى النصي والبايتات؛ تعيد `data` و`binaryData` و`location` عند التعرف على الرمز وإلا `null`.
- تُستخدم في ماسحات بوابة الدخول والخروج و`QrLocalImporter` (الأخير يحمل أيضًا `BarcodeDetector`).
- تُظهر خيار `inversionAttempts`، ما يتيح محاولة تفسير ألوان الصورة المعكوسة. لا يقوم decoder بالتحقق من توقيع أو مصدر QR ولا يصل بذاته إلى أي endpoint حكومي.
- **حد الثقة:** نجاح `jsQR` يعني أن الصورة تحتوي حمولة قابلة للقراءة؛ ليس تصديقًا على وثيقة حكومية.

## 2. `StationsDetailsModal.vue_vue_type_script_setup_true_lang-CppuJXhm.js` — تفاصيل المحطات

- **2,550 بايت؛ SHA-256:** `8afe444c1fe2203397347394dd66b198ec611fc657f8907f933b6e78269d4b94`.
- يستورد `BaseModal-DjCaQzje.js`، ويقبل `isOpen` و`hashId` و`sections` و`attachmentsEntrance` و`attachmentsSonography`.
- يعرض أقسام `sections` عبر `section.title` و`Object.keys(section.details)`، ويصدر حدث `close`.
- يعرض زر تنزيل لمرفقات `entrance_gate` و`sonography_gate`. ينشئ حدث `download-file` بكائن `{path,station_name,hash_id}`. **لا يُصدر طلب الشبكة بنفسه**.
- **اكتشاف جديد عابر للملفات:** `EntranceGateView` يمرّر أيضًا `attachments-register: goodsData.register.attach_paths`، لكن المكوّن لا يعلن prop `attachmentsRegister` ولا يرسم قائمة للتسجيل. هذه المرفقات لا تظهر في الواجهة الحالية رغم تمريرها من الأب.
- **حدود التحمل:** استدعاء `Object.keys(section.details)` دون قيمة افتراضية قد يفشل إذا وصل section بلا `details`. من مصدر الأب الحالي، المصفوفة الأساسية تُبنى بقيمة details معروفة، لذا هو خطر عقد بيانات وليس فشلًا مثبتًا في التدفق المعتاد.
- استخدام `filePath.split("/").pop()` يفترض مسارًا نصيًا؛ ليس تحقّقًا من اسم الملف أو MIME.

## 3. `Modal-C_od4hhs.js` — مكوّن حوار عام

- **12,127 بايت؛ SHA-256:** `04830b150d5a6dda684a75c954409c44b5b1c1e2ecd685b198deb49217a25194`.
- حزمة واجهة تعتمد على DialogRoot/DialogContent/DialogOverlay/DialogClose، وتتحكم في open/close والضغط خارج الحوار وإغلاق Escape والحفاظ على التركيز عبر `trapFocus`.
- تنشئ `role="dialog"` و`aria-describedby` و`aria-labelledby` وتدعم أوضاع modal وغير modal.
- **ليس** مصدر طلب رفض/تعطيل مستند ولا يقرر امتيازات المستخدم. فحص صحة التفاعل والإتاحة يتطلب تشغيل مثال UI اصطناعي، ولا نستنتج سلامة نماذج الأعمال من مكتبة الحوارات وحدها.

## 4. `index-BKvq_4_A.js` — تحويل HTML إلى صورة

- **13,327 بايت؛ SHA-256:** `25bd2f9df43d5ed1ae182f1dd68d1c05f735a5352ce7fe9149af501a1c706f05`.
- ينسخ عنصر DOM وأطفاله والأنماط والخطوط والصور، ويستعمل SVG `foreignObject`، ثم يرسم على Canvas ويُخرج Blob. الصادر `Ut as t` ينفذ مسار `toBlob`.
- يقرأ موارد الصور والخطوط المطلوبة عبر `fetch`، مع خيارات cache و`fetchRequestInit` و`imagePlaceholder` و`cacheBust`.
- **قيود عملية:** صورة أو خط خارجي قد يفشل بسبب CORS أو قيود الشبكة؛ عندها يمكن ملؤه ببديل فارغ/placeholder مع `console.warn`، ما يجعل المستند المصدَّر ناقصًا بصريًا. يعالج أحجام Canvas كبيرة بخفض القياس بعد حدود داخلية (16384)، فليس كل حجم يطبع بالدقة المطلوبة.
- لا يصدر مستندًا رسميًا ولا يوقع QR، وحتى صورة PNG ناجحة ليست إثباتًا لأصالة الوثيقة.
- في ملفات واجهة أخرى، `QRDocument` قد يرفع لقطة PNG مشروطة بـ`auto_send`؛ هذه المكتبة لا تحتوي endpoint الرفع بذاتها.

## 5. `browser-3Qg8aFGH.js` — توليد QR

- **25,785 بايت؛ SHA-256:** `ac20dcd5e80b582864e38bd16a87f2068f938b6b32785f5ddd5a4b9ed7b3e0af`.
- حزمة توليد QR تحتوي تصحيح أخطاء وأنماط QR وطرق `create` و`toCanvas` و`toDataURL` و`toString`. دالة `toDataURL` تستخدم Canvas وتختار `image/png` افتراضيًا.
- مصدر تكوين صورة `ShipmentDoc` عند توفر `doc.qr_code`، وعند fallback من رقم الإجازة أو المركبة أو السائق؛ هذا fallback **معلوماتي فقط**.
- أي نص يمكن ترميزه إلى صورة QR. هذه الوحدة ليست نظام تحقق أو تشفير حكومي، ولا تحتوي منطق إصدار مفاتيح رسمية.
- **ملاحظة:** لا تخلط `toDataURL` هنا مع `toBlob` في `index-BKvq_4_A`: الأولى ترسم QR، والثانية تصوّر عنصر HTML.

## 6. `Select-DZpjzzNJ.js` — قائمة اختيار

- **34,010 بايت؛ SHA-256:** `0c230f2ecf805c6253fbe14adc9ce43944a85074b098024a2513f2fd4a348254`.
- مكوّن Select واجهي، يدعم `modelValue`، و`defaultValue`، و`multiple`، و`by` للمقارنة، والبحث باختصارات لوحة المفاتيح، وقيود `required/disabled`.
- يعتمد على `useFormControl-XQpg82Ny.js`، ويستخدم Select أصليًا مخفيًا/متزامنًا لتكامل النماذج.
- لا يكتب API ولا يحدد مخزون الشركات أو صحة QR. يشرح كيفية اختيار عناصر حقول السجل أو الشحنة، لكنه لا يثبت أن عقد تلك الخيارات صحيح لدى Backend.

## 7. `QrLocalImporter-DYzNB5Fh(2).js` — نسخة مطابقة لقارئ المستورد

- **7,222 بايت؛ SHA-256:** `59ff26bfbc4b731799101527e9604fc736c170e80e4988eb69be672990cf8208`.
- مطابق بايتًا ببايت للملف `QrLocalImporter-DYzNB5Fh(1).js` الذي حللناه سابقًا.
- قارئ كاميرا يستخدم `BarcodeDetector` مع `jsQR` fallback، ثم `useExitGate.searchImportedGoods` للحصول على نتيجة بوابة الخروج. تتولى تبعية `useExitGate` طلب `support_org/read_qr_exitgate`.
- **ليس نسخة أحدث** بمجرد لاحقة `(2)`؛ لا داعي لنشره مرتين.

## 8. `CompanyOwnerView-CIdFF3LL(3).js` — نسخة مطابقة لصاحب الشركة

- **24,517 بايت؛ SHA-256:** `78af159ff95bf493a5050b4fb0fe6e4068ee49576100829ce1783644f92d2b2d`.
- مطابق بايتًا ببايت للنسخ المراجعة سابقًا.
- يدير `AppUrLogin` و`CompanyOwnerView` و`CompanyOwnerItems` و`VSearchHashCode`، مع `company_item_reduce` و`return_company_doc` والعرض عبر `ShipmentDoc`.
- لم تتغير استنتاجاتنا: هذا عميل واجهة، ولا يكشف توقيع QR أو منطق إصدار وثيقة حكومية في الخادم.

## 9. `FormField-DW4k76E2.js` — حقول وتحقق النماذج في الواجهة

- **3,491 بايت؛ SHA-256:** `a88958cbe6ad3a4b53f9e4c93cc129553ecdae580144f96d6a60596aa84ccca7`.
- يعرض label وdescription وhint وhelp وأخطاء النموذج، ويقرأ سياق Validation لربط اسم الحقل برسالة الخطأ.
- يقبل `errorPattern`، `required`، `eagerValidation`، `validateOnInputDelay`، وUI variants.
- لا يرسل طلبًا حكوميًا ولا يطبق تحققًا خادميًا. وجود required هنا ليس دليلًا أن بيانات الرفض أو المرفقات خاضعة لقيود خادم.

## 10. `useAttachments-YD2hRx7D.js` — تنزيل ملفات المحطات

- **747 بايت؛ SHA-256:** `384aa93decf853b8135044a50511b472c7860c564e81467565b43b87ed40d173`.
- تصدّر `downloadAttachment(info)`. إذا غاب `info.hash_id` تعرض رسالة «معرف السجل غير متوفر».
- تطلب:
  `GET carrier_register/download_file`
  مع `params: {hash_id:info.hash_id,url:info.path,station_name:info.station_name}` و`responseType:"blob"`.
- تنشئ `URL.createObjectURL(new Blob([response.data]))` ثم رابط `a[download]`، وتحذف الرابط و`revokeObjectURL` بعد إطلاق النقر، وتعرض نجاحًا أو فشلًا.
- يستدعيها `EntranceGateView` عند استقبال حدث `download-file` الذي أطلقته `StationsDetailsModal`.
- **مسؤولية الخادم غير الظاهرة:** يجب أن يقيد `hash_id` و`url` و`station_name` بصلاحية المستخدم وتبعية الملف للسجل، ويحدد الحجم والنوع المسموحين. لا يعني قبول المعاملات في العميل أن الخادم يثق بها دون تحقق.
- واجهيًا لا يُفحص `info.path` قبل استخدام `split`، ولا MIME/حجم Blob قبل حفظه؛ كما قد يختلف سلوك إلغاء Object URL الفوري بين المتصفحات في أحمال كبيرة، ويحتاج تجربة مستقلة.

## الربط الدقيق بعد استلام الملفات الجديدة

```text
EntranceGateView
  ├─ jsQR-CKtgBSaS -> QR النصّي
  ├─ carrier_register/scrape_search_goods_gateway_register -> goodsData
  ├─ StationsDetailsModal
  │    ├─ sections[]
  │    ├─ attachmentsEntrance[] -> download-file
  │    ├─ attachmentsSonography[] -> download-file
  │    └─ [MISSING PROP] attachmentsRegister[] (الأب يمرره، الابن لا يرسمه)
  │          ↓
  └─ useAttachments.downloadAttachment
          -> GET carrier_register/download_file -> Blob -> تنزيل

CompanyOwnerView -> company_item_reduce / return_company_doc -> ShipmentDoc
  └─ browser-3Qg8aFGH -> صورة QR محلية
QRDocument -> index-BKvq_4_A -> لقطة HTML / PNG
QrLocalImporter -> BarcodeDetector / jsQR -> useExitGate
واجهة النماذج -> Modal / Select / FormField
```

## ما لا يثبته هذا الفحص

- صحة توقيع QR أو فك Fernet أو آلية إصدار المستند رسميًا.
- صلاحيات الحكومة على تنزيل الملفات أو اتخاذ قرارات البوابة.
- أن الـBlob المسترجع يحتوي نوع الملف المتوقع بالفعل.
- أن اختلاف `attachments-register` يؤدي إلى فقدان سجلات خادمية؛ هو قسم عرض غير موجود في الابن.
- أن بقاء بعض الموارد خارج مجلداتنا يمنع عمل الموقع المنشور؛ هذه أرشفة مستقلة وليست نسخة تطبيق تشغيلية.

## ملفات ستكون أكثر فائدة في الدفعة التالية

1. `index-ccmhdhtn.js` — نسخة أخرى من دخول صاحب الشركة ومساراته.
2. `BaseModal-DjCaQzje.js` — تنفيذ النافذة المستخدمة تحديدًا في StationsDetailsModal.
3. `useFormControl-XQpg82Ny.js` — سياق نماذج Select.
4. `AppPagination.vue_vue_type_script_setup_true_lang-DzdlD2T5.js` — أحداث صفحات سجل QR.
5. `Input-XMNBc09N.js` و`Textarea-vxo1mVYX.js` — تفصيل إدخال نصوص وأسباب القرارات.

هذه ملفات واجهة وتبعيات؛ تفاصيل Backend الرسمية تحتاج توثيقًا/بيئة اختبار مخولة، وليس كلمات مرور أو توكنات حقيقية.
