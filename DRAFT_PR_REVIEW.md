# Draft PR Review — Qafila Deterministic Gate

**الفرع المحلي:** `chore/qafila-governance-draft`
**المستودع المستهدف لاحقاً:** `wissamblue69-dotcom/qafila-systems-architecture` على `main`
**الحالة:** محلي فقط؛ لا push، لا Pull Request، لا تعديل إعدادات GitHub، ولا branch protection.

## الهدف

إضافة بوابة GitHub Actions تجريبية غير إلزامية باسم check ثابت:

```text
Qafila Governance / deterministic-gate
```

تشغّل GH-01 وGH-02 عند Pull Request يستهدف `main` أو عبر تشغيل يدوي. تمنح workflow أقل الصلاحيات اللازمة (`contents: read`, `pull-requests: read`)، ولا تملك صلاحية إنشاء commit أو تعليق أو issue أو Pull Request أو release.

## المحتوى المقترح

| المسار | الدور |
|---|---|
| `.github/workflows/deterministic-gate.yml` | Workflow غير إلزامية؛ تشغّل الفاحص وتُرفق أدلة كـartifact. |
| `qafila/schemas/qafila-event.v1.schema.json` | عقد الحدث. |
| `qafila/policy/governance-policy.v1.json` | سياسة `experimental_dry_run` مع `network_egress: deny`. |
| `qafila/qafila_gate/` | الفاحص الحتمي وواجهة التشغيل. |
| `qafila/scripts/` | مولد fixtures ومقارن تشغيلين. |
| `qafila/fixtures/` | fixture صالحة وعشر fixtures سلبية. |
| `qafila/docs/gh01-gh02-local-results.md` | نتائج التشغيل المحلي. |

## ما سيفعله الـworkflow

1. يتحقق أن fixtures المتتبعة قابلة لإعادة التوليد بلا اختلاف.
2. يشغّل fixture صالحة مرتين ويقارن الحقول الحتمية في `benchmark.csv`.
3. يشغّل عشر حالات سلبية ويتحقق أن `hold_register.jsonl` يحوي عشر حالات حجب.
4. ينشر ملفات القياس وسجل الحجب كتجميعة artifact مؤقتة وcheck summary.

## ما لن يفعله

لا توجد اتصالات MCP، ولا وصول API خارج GitHub Actions، ولا استخدام لـsecrets، ولا كتابة إلى المستودع، ولا تحديث تلقائي لـ`evidence_coverage.md`، ولا تشغيل branch protection، ولا فتح أو دمج Pull Request، ولا إنشاء release.

## التحقق المحلي المنجز

```text
GH-01 / run A: allow=1, hold=0
GH-01 / run B: allow=1, hold=0
GH-01 / comparison: matches=true
GH-02 / negative suite: allow=0, hold=10
Draft workflow local validation: ok
```

## نقاط يجب حسمها قبل الرفع

1. تثبيت SHA المراجعة لكل GitHub Action بدلاً من tags `@v4` قبل جعل أي check إلزامياً.
2. اعتماد سياسة التراخيص وملفات CODEOWNERS قبل إضافة License Boundary.
3. تحديد طريقة توقيع إيصال الإصدار قبل إضافة Release Receipt workflow.
4. مراجعة ما إذا كان `main` هو الفرع الصحيح والوحيد المستهدف لجميع فحوص المرحلة الأولى.

## الإجراء التالي

بعد مراجعة هذه المسودة، يكون الإجراء الخارجي المقترح هو **دفع الفرع وفتح Draft PR فقط**. لن تُفعل قواعد الحماية أو required checks أو release receipts في تلك الخطوة.
