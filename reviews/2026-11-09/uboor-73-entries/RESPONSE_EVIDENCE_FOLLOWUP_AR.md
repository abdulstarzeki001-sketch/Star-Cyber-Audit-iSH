# متابعة البحث عن استجابة وثيقة الشركة

9 نوفمبر 2026

راجعت المواد المرتبطة بطلب `return_company_doc` في المستودع وOneDrive ومساحة العمل. لم يظهر جسم الاستجابة المطلوب في المواد التي أمكن فحصها. يبقى الدليل التاريخي المتاح ترويسات طلب `POST` وحالة `200` ونوع محتوى معلن `application/json`. [تفريغ اللقطة 66](https://github.com/abdulstarzeki001-sketch/Star-Cyber-Audit-iSH/blob/51627d2089ae52ed2d09db708499250f3a564213/research/private-evidence/2026-11-09/UBOOR_ALL_73_IMAGES_COMPLETE_TEXT_2026-11-09%202.txt#L2017-L2044)

| المادة المفحوصة | النتيجة |
| --- | --- |
| ZIP المحفوظ لواجهة UBOOR في OneDrive | 39 ملفًا، واجتازت جميعها فحص CRC. الأنواع هي HTML وJavaScript وCSS وصور PNG وخطوط TTF. يظهر اسم المسار في ملفي JavaScript، ولم يظهر سجل HAR أو ملف JSON مستقل. |
| نسختا يناير داخل ZIP | تطابقت بصمة Git لملف `index-d1j-jb9c.js` مع `403167a1e3f5602da0b531ba2b8c99b1a52eec28`، ولبناء `companyownerview-dwbcwxr4.js` مع `d8ec976ea4eb4a8f68aeb9abab56bcd7e4290fbc`. يؤكد التطابق مصدر النسختين على مستوى البايتات. |
| حزم إضافية أعادها البحث | حزمة `index-cseaomal.js` داخل ZIP تشير إلى `CompanyOwnerView-BT9XbYQI.js`. الملف النصي الآخر في OneDrive يحتوي حزمة Vite تشير إلى `CompanyOwnerView-DWvqGtIJ.js`. كلا المقطعين يستدعيان المسار بجسم `null` ويتوقعان `doc_id` داخل `response.data.data`. |
| ملفات `dashboard*.devtools` و`qrpubliclink*.devtools` | أربعة ملفات، اثنان بحجم 847 بايت واثنان بحجم 839 بايت. فُحصت بايتاتها واتضح أنها أغلفة HTML. لا يظهر فيها المسار أو بنية سجل الشبكة. |

بصمة SHA-256 لنسخة ZIP المفحوصة هي `efaa3d95210210d41f8d6afc7c25b993a599f1a3cc88b2a0cd8c779f5a452ee1`. لم يُنفّذ JavaScript المؤرشف ولم يُرسل طلب إصدار إلى الخدمة.

الدليل المطلوب هو `Response` أو `Preview` للطلب نفسه، أو HAR منقّح يحتوي جسم الرد. تكفي بنية JSON وأسماء الحقول مع حجب قيم المصادقة ومعرّفات الشركة والسائق ورمز QR. لربط الصورة بالرد يلزم حفظ ترتيب الطلبين وبيانات `Initiator` أو مطابقة القيمة محليًا قبل حجبها. يظل التحقق من التوقيع والأصالة فحصًا مستقلًا.
