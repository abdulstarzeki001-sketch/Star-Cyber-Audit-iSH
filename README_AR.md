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
