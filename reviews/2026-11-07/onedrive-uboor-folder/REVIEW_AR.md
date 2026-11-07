# تحليل مجلد OneDrive — لقطات UBOOR

**التاريخ:** 7 نوفمبر 2026  
**المصدر:** [مجلد OneDrive الذي شاركه المستخدم](https://1drv.ms/f/c/c39a63f918f32793/IgA2nSQ7b_hOTbUREmsIQezrAWpZV0ErGJuuREHOd_UlhBo)

## نتيجة الوصول

تم فتح رابط المشاركة بنجاح وتحديد المجلد **`customs-uboor.ur.gov.iq+_1772003025841`**. رُصد **8 ملفات** إجمالًا (6 HTML و2 PNG) ضمن مجلد `customs-uboor.ur.gov.iq` ومجلداته الفرعية. وُجد مجلد `ur.gov.iq/js` بلا ملفات ظاهرة.

**هذا تقرير مشتق من المصدر:** لم تُنسخ صفحات HTML الخام أو صور الجهة الثالثة إلى GitHub العام، لاحتواء بعض الأسماء والصفحات على رموز QR طويلة، ورقم هاتف، واسم ومعلومات تواصل شخص أو شركة. تمت تسمية الملفات الحساسة بأسماء منقحة في هذا الجرد فقط.

## جرد المرفقات

| المسار المنقّح | الحجم | القرار |
|---|---:|---|
| `customs-uboor.ur.gov.iq/index.html` | 19436 B | فهرسة فقط — contains contact information |
| `customs-uboor.ur.gov.iq/_downloads.html` | 1883 B | فهرسة فقط — contains opaque QR values and phone references |
| `customs-uboor.ur.gov.iq/company-owner/index.html` | 21241 B | فهرسة فقط — contains person or company identifiers, email and phone |
| `customs-uboor.ur.gov.iq/company-owner/index_code_[REDACTED].html` | 19185 B | فهرسة فقط — opaque QR token in original filename; client error snapshot |
| `customs-uboor.ur.gov.iq/company-owner/index_phone_[REDACTED].html` | 1 B | فهرسة فقط — phone number in original filename and no useful content |
| `customs-uboor.ur.gov.iq/user-auth/index.html` | 19581 B | فهرسة فقط — login form snapshot; frontend-only evidence |
| `customs-uboor.ur.gov.iq/images/customes-logo.png` | 90851 B | فهرسة فقط — third-party logo asset |
| `customs-uboor.ur.gov.iq/images/ur-logo.png` | 19094 B | فهرسة فقط — third-party logo asset |

## التحليل الوظيفي للصفحات

1. **الصفحة الرئيسية:** تعرض واجهة UBOOR TECH، وتحمّل `index-cseaomal.js` و`index-iqgxgunl.css`. تتضمن رابطًا إلى تسجيل الدخول ومعلومات اتصال عامة.
2. **واجهة صاحب الشركة:** تعتمد على `index-ccmhdhtn.js` و`companyownerview-cjdszkn6.js` ومكونات أخرى. تتضمن نموذج إدخال **Hash Code عبر SMS**، كما تتضمن بيانات تعريف واتصال موجودة في لقطة HTML.
3. **لقطة التحقق من صاحب الشركة:** تظهر رسالتي «حدث خطأ أثناء التحقق من صاحب الشركة» و«خطأ في السيرفر» مع زر دخول عبر بوابة أور. هذه حالة واجهة محفوظة، ولا تثبت السبب الحقيقي للخطأ في الخادم.
4. **صفحة تسجيل الدخول:** تشتمل حقلي اسم مستخدم وكلمة مرور، وتستدعي `loginview-czys-bdx.js` وعدة مكونات نماذج؛ لا تكشف لقطة HTML وحدها قواعد التحقق من OTP أو سياسات المصادقة الخادمية.
5. **`_downloads.html`:** يبدو فهرسًا محفوظًا لمصادر تم تنزيلها، لكنه يحوي قيم QR وأرقام هواتف؛ لا يصلح للنشر الخام.
6. **الصور:** `customes-logo.png` و`ur-logo.png` موجودتان في مجلد images لكن لم تُحلل البايتات ولم تُرفع للـGitHub العام.

## الاعتمادات الناقصة عن مستودع Star Cyber Audit

بالمقارنة الاسمية مع شجرة `Star-Cyber-Audit-iSH`، **لا توجد ملفات في GitHub تحمل الأسماء التالية**:

```text
index-cseaomal.js
index-ccmhdhtn.js
index-iqgxgunl.css
card-cxdtecyo.js
textarea-bgo3bjb3.js
table-dtmqfnp9.js
basemodal-c8lwmuhw.js
vue3-treeselect.min-c1blx3zb.js
form-ldzoexkp.js
schemas-b4dorvt-.js
uboor-banner.jpeg
customes-logo.png
ur-logo.png
```

هناك **10 أصول JS/CSS و3 صور** بأسماء غير موجودة في المستودع؛ صورتا الشعار موجودتان داخل OneDrive، أما ملفات JavaScript/CSS المشار إليها فليست ضمن الملفات الثمانية في المجلد المشارك. عدم تطابق الاسم لا يثبت عدم وجود نفس المحتوى تحت اسم آخر.

## توصيات المراجعة

- حافظ على الملفات الأصلية داخل OneDrive، ولا تنشر `code=` أو `phone=` ضمن أسماء عامة أو سجلات.
- قبل محاولة إعادة بناء واجهة محلية، اجمع النسخ المرخّصة من ملفات JS/CSS المشار إليها بالمسارات النسبية؛ الصفحات الحالية وحدها **لا تشكل تطبيقًا مستقلًا**.
- تعامل مع رسالة «خطأ في السيرفر» كرسالة واجهة فقط؛ لا تفترض خللًا في التوقيع أو QR أو صلاحيات الخادم.
- عند إجراء تدقيق مصرح به لمنظومة تملكها، استخدم بيئة اختبار وبيانات وهمية، ولا تعرض نموذجًا مطابقًا لبوابة حكومية على نطاق عام.
- رابط المشاركة نفسه كان قابلًا للفتح دون تسجيل دخول؛ إن كان يحتوي بيانات خاصة، راجع إعدادات المشاركة في OneDrive.

## حدود التقرير

مراجعة **ملفات ثابتة فقط**. لم يتم اختبار خوادم الجهات الأخرى أو تشغيل JavaScript أو تجاوز المصادقة. `file_count` يشمل ملف HTML ذي حجم 1B وليس صفحة قابلة للتحليل.
