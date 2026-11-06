# Star Cyber Audit — iSH / a-Shell

مختبر **تحليل ساكن للملفات العامة**، وليس منصة رسمية أو ماسح اختراق.
لا يرسل POST، ولا يسجّل الدخول إلى بوابة عبور، ولا يتجاوز Huawei WAF، ولا ينفّذ JavaScript الذي يجلبه.

## iSH

```sh
apk add python3 ca-certificates
mkdir -p /mnt/star-audit
mount -t ios . /mnt/star-audit
cd /mnt/star-audit
sh run.sh
```

إذا اخترت مجلدًا خاطئًا عبر Files، تأكد من ظهور run.sh بأمر `ls -la`.

## الأوضاع

```sh
sh run.sh --local ./my-files      # تحليل ملفات JS المحلية
sh run.sh --fetch                 # طلب أربعة أصول ثابتة عامة فقط
sh run.sh --fetch-all             # طلب 20 ملفًا عامًا مع فترة بين الطلبات
sh run.sh                         # تحليل النسخ المحلية offline_samples وdownloads إن وجدت
```

أي HTML يعيده Huawei WAF لا يحتسب JavaScript. لا تعِد المحاولة آليًا لتخطي نظام الحماية.

## التقارير

تُحفظ الملفات في `reports/`: 
`analysis.json`, `inventory.csv`, `api_paths.txt`, `review_flags.txt`, `report.html`, و`fetch_status.json` عند استخدام --fetch.

المؤشرات المستخرجة ليست إثباتًا لثغرات فعلية في الخادم. لا تشارك ملفات أصلية أو طلبات HTTP تحتوي بيانات دخول أو معلومات أشخاص.

## واجهة Cloudflare

الموقع المنشور واجهة عامة **للاطلاع على نتائج تجريبية وإدخال ملف analysis.json محليًا داخل المتصفح**.
لا يرفع الملفات إلى Cloudflare؛ الفحص المتقدم ببايثون يستمر داخل iSH أو الكمبيوتر.

## الدفعة المرفوعة للمراجعة — 7 نوفمبر 2026

- 6 ملفات JavaScript أصلية فُحصت محليًا + 4 تقارير مرجعية تاريخية.
- النتيجة: **8** مسارات API نصية ضمن الملفات الستة، و**20** ملاحظة مراجعة هندسية (ليست ثغرات مؤكدة).
- النتائج المنقحة مرفوعة في: [reviews/2026-11-07](reviews/2026-11-07/REVIEW_AR.md).
- البصمات موثقة في [source_manifest.json](reviews/2026-11-07/source_manifest.json) ومخرجات JSON في [analysis.json](reviews/2026-11-07/analysis.json).
- أربعة التقارير السابقة محفوظة في [reference](reviews/2026-11-07/reference).
- **حماية النشر:** لم تُنسخ ملفات JavaScript الحكومية الخام إلى المستودع العام. يمكن فحصها محليًا عبر `sh run.sh --local /path/to/js`، أو فتح ملف JSON في لوحة Cloudflare.
- لوحة Cloudflare الحالية تعرض هذه الدفعة تلقائيًا؛ ولا يستدعي الموقع الخادم الحكومي.
