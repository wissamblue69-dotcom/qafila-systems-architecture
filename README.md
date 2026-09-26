# Qafila Systems Architecture

> **Founder and Principal AI & Systems Architect:** **وسام حاج محمد — Wissam Haj Mohammed**

**Qafila Systems Architecture** هو المستودع المرجعي لمعمارية القافلة: منظومة حوكمة متعددة الوكلاء تعتمد الإسناد أولاً، وسياسة الحجب عند الخطأ، وقرارات بشرية موثقة قبل الأفعال الخارجية. يوثق المستودع عقود الأحداث والسياسات الحتمية وإيصالات التشغيل وسجل التنسيق القابل للمراجعة.

## الوضع الحالي المثبت

| المكون | الغرض | الحالة |
|---|---|---|
| `qafila-event.v1` | عقد حدث مقيد بـprovenance وبصمات قابلة لإعادة الحساب. | مثبت في اختبار PoC. |
| Deterministic Governance Gate | فحص schema وsource allowlist وpayload hash وidempotency وقواعد hold. | يعمل في GitHub Actions بوضع غير إلزامي. |
| GH-01 | مقارنة تشغيلين لمدخل ثابت. | تطابق حتمي مثبت في بيئتين: محلية وGitHub Actions. |
| GH-02 | حزمة عشر حالات سلبية. | حجب 10/10 قبل أي Adapter أو خروج شبكي. |
| سجل التنسيق | مراجعات وإيصالات واختبارات تحقق قابلة للربط بالـcommit. | متاح تحت `qafila/coordination/`. |
| G-2 / G-3 | عقد موافقة pending وتغطية أدلة Artifact-only. | قيد المراجعة في Draft PR منفصل. |

## المبادئ الحاكمة

| المبدأ | التطبيق |
|---|---|
| **Provenance-first** | لا يتحول المحتوى إلى claim معتمد بلا `source_ref` و`locator` و`source_hash`. |
| **Fail-closed** | أي schema أو مصدر أو بصمة أو موافقة ناقصة تسجل `hold` ولا توسع الصلاحية. |
| **Least privilege** | بوابات CI وMCP تعمل بالصلاحيات الدنيا اللازمة وبلا أسرار في PoC. |
| **Human approval** | لا تمنح المراجعة أو metadata أو Agent أي صلاحية دمج أو release أو إعدادات مستودع. |
| **Evidence separation** | المصدر والدليل والادعاء وقرار الموافقة وإيصال التشغيل سجلات منفصلة. |

## الإسناد والاستشهاد

* سجل الهوية المعمارية المقروء آلياً: [`qafila/metadata/architectural-identity.v1.json`](qafila/metadata/architectural-identity.v1.json).
* وثيقة الإسناد والنطاق وحدود الإثبات: [`ARCHITECTURAL-AUTHORSHIP.md`](ARCHITECTURAL-AUTHORSHIP.md).
* صيغة الاستشهاد المعيارية: [`CITATION.cff`](CITATION.cff).

الصيغة المفضلة للإحالة:

> Wissam Haj Mohammed. *Qafila Systems Architecture: Provenance-First Fail-Closed Multi-Agent Governance*. 2026.

## حدود النطاق

هذا المستودع مرجع معماري وحوكمي. ولا يمثل وحده حكماً قانونياً في الملكية الفكرية أو تفويضاً للوصول إلى خدمة أو secret أو صلاحية دمج أو نشر إصدار. تعالج التراخيص والحقوق الخاصة بكل مكوّن أو تبعية في إشعاراتها وسجلاتها المستقلة.

## المساهمة والمراجعة

تتم أي مساهمة عبر Pull Request قابل للمراجعة. قبل تفعيل حوكمة إلزامية أو تعديل حماية الفروع أو إنشاء إصدار، يلزم سجل موافقة بشري صالح وفق `qafila-approval.v1` وبنطاق يطابق الفعل المقترح.
