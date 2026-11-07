# تحليل UBOOR وربط iSH / a-Shell — 6 نوفمبر 2026

> مراجعة ساكنة للملفات العامة المنشورة. لا تُجرى طلبات تعديل للمنصة أو محاولة تجاوز WAF. الوقائع أدناه مستمدة من نص JavaScript الذي جُلب من مسارات assets العامة؛ سلوك خادم API نفسه غير مختبر.

## حالة الوصول إلى الأجهزة

- Remote Desktop Commander: الجهاز DESKTOP-16NTS4H مسجّل لكن اتصالاته الثلاثة كانت Offline وقت الفحص. لا توجد جلسة متاحة للتحكم فيه. لم يُتحكَّم في iSH أو a-Shell.
- الأداة المرفقة `uboor_audit_mobile.sh` هي بديل عملي يعمل في الجهاز محليًا، وتتحقق من أن النص المنزَل JavaScript وليس صفحة Huawei WAF. لا توفر تحكمًا عن بُعد بحد ذاتها.

## خريطة المكونات الموثقة

| الواجهة/المكتبة | الوظيفة المثبتة | API ظاهر في المصدر أو مكتبة مستدعاة |
|---|---|---|
| `QrLocalImporter-DYzNB5Fh.js` | كاميرا QR بوابة خروج المستورد؛ `BarcodeDetector` أو jsQR، منع تكرار محلي 3 ثوانٍ، قراءة موقع | يستدعي `searchImportedGoods` في `useExitGate`; هذا يستخدم `POST support_org/read_qr_exitgate` |
| `QrControlScan-M6uGJnR1.js` | عرض سجلات القراءات المحلية مع حقول البحث وتصدير Excel حسب الصلاحيات | المنطق في `useLocalCompany-DfV5kpAj.js` |
| `useLocalCompany-DfV5kpAj.js` | جلب السجلات، معاينة الوثيقة، تنزيل Excel، استخدام `qrStore` | `POST local_form/paginate_qrcode_reader2`, `POST local_form/return_doc_qrcode`, `POST local_form/download_qrcode_readers2` |
| `QRReadings-B-a3jcrk.js` | واجهة أخرى لسجل QR ذات أسماء API مختلفة | `POST local_form/pagination_qrcode_reader`, `POST local_form/return_doc_qrcode`, `POST local_form/download_qrcode_readers` |
| `QRCheckpoints-Brs0uL0-.js` | عرض `doc_reader_org_name`, `time_stamp` والإحداثيات من `read_doc`; لا يستدعي API بنفسه | لا يوجد |
| `qrStore-B8bgApfd.js` | تخزين سجل محلي تحت `localStorage['qr_readings']` | لا يوجد |
| `AchievementDocument-DEzIzJ3I.js` | استمارة الناقل، استرجاع تفاصيل، طباعة، توليد QR محلي من `qr_code` أو رقم الوثيقة | عبر `useExitGate`: `support_org/return_doc_qrcode_export` |
| `ExitGateView-D33Au6wp.js` | شاشة بوابة الخروج وتستخدم useExitGate | المنطق في `useExitGate` |
| `EntranceGateView-B9IBJo4k.js` | بوابة الدخول؛ واجهة تحتوي معالجة قرارات ومرفقات | لا يظهر مسار API صريح في هذا المكوّن، وتوجد تبعيات أخرى |
| `DisableDocument-AXBjrkYS.js` | واجهة مسح لتقديم طلب متعلق بتعطيل وثيقة | `local_form/reset_company_qrcode` |
| `RejectedLocalDocuments-CC07EpF_.js` | عرض وثائق محلية مرفوضة ومعاينتها | `local_form/return_doc_qrcode`، وقد توجد API أخرى مضمّنة بطرق غير ظاهرة في النص المباشر |
| `QRImported-C65Oqm1K.js` | ماسح QR مميز عن مستورد بوابة الخروج | `local_form/read_doc_company` |
| `QRHealthCertificate-Byvh35hk.js` | مسح QR الشهادات الصحية | `BorderPort_HS/read_doc_health` |

## فروقات مؤكدة

