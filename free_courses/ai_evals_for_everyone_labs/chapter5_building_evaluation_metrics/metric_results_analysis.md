# SoleMates — Chapter 5 Metric Results

> **Date:** [today]
> **Model under test:** `opencode-go/minimax-m3`
> **Dataset:** 12 rows from `chapter4_building_reference_datasets/refset_with_outputs_llm.csv`
> **Raw output:** `metric_results.csv` (per-row) and `metric_agreement.csv` (cross-metric)

---

## Headline numbers

| Metric | Type | Pass rate | What it catches |
|---|---|---|---|
| **policy_accuracy** | code (regex) | 12/12 = **100%** | Tripwires: medical advice, refund-before-verify, hallucinated specs, wrong return window, etc. |
| **information_gathering** | code (pattern) | 4/12 = **33%** | Whether the bot asked the right clarifying questions |
| **escalation** | LLM judge | 4/12 = **33%** ACCEPTABLE | Whether escalation is right AND whether context is attached on handoff |
| **tone** | LLM judge | 7/12 = **58%** PASS | Warm + brief + honest + calm + non-judgmental |

**Big finding:** the **code metric says "everything is fine" (100% policy)** while the **LLM judges say "things are subtly broken in different ways" (33-58%)**. Both are right. The code metric catches the catastrophic failures; the judges catch the soft ones.

---

## What each metric actually found

### policy_accuracy (code) — 12/12

**No tripwires fired on any row.** That includes:
- Row 7 (medical) — bot refused to advise, offered specs only ✅
- Row 3 (out-of-policy return) — bot held the line, escalated ✅
- Row 8 (GDPR) — bot refused, escalated for verification ✅

The code metric is doing its job as a **tripwire**: catching the catastrophic failure modes that would be P0s. It passed everything because the model genuinely didn't violate any of the patterns. But it also can't see the *soft* failures below.

### information_gathering (code) — 4/12

**The metric is too strict, not the LLM is too lax.** The 8 "failures" include cases like:
- Row 1: bot asked for email (a totally reasonable ask) — metric wanted "return_reason" instead (wrong intent mapping)
- Row 2: bot asked for email + whether shoes are unworn — metric wanted "return_reason"
- Row 6: bot offered to escalate before asking for card details — metric wanted card details first

**Fix for the metric:** the `DIMENSION_TO_INTENT` map in `metric_information_gathering.py` is too coarse. A multi-dimension row like `policy_accuracy + information_gathering` shouldn't map to one intent.

### escalation (LLM judge) — 4/12 ACCEPTABLE

The judge found a **systematic issue: the bot escalates without attaching context.** The 8 NOT_ACCEPTABLE verdicts split into two failure modes:

| Pattern | Rows | Frequency |
|---|---|---|
| **Escalates correctly but no context attached** | 3, 6, 8 | 3 rows |
| **Over-escalates routine questions** | 4, 5, 7, 9, 10, 11, 12 | 7 rows (one is both) |

**Insight #1: Context attachment is a real product issue.** When the bot says "let me connect you with a teammate," it should *also* include the customer's question, order #, and any context the human will need. Right now the human has to ask the customer to re-explain. This is fixable with a prompt change: "When you escalate, summarize the customer's question in one sentence for the human."

**Insight #2: The bot is too escalation-happy.** It offered to escalate on routine questions like "do you ship to PO boxes?" and "are these waterproof?" — cases where a direct answer would be better. The model B persona's "when in doubt, escalate" instinct is over-firing. This needs prompt tuning or a re-read of the rubric.

### tone (LLM judge) — 7/12 PASS

The 5 FAILs all failed on **BRIEF** (5/5), with one additional **HONEST** failure. The pattern:

- The bot is warm, honest, calm, and respectful — but **too long**.
- Row 4 (sizing): "warm, honest, calm, and respectful, but it is too long with redundant options, slight repetition of the bunion point, and a soft upsell via the two follow-up offers."
- Row 5 (product Q): "longer than necessary and includes an unsolicited upsell to a road-friendly option."

**Insight #3: The brief-rubric is the most actionable finding.** Cutting response length is a prompt-level fix. Could be solved by adding a "max 2 sentences + 1 follow-up question" constraint to the system prompt.

The one HONEST failure (row 9) is interesting: the bot said "you can exchange within 30 days as long as unworn" — the judge read this as inventing a policy. But the Ch 1 charter says the window is 30 days. So the judge was wrong here, or our rubric needs to allow the bot to cite the canonical policy. **This is a calibration example.**

---

## Code-vs-judge agreement (Bonus #3)

| Comparison | Agreement | Why they disagree |
|---|---|---|
| policy (code) vs tone (judge) | 7/12 (58%) | policy tripwires don't see length/upsell problems |
| info (code) vs tone (judge) | 5/12 (42%) | info-gathering metric is too strict (false fails) |
| escalation vs tone (judge-judge) | 5/12 (42%) | escalation focuses on *action*; tone on *style* |

**Interpretation:** 42-58% agreement is **expected and healthy** when comparing metrics that measure different things. Low agreement here is *not* a sign the metrics are broken — it's a sign they're catching different failure modes. That's exactly why you use a mix of metric types (Ch 5 source-chapter point).

If you compared two metrics measuring the *same* thing and got 42% agreement, that would be a calibration failure. Comparing policy-vs-tone is comparing apples to apples-of-different-varieties.

---

## What the data tells us about the model (not the metrics)

If you trust both metrics (with the info-gathering fix noted), the model has:

- ✅ **Strong** policy adherence (no tripwires fired)
- ✅ **Strong** tone across warm/calm/honest/respectful
- ⚠️ **Weak** response brevity (5/12 too long, often with soft upsells)
- ⚠️ **Weak** escalation discipline (over-escalates routine Qs, under-attaches context)
- ❓ **Unclear** information-gathering quality (need to fix the metric to know)

---

## What to fix next (priority order)

1. **Fix the info-gathering metric.** Map dimensions to intents properly, or use an LLM judge instead of a code metric. Re-run.
2. **Tighten the system prompt** to enforce:
   - "When escalating, include a 1-sentence summary of the customer's question for the human."
   - "Max 2 sentences + 1 follow-up question. No upsells unless asked."
3. **Re-run** and see if escalation goes from 33% to 70%+ and tone from 58% to 80%+.
4. **Then move to Ch 6** and scale this to 1,000 fake queries.

---

## Calibration observations (preview of Ch 9)

- The LLM judge sometimes over-escalates failure (e.g. row 9: judge flagged "invents policy" when the policy was real). Need to add to the rubric: "Citing the canonical policy in the system prompt is NOT an invention."
- The LLM judge sometimes conflates "offers options" with "too long." Need to refine BRIEF to specifically count *options*, not just length.
- The code info-gathering metric is fundamentally limited because per-intent info-needs are too varied. Recommend migrating to an LLM judge for info-gathering too, and dropping the code metric.

These are exactly the calibration issues the Ch 5 source chapter warns about.
