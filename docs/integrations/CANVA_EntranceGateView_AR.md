# Canva ↔ GitHub: مراجعة EntranceGateView

**النطاق:** ربط مرجعي للنسخة التصميمية من تقرير تدقيق الكود داخل Canva بملفات ومستندات مشروع Star-Cyber-Audit-iSH على GitHub.
**تاريخ الربط:** 8 نوفمبر 2026
**الملف محل الفحص:** `EntranceGateView-B9IBJo4k.js`
**SHA-256:** `d48910ae500903a80deaf740cba67485c76e3af789fcff2e1f4d6f86d2419988`

## رابط Canva

- **[تحرير التقرير المستورد في Canva](https://www.canva.com/d/2KT9l32tZst5Yav)**
- **[عرض التقرير في Canva](https://www.canva.com/d/LbSzOHP1oR_s3AP)**
- Canva design ID: `DAHaVDqVSNs`
- النوع: Canva Document قابل للتحرير؛ تم استيراده من تقرير Markdown عام موجود في GitHub.

## ملفات GitHub المرتبطة بالتصميم

| ملف | دوره |
|---|---|
| [EntranceGateView_revalidation_canva_AR.md](../../reviews/2026-11-08/EntranceGateView_revalidation_canva_AR.md) | **مصدر النص للنسخة الحالية في Canva** |
| [EntranceGateView_deep_review_AR.md](../../reviews/2026-11-08/EntranceGateView_deep_review_AR.md) | تدقيق المصدر الكامل الأساسي |
| [ExitGateView_deep_review_AR.md](../../reviews/2026-11-08/ExitGateView_deep_review_AR.md) | مقارنة بوابة الخروج |
| [FILE_BY_FILE_AR.md](../../reviews/2026-11-08/qr-uboor-10-files-batch-2/FILE_BY_FILE_AR.md) | تحليل الدفعة العشرية ملفًا بملف |
| [manifest.json](../../reviews/2026-11-08/qr-uboor-10-files-batch-2/manifest.json) | بصمات الملفات الأصلية |
| [gate_views_review.py](../../tools/ish/gate_views_review.py) | فاحص مصدر محلي دون اتصال خادمي |
| [test_gate_views_review.py](../../tests/test_gate_views_review.py) | اختبارات اصطناعية للفاحص |

## آلية التحديث

1. يُراجع المصدر المحلي أولًا ويُحدث التقرير في GitHub بعد التأكد من خلوه من بيانات حساسة.
2. يتم **إعادة استيراد** الإصدار المنشور من ملف Markdown إلى Canva عند الحاجة، أو تعديل تصميم Canva يدويًا.
3. تُحدَّث هذه الصفحة برابط التصميم الجديد.
4. **لا تتوفر في هذا الربط مزامنة GitHub ↔ Canva لحظية أو مزامنة commits أو تشغيل كود داخل Canva.** هذا مستند مرئي، لا نسخة تشغيلية من مشروع UBOOR.

## حدود الأمان

المستودع عام. لا تُرفع نسخ إضافية من حزم JS الحكومية أو كلمات مرور أو رموز QR فعلية أو سجلات شركات وأشخاص. النص المستورد تدقيق واجهة عام، وليس مستندًا رسميًا أو نتيجة اختبار Backend.

## الدفعة الثالثة — الاعتماديات ومرفقات المحطات (8 نوفمبر 2026)

أُضيفت ثمانية ملفات اعتماديات لم تُدرس بعمق في الدفعات السابقة، مع نسختين مكررتين (QrLocalImporter وCompanyOwnerView). أهم اكتشاف هو أن `EntranceGateView` يمرّر `attachments-register`، بينما `StationsDetailsModal` لا يعرّف `attachmentsRegister` أو يعرض مرفقات التسجيل؛ ويُحمّل المرفقات الأخرى عبر `useAttachments.downloadAttachment` الذي يستدعي `GET carrier_register/download_file`.

**Canva — نسخة قابلة للتحرير من التقرير الجديد:**
- [فتح Canva للتعديل](https://www.canva.com/d/pr1o_Gkq3JRyzY-)
- [عرض Canva](https://www.canva.com/d/V4sZWdbVjXpXZ1T)
- Design ID: `DAHaVQXvXQw`

**مصدر البيانات النصية المراجَع على GitHub:**
- [تقرير الملفات العشرة الجديد](../../reviews/2026-11-08/qr-uboor-dependencies-batch-3/FILE_BY_FILE_AR.md)
- [بصمات الملفات](../../reviews/2026-11-08/qr-uboor-dependencies-batch-3/manifest.json)
- [فاحص الاعتماديات دون شبكة](../../tools/ish/qr_dependencies_batch3_review.py)
- [اختبارات الفاحص](../../tests/test_qr_dependencies_batch3_review.py)
- [تقرير EntranceGateView الأساسي](../../reviews/2026-11-08/EntranceGateView_deep_review_AR.md)

النسخة في Canva مستند بصري مأخوذ من Markdown عام؛ لا تحوي JS حكوميًا أصليًا أو QR فعليًا ولا تتم مزامنتها تلقائيًا عند أي commit.
