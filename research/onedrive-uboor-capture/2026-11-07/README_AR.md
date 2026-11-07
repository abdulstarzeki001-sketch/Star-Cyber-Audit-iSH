# أرشيف OneDrive — محتويات مجلد UBOOR

**المصدر:** [مجلد OneDrive الذي حدده المستخدم](https://1drv.ms/f/c/c39a63f918f32793/IgA2nSQ7b_hOTbUREmsIQezrAWpZV0ErGJuuREHOd_UlhBo)  
**المجلد:** `customs-uboor.ur.gov.iq+_1772003025841`  
**تاريخ الجرد:** 7 نوفمبر 2026  
**العدد:** 8 ملفات فعلية (6 HTML و2 PNG)، ومجلد `ur.gov.iq/js` فارغ.

## الملفات — ملفًا ملفًا

| # | الملف المنقّح | الحجم الأصلي | المحتوى المثبت في الملف | ما نُشر في GitHub |
|---:|---|---:|---|---|
| 1 | [الصفحة الرئيسية `index.html.txt`](customs-uboor.ur.gov.iq/index.html.txt) | 19,436 B | صفحة UBOOR TECH؛ وصف الخدمة والتنقل؛ مرجع `index-cseaomal.js` | مصدر HTML نصّي منقّح |
| 2 | [فهرس التحميل `_downloads.html.txt`](customs-uboor.ur.gov.iq/_downloads.html.txt) | 1,883 B | قائمة تنزيل محلية تحتوي قيم QR وأرقام اتصال | مصدر نصّي مع إزالة القيم الحساسة |
| 3 | [صفحة الشركة `company-owner/index.html.txt`](customs-uboor.ur.gov.iq/company-owner/index.html.txt) | 21,241 B | بوابة صاحب الشركة ونموذج Hash Code عبر SMS ومرجع `index-ccmhdhtn.js` | مصدر نصّي مع حذف الاسم/الهاتف/البريد |
| 4 | [حالة فشل التحقق `qr-validation-error.html.txt`](customs-uboor.ur.gov.iq/company-owner/qr-validation-error.html.txt) | 19,185 B | «حدث خطأ أثناء التحقق من صاحب الشركة» و«خطأ في السيرفر» وزر دخول عبر بوابة أور | مصدر نصّي باسم آمن بدل `index_code=[REDACTED]` |
| 5 | [ملف شبه فارغ `empty-phone-file.html.txt`](customs-uboor.ur.gov.iq/company-owner/empty-phone-file.html.txt) | 1 B | محتواه حرف واحد فقط | حفظ الحرف مع إزالة رقم الهاتف من الاسم |
| 6 | [تسجيل الدخول `user-auth/index.html.txt`](customs-uboor.ur.gov.iq/user-auth/index.html.txt) | 19,581 B | نموذج اسم مستخدم وكلمة مرور ومرجع `loginview-czys-bdx.js` | مصدر HTML نصّي غير قابل للتنفيذ مباشرة |
| 7 | [صورة `customes-logo.png` — مرجع المصدر](customs-uboor.ur.gov.iq/images/customes-logo.png.source.md) | 90,851 B | شعار مُشار إليه في HTML | مرجع OneDrive؛ **ملف PNG الأصلي غير مرفوع إلى GitHub** |
| 8 | [صورة `ur-logo.png` — مرجع المصدر](customs-uboor.ur.gov.iq/images/ur-logo.png.source.md) | 19,094 B | صورة شعار مُشار إليه في HTML | مرجع OneDrive؛ **ملف PNG الأصلي غير مرفوع إلى GitHub** |

[مجلد `ur.gov.iq/js` الخالي من الملفات](ur.gov.iq/js/README.md)

## لماذا لم تُنشر البايتات الخام؟

تحتوي أسماء بعض الملفات والمحتوى على **رمز QR طويل، ورقم هاتف، واسم شخص، وبيانات اتصال**. المستودع عام؛ لذلك نُشرت صفحات HTML الست بصيغة `.html.txt` مع تنقيح القيم الحساسة، وحُفظت الصورتان بوصفهما مرجعَي OneDrive دون إعادة توزيع بايتات الشعارين.

أُعيد التحقق من ملفات HTML المنشورة بحثًا عن رموز QR الطويلة والبريد وأرقام الهاتف الظاهرة. **لا يشكل ذلك فحصًا آليًا شاملًا لكل المعلومات الشخصية**. لتعديل أو نشر الأصل دون تنقيح، استخدم مخزنًا خاصًا بعد تحديد الحقوق والصلاحيات اللازمة.

## ملاحظات التحليل

- الـHTML المجمّع **غير كافٍ لتشغيل تطبيق حكومي** دون ملفات JS/CSS referenced. تم توثيق المراجع الناقصة في [التقرير السابق](../../../reviews/2026-11-07/onedrive-uboor-folder/REVIEW_AR.md).
- رسالة الخطأ في صفحة الشركة تُثبت ما عُرض في لقطة المتصفح فقط؛ لا تبيّن سبب الفشل على الخادم.
- صورة QR التي تُنشأ أو تُعرض في الواجهة **ليست دليلًا على صلاحية مستند أو توقيع رسمي**.
- لم تُنفذ شيفرة الواجهات ولم تُرسل طلبات إلى الأنظمة الحكومية.

**الأرشيف للبحث الثابت وغير تابع للجهات الحكومية، ولا يجوز استخدامه كنسخة تحقق رسمية.**