1. اسم `QrControlScan` قد يوحي بالمسح المباشر، لكنه واجهة سجل لا تُشغّل الكاميرا. الماسح الفعلي للمستورد عند الخروج هو `QrLocalImporter`.
2. واجهتا `QrControlScan` و`QRReadings` تستدعيان نقاط API مختلفة لقوائم القراءات والتنزيل؛ `paginate_qrcode_reader2` مقابل `pagination_qrcode_reader`، و`download_qrcode_readers2` مقابل `download_qrcode_readers`. لا تُدمج الأسماء بالتخمين.
3. صلاحيات الواجهة: `download_qrcode_readers2` لتصدير سجل `QrControlScan`، و`return_doc_qrcode` للمعاينة. إخفاء/إظهار أزرار الواجهة ليس دليلًا على تطبيق الصلاحية في الخادم.
4. وظيفة المعاينة في `useLocalCompany` ترسل `doc_number:Number(r)` وقد تضيف `company_type`، وتحفظ نسخة معاينة في `qrStore` و `sessionStorage['qr_preview_entry']`، ثم تنتقل إلى `QRDocument`.
5. الوظيفة `loadReadings` في `useLocalCompany` تزرع ثلاثة إدخالات تجريبية من النوع `QRCODE:...` إذا لم يوجد المفتاح المحلي `qr_readings`. لا يجوز اعتبار هذه الإدخالات سجلًا رسميًا للخادم.
6. `QrLocalImporter` يحاول تمرير الإحداثيات قبل استخدام `searchImportedGoods`، لكن `useExitGate` يطبّق شرط توفر الإحداثيات في المسار المعني. لا يمكن التحقق من صحة الإحداثيات من العميل وحده.
7. `QRHealthCertificate` يتعامل مع حالة HTTP 402 بوصفها انتهاء صلاحية على مستوى الواجهة، ويحتفظ ببيانات الطباعة في `sessionStorage['hc_print']`. لا يثبت سياسة خادم رسمية لصلاحية الوثائق.
8. `QRCheckpoints` يمكنه استرجاع معلومات قراءة من `history.state`، ثم `sessionStorage`، أو من بيانات `route.query`؛ ومعرف الوثيقة لا يُطابق في هذا المكون قبل العرض. يعد ذلك خطر اختلاط بيانات عرض محلية، وليس دليلًا على فساد سجل الخادم.

## مستويات الإثبات

- **مثبت من مصدر JavaScript العام**: أسماء المكوّنات، مسارات الطلب المضمنة في الشيفرة، الحقول، شروط الواجهة، التخزين المحلي.
- **غير مثبت**: طبيعة ضوابط الخادم، صحة الوثائق المرسلة، خوارزمية توقيع QR الحكومي، آلية إدراج السجل الرسمي، صلاحية الرموز أو طريقة اعتمادها، أو إمكانية استغلال أي خلل في بيئة الإنتاج.
- **WAF**: HuaweiCloudWAF يعيد HTML أحيانًا بدل JS. تنزيل HTML إلى اسم `.js` لا يحوله إلى مصدر JavaScript. نتجنب تجاوزه أو إرسال Cookies/رموز تحقق خاصة.

## التشغيل على iSH

```sh
apk add curl ca-certificates
# احفظ السكربت المرفق uboor_audit_mobile.sh داخل مساحة iSH
sh uboor_audit_mobile.sh
# أو الفحص الموسع:
sh uboor_audit_mobile.sh --all
```

النتائج داخل `$HOME/UBOOR-audit`، ومنها `summary.csv` و`api_paths.txt` و`status.txt`. لتبادل الملفات مع iOS، يمكن الاستفادة من تطبيق Files أو تركيب مجلد يختاره المستخدم بأمر `mount -t ios` في iSH (حسب إصدار التطبيق وإعداداته).

## التشغيل على a-Shell

```sh
# افتح مكان الملف عبر تطبيق Files أو pickFolder
sh uboor_audit_mobile.sh
# أو:
sh uboor_audit_mobile.sh --all
```

a-Shell يوفر curl وsh وPython ووصولًا إلى المجلدات المحددة عبر `pickFolder`. إن لم يكن مجلد الملف هو الحالي، انتقل إليه قبل تشغيل السكربت.

## الربط مع ChatGPT

1. إن كان المقصود **وصولًا مباشرًا لجهاز Windows / Kali**، يجب تشغيل وكيل Remote Desktop Commander في الجهاز وإبقاء الاتصال Online. نقطة الربط الرسمية: https://mcp.desktopcommander.app/
2. إن كان المقصود **التحليل من داخل iSH أو a-Shell**، فالخطوة المدعومة فورًا هي تشغيل السكربت محليًا وإرسال ملف `summary.csv` و`api_paths.txt` أو أرشيف المجلد إلى المحادثة. لا يوجد اتصال مباشر مثبت إلى iOS terminal حاليًا.
3. لا تحفظ أو تشارك Cookies الخاصة بالمصادقة، أو bearer tokens، أو بيانات وثائق شخصية دون تنقيح.