# Qafila Architectural Metadata

## المصدر المعياري

ملف [`architectural-identity.v1.json`](architectural-identity.v1.json) هو المصدر المعياري لهوية الإسناد المعماري في هذا المستودع. لا يغير provenance لأي `qafila-event.v1`، ولا يضيف حقاً تشغيلياً إلى Agent أو Workflow.

## قاعدة الحزم المستقبلية

لا يحتوي هذا المستودع المعماري حالياً على `package.json` أو حزمة تنفيذية Node.js، ولذلك لا ينشئ هذا المسار ملفاً شكلياً لا تستخدمه أدوات البناء. عند إنشاء حزمة تنفيذية فعلية، تنقل القيم التالية من سجل الهوية إلى metadata الحزمة مع الحفاظ على الترخيص الفعلي للمكوّن:

| حقل الحزمة | المصدر |
|---|---|
| `author` | `person.canonical_name` |
| `contributors` أو `maintainers` | الأدوار الموثقة لكل مساهم فعلي |
| `copyrightHolder` أو مكافئه في manifest | `attribution.copyrightHolder` |
| `repository` | `project.repository` |
| `keywords` | `citation.keywords` |
| `license` | سياسة الترخيص المعتمدة للمكوّن؛ لا تستنتج من سجل الهوية وحده. |

## مبدأ الإسناد

يجب ألا تستخدم metadata الحزمة لتحويل مساهمة طرف ثالث إلى ملكية للمعمار الرئيسي، أو لإخفاء notices أو تراخيص مستقلة. تحفظ الحزمة المصدر والتراخيص وحقوق المساهمين لكل dependency أو component بحسب سجلاته الأصلية.
