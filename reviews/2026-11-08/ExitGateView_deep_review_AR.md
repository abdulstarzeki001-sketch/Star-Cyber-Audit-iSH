# ExitGateView-D33Au6wp.js — تدقيق قارئ QR في بوابة الخروج

**المصدر:** ملف JavaScript المرفق من المستخدم بتاريخ 8 نوفمبر 2026.  
**الحجم:** 4,468 بايت؛ **SHA-256:** `4c7d47c65b845c7b00143dfed244f28435cf5e2c64d6da9330820b3b53fbdc52`؛ **Git Blob SHA-1:** `33cf453d5d99d15ed4e0f23720c5ec8c087c03ff`.  
**المنهج:** فحص ثابت محلي فقط؛ لم تُنفذ طلبات خادم حكومي ولم تُستخدم وثائق رسمية أو حسابات.

## 1. وظيفة المكوّن والاعتماديات

يصدّر Vue component واحدًا باسم `ExitGateView`. يعرض «بوابة الخروج» و«مسح رمز QR للبضائع المستوردة»، ويعتمد على:
- `jsQR-CKtgBSaS.js` لفك رمز QR من صورة فيديو.
- `navigator.mediaDevices.getUserMedia` لفتح الكاميرا الخلفية بدقة مفضلة 1280×720.
- `useExitGate-BvHNutwH.js` لتطبيق عملية `searchImportedGoods` وإدارة `isLoading`.
- وظائف Vue المستوردة من `index-gleMzSil.js`.

**ليس مسؤولًا بنفسه عن قرار خروج إداري أو إنشاء مستند أو طباعة.**

## 2. المسار الفعلي

```text
Start camera -> video -> hidden canvas -> jsQR
  -> if detected QR:
       stop camera, release tracks
       require startsWith("http://") or startsWith("https://")
       call useExitGate.searchImportedGoods(scannedText)
  -> composable searchImportedGoods:
       requires GPS coordinates from its own flow
       POST support_org/read_qr_exitgate {url,x_coordinate,y_coordinate}
       on successful response may navigate to AchievementDocument
```

توجد خانة إدخال يدوي تستدعي `searchImportedGoods(trimmedText)` مباشرة، دون المرور بفرع التحقق `http/https` في الكاميرا. لذلك يوجد اختلاف في شروط الواجهة، ولا نستنتج منه أي قبول خادمي لمدخل غير صالح.

لا يستخدم هذا المكوّن `BarcodeDetector`، ولا يضيف سجلًا إلى `qrStore` مباشرة. استيراد `qrStore` ضمن سلسلة dependencies ليس دليلًا على حصول كتابة.

## 3. إدارة موارد الكاميرا

- يفتح `getUserMedia` ويعيد تشغيل الإطارات باستخدام `requestAnimationFrame` و`canvas.getImageData` و`jsQR`.
- عند قراءة رمز، يوقف الكاميرا ثم يمرر النص إلى composable.
- عند إزالة الشاشة، يلغي `requestAnimationFrame` ويوقف مسارات الفيديو.
- في النسخة المحددة لا يظهر مسار `BarcodeDetector` أو تحجيم الإطارات قبل المعالجة؛ قد يرتفع استهلاك المعالج على الهواتف بدقة فيديو مرتفعة.

## 4. أخطاء وحدود موثوقية

| الملاحظة | دليل المصدر | التفسير المحدود |
|---|---|---|
| اختلاف URL بين الكاميرا والإدخال اليدوي | `startsWith(http/https)` في فرع scan فقط | الأفضل توحيد سياسة المدخل في الخدمة والخادم |
| إيقاف الكاميرا قبل طلب الشبكة | استدعاء `p()` في handler | فشل API يتطلب تشغيلها ثانية؛ ليس عيب صلاحية |
| قراءة كل إطار بدقة الفيديو | `canvas.getImageData` و`jsQR` | تكلفة أداء محتملة وليست ثغرة |
| لا يظهر GPS في هذا الملف | يفوض `searchImportedGoods` | مصدر الإحداثيات يراجع في `useExitGate` |
| لا يوجد إرسال API مباشر هنا | يستورد `useExitGate` | عنوان `read_qr_exitgate` موثق من ملفه وليس من هذا الملف |
| لا يوجد قرار إداري/رفع مرفقات | لا `FormData` أو `gateway_decision` | يختلف عن `EntranceGateView` |

## 5. مقارنة مع قارئات UBOOR الأخرى

- `EntranceGateView`: جلب بيانات بوابة الدخول عبر `carrier_register/scrape_search_goods_gateway_register` ثم يُتيح قرارًا `APPROVED/REJECTED` مع السبب و`FormData` ومرفقات عبر `carrier_register/gateway_decision`.
- `QRLocal`: ماسح المنتج المحلي يستخدم GPS و`local_form/read_doc_company` وينتقل إلى `QRDocument` عبر `qrStore`.
- `QrLocalImporter`: واجهة ماسح أخرى ترتبط أيضًا بـ`useExitGate`، لكن تختلف تفاصيل الكاميرا والتدفق.
- `AchievementDocument`: يعرض استمارة الناقل عند الرجوع من طلب الاسترجاع أو المسح، وليس مصدر صدور QR الموقّع.

## 6. التوصيات الدفاعية

1. وحّد قبول نوع/بروتوكول/وجهة URL في فاحص مدخل واحد مع تحقق خادمي مستقل؛ لا تجعل النص المدخل يدويًا يتجاوز شروط العرض.
2. بعد فشل `searchImportedGoods` أو عدم صلاحية QR، اعرض حالة خطأ واضحة مع زر إعادة تشغيل الكاميرا، دون تكرار الطلب نفسه تلقائيًا.
3. قيّد معدل معالجة الإطارات أو استخدم native detector عند توفره إذا كانت تجربة الهواتف بطيئة.
4. لا تعتبر مجرد الانتقال إلى `AchievementDocument` إثباتًا لصحة الوثيقة أو اعتمادها من الخادم.
5. راقب خصوصية بيانات GPS والاستجابة داخل composable الذي يملك طلب API الفعلي.

**الحدود:** لا يثبت هذا الملف كيف يتحقق خادم `support_org` من الرموز أو صلاحيات القراءة أو صحة وثيقة بعينها. التقرير لا يتضمن بيانات QR حقيقية أو نتائج عمليات حكومية.
