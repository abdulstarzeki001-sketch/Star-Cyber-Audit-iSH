# المرحلة الأولى — الأساس الأمني لـ Star Cyber Audit

**الإصدار:** Phase 1 / 2026-11-09  
**النطاق:** اختبارات محلية فقط. لا مصادقة مع خدمات حكومية، ولا إرسال POST، ولا تجاوز WAF، ولا فحص نطاقات حية.

## ما الذي أُضيف؟

| العنصر | المسار | الوظيفة |
|---|---|---|
| قواعد مراجعة ساكنة | config/security_rules.json | قواعد قابلة للتعديل ومراجعة GitHub |
| محرك القواعد | tools/security/rule_engine.py | تحليل محلي لأسطر الأكواد دون تشغيلها |
| كاشف الأسرار | tools/security/secret_scan.py | كشف مرشحات مفاتيح API والأسرار عالية الثقة دون طباعة القيم |
| مقارنة الأدلة | tools/security/compare_reports.py | مقارنة تقريرَي analysis.json وفصل الجديد عن المُعالَج |
| ملف الجرد الآمن | tools/security/core.py | حدود الملفات، استبعاد الرموز والملفات الكبيرة والروابط الرمزية |
| تشغيل iSH | tools/ish/phase1_security.sh | scan / test / compare |
| اختبارات انحدار | tests/test_phase1_security.py | اختبارات القواعد والخصوصية وعدم الاتصال بالشبكة |
| بوابة CI | .github/workflows/phase1-security.yml | تشغيل الاختبارات وقطع CI عند العثور على أسرار عالية الثقة |

## على iSH في الآيفون

شغّل الأوامر بعد جلب التغييرات إلى مجلد المستودع:

~~~sh
apk add python3 ca-certificates
cd /mnt/star-audit
sh tools/ish/phase1_security.sh test
sh tools/ish/phase1_security.sh scan
~~~

**المخرجات المحلية:**

- reports/security_rules.json: مؤشرات القواعد مع نوعها والمسار ورقم السطر والتوصية (من دون قصاصات مصدر).
- reports/secret_scan.json: مواقع المرشحات وأنواعها من دون عرض قيم المفاتيح.

مجلد reports/ موجود أصلًا في .gitignore، فلا ترفعه إلى GitHub. كود الخروج 2 من أداة الأسرار عند تشغيل --fail-on-secrets يعني أن المراجعة مطلوبة؛ لا تلتف على الفحص بل صحح السبب أو اضبط سياسة الكشف بعد مراجعة بشرية.

### مقارنة تحليل سابق بتحليل جديد

~~~sh
# احتفظ بنسخة محلية من تقرير التحليل الحالي قبل إعادة تشغيل المحلل
cp reports/analysis.json reports/before.json
sh run.sh --local research
sh tools/ish/phase1_security.sh compare reports/before.json reports/analysis.json
~~~

ستُكتب reports/change_comparison.json وreports/change_comparison.md، مع عدد الملفات الجديدة والمحذوفة والمتغيرة، وتغير مسارات API ومؤشرات المراجعة. المقارنة **لأدلة الواجهة المحفوظة فقط**، ولا تثبت ثغرات في Backend.

## قواعد المراجعة

القواعد الحالية SC-EVAL وSC-HTML وSC-POSTMSG وSC-STORAGE وSC-HTTP وSC-TLS وSC-SHELL وSC-QRFALLBACK هي *heuristics*: مؤشر ظهور النمط لا يعني تلقائيًا وجود ثغرة قابلة للاستغلال.

عند إضافة قاعدة إلى config/security_rules.json، حدد id فريدًا، وtitle وseverity وextensions وpattern وrecommendation. الحد الأقصى 100 قاعدة، وطول النمط لا يزيد عن 240 حرفًا. راجع تعبيرات Regex في Pull Request وأضف اختبارًا يثبت السلوك المتوقع، ولا تستخدم أنماطًا ثقيلة أو غامضة.

**نطاق القراءة الافتراضي:** ملفات المشروع المملوكة له (الأكواد والوثائق والإعدادات)، مع استبعاد research/ وreviews/ وdownloads/ وreports/ وoffline_samples/ والروابط الرمزية والملفات التي تتجاوز 1 MB. عند طلب تدقيق أدلة محلية مؤرشفة صراحة، تتوفر --include-evidence مع أدوات القواعد والأسرار.

للملفات الكبيرة أو JavaScript المصغّر قد لا تكفي حدود 4000 حرف من كل سطر في محرك القواعد؛ هذا قيد موثق لتجنّب الفحص غير المحدود، وليس ضمانًا بعدم وجود ثغرات.

## حماية سلسلة التطوير

يعمل Workflow الجديد على pull_request وعلى push إلى main، بصلاحية contents: read، ومن دون GitHub tokens محفوظة في checkout، ويشغّل جميع اختبارات unittest، وبوابة كشف الأسرار. مؤشرات القواعد لا توقف الدمج تلقائيًا لأنها تحتاج فحصًا بشريًا، لكن كشف الأسرار عالية الثقة يفشل CI.

**مهم:** نجاح GitHub Actions وحده لا يمنع الدمج ما لم يُضبط Branch Protection / Rulesets على main. اجعل فحص **Offline Security Gate** والفحص الحالي **test** من Required status checks وفق سياسة المستودع. لا تغيّر حماية الفرع قبل التأكد من أن الفحصين يعملان.

## ضوابط مهنية

1. لا تُرسل نتائج التحليل الخام أو مفاتيح API إلى خدمات AI لمجرد تشغيل هذه الأدوات؛ التنفيذ محلي تمامًا.
2. لا تُدخل مفاتيح حقيقية في ملفات test أو examples. استخدم قيماً تركيبية أو تجميع النصوص داخل الاختبارات.
3. إذا ظهرت نتائج عالية الثقة، دوّر المفتاح الذي كُشف وأزله من المصدر والسجل بالوسائل المناسبة، مع عدم كشفه في تقارير عامة.
4. هذه الحزمة لا تستبدل SAST متقدمًا مثل CodeQL أو Semgrep، ولا تُجري تحليلًا كاملًا لتدفق البيانات، ولا تدعي الالتزام بشهادة ISO 27001.
5. افصل بين نتائج الصنف heuristic والحوادث أو الثغرات المتحقق منها بالاختبار المخوّل.

## إعادة التحقق

~~~sh
python3 -m py_compile analyze.py tools/security/*.py
python3 -m unittest discover -s tests -v
sh -n tools/ish/phase1_security.sh
~~~

راجع GitHub Actions قبل الدمج في main. هذا التطوير لا يغيّر analyze.py أو run.sh أو الأرشيفات أو Worker المنشور.
