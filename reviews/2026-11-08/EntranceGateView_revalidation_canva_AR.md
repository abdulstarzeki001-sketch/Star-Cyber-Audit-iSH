# إعادة فحص EntranceGateView وربطه بـCanva

**التاريخ:** 8 نوفمبر 2026
**الملف:** `EntranceGateView-B9IBJo4k.js`
**الحجم:** 21,501 بايت
**SHA-256:** `d48910ae500903a80deaf740cba67485c76e3af789fcff2e1f4d6f86d2419988`
**النتيجة:** مطابق للنسخة المفحوصة سابقًا؛ لا يوجد فرق بايتات.
**الحدود:** مراجعة ثابتة لواجهة عميل، دون تنفيذ أي طلب إلى خوادم حكومية.

## كيف يعمل؟

1. يبدأ `EntranceGateView` الكاميرا باستخدام `getUserMedia`، وينقل إطارات الفيديو إلى Canvas ثم `jsQR`.
2. يجلب الإحداثيات من الحالة المشتركة. يطلب عبر `POST carrier_register/scrape_search_goods_gateway_register`، ويرسل `url` و`x_coordinate` و`y_coordinate`.
3. عند HTTP 200 مع `response.data.Agent_name` يضع البيانات في `goodsData` ويقرأ `hash_id`.
4. يظهر زر القرار عند صلاحية الواجهة `gateway_decision` وحالة `غير محددة`.
5. يجمع `EntranceGateModel` قرار `APPROVED` أو `REJECTED`، والسبب ومرفقات JPEG أو الملفات المختارة.
6. يرسل `POST carrier_register/gateway_decision` كـ`FormData` وفيه `hash_id` و`decision` و`decision_reason` والإحداثيات و`attachment[index]`.

## نتائج تأكدت منها في المصدر الأصلي

| ID | الملاحظة | حدود الأثر |
|---|---|---|
| EG-R01 | شرط الكاميرا `!x.startsWith("http")||!x.startsWith("https://")` يعادل اشتراط HTTPS؛ الإدخال اليدوي لا يستعمل الشرط نفسه | عدم تماثل تحقق الواجهة، لا إثبات قبول Backend |
| EG-R02 | عند بدء بحث جديد لا يُصفَّر `goodsData` قبل الطلب | قد يبقى مستند سابق ظاهرًا عند فشل البحث |
| EG-R03 | قبول رد البيانات يعتمد على HTTP 200 و`Agent_name` دون Schema كامل | احتمال عرض أو رفض بيانات جزئية |
| EG-R04 | يظهر زر القرار إذا وجد `gateway_decision` و`status="غير محددة"`، لكن معالج الإرسال لا يعيد فحصهما | UI permissions ليست بديلًا عن تفويض الخادم |
| EG-R05 | بعد `await POST gateway_decision` تعرض الواجهة عبارة «تم إرسال قرار الموافقة بنجاح» حتى عند اختيار `REJECTED` | خطأ نص واجهة مثبت |
| EG-R06 | `latitude&&longitude` يستبعد القيمة الرقمية صفر | عدم دقة GPS في حالات محددة |
| EG-R07 | الإدخال اليدوي ينفذ `await V(M.value.trim()),M.value=""` | يمسح الإدخال بعد نتيجة بحث `false` بلا استثناء |
| EG-R08 | لا يُفحَص `hash_id` صراحة قبل إرسال FormData؛ المصدر يتحقق من `goodsData` | يلزم اختبار رد ناقص بصورة اصطناعية |
| EG-R09 | التقاط الصور إلى `image/jpeg` ورفع `attachment[index]`؛ لا تظهر قيود حجم/نوع ضمن معالج الإرسال | سياسات الملفات على الخادم غير معروفة |
| EG-R10 | يوقف `requestAnimationFrame` ومسارات الفيديو عند التنظيف | سلوك إيجابي لإدارة الموارد |
| EG-R11 | مساران متزامنان للبحث قد يغيران `goodsData` دون حارس أحدث طلب ظاهر | فرضية سباق، تحتاج اختبارًا محليًا |

## الاعتماديات التي ما زلنا نحتاجها

- `useAttachments-YD2hRx7D.js` — تنزيل المرفقات.
- `StationsDetailsModal.vue_vue_type_script_setup_true_lang-CppuJXhm.js` — بيانات المحطات.
- `jsQR-CKtgBSaS.js` — مكتبة QR المدمجة في هذا الإصدار.
- `index-gleMzSil.js` — سياق Axios والمصادقة (مراجع ومؤرشف مسبقًا).

## مصدر GitHub ومراجعاته

- [التقرير التفصيلي السابق](EntranceGateView_deep_review_AR.md)
- [فاحص الملفات المحلي](../../tools/ish/gate_views_review.py)
- [الاختبارات الاصطناعية](../../tests/test_gate_views_review.py)
- [Manifest للبصمات](qr-uboor-10-files-batch-2/manifest.json)
- [مستودع المشروع](https://github.com/abdulstarzeki001-sketch/Star-Cyber-Audit-iSH)

**Canva:** يمكن استيراد هذا التقرير من عنوانه العام في GitHub إلى تصميم Canva قابل للتحرير. لا توجد مزامنة ثنائية تلقائية للكود. لا تنشر توكنات أو ملفات حكومية أصلية في Canva.