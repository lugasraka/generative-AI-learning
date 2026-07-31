# SoleMates AI Support — Evaluation Runbook v1

> **Date:** [today]
> **Owner:** [Your name], PM
> **Status:** v1 — first end-to-end run. v2 will follow next quarter after the calibration round + v4 prompt fix.
> **Scope:** This runbook is the single artifact a stakeholder reads to understand how we evaluate the SoleMates AI support agent. Engineering details live in the code; stakeholder-level findings live here.

---

## Executive summary

SoleMates' AI support agent is production-ready on policy compliance (100% pass rate) and on escalation discipline (100% acceptable on the top 20 highest-risk interactions). Tone is at 50% — half our responses are passing the LLM judge's quality bar, the other half have calibration issues we'll address in v2 of the prompt. The work happened in three prompt iterations (v2 → v3 → v3.1) over one focused week, and each iteration was driven by findings from the previous one. That's the discovery loop working as designed. Next quarter: tighten the v4 prompt to fix the non-escalation tone issues, run a human calibration round on the 5 persistent HONEST failures, and scale the pilot from 100 to 1,000 queries to confirm the v3.1 baseline holds.

---

## Step 1 — Evaluation context

We started by writing the AI Charter before writing any code. The charter defines what the bot does (5 in-scope intents: tracking, returns, sizing, product questions, billing), what it must never do (give medical advice, promise refunds it can't issue, confirm account deletion without human verification, etc.), and what "good" looks like per intent. The charter also identifies which stakeholders own each row of expected behavior — legal owns medical and GDPR rows, sizing expert owns the empathy-test sizing row, retention is a consult on out-of-policy returns.

**What we found:** the charter forced us to surface disagreements we hadn't noticed. CS Ops wanted the bot to hold the 30-day return window hard; retention wanted softer "is there anything we can do" language. We picked the policy-strict version unless retention had explicit override authority. These decisions show up in the v3.1 prompt.

**What we changed:** nothing — the charter is the source of truth, and every later artifact (metrics, prompts, refset) references it.

---

## Step 2 — Reference dataset

We hand-crafted **12 rows** that cover the 5 in-scope intents plus 3 out-of-scope cases (medical, GDPR, competitor). The mix is weighted toward tracking (40%) and in-policy returns (20%) because that's where production volume is highest, but we kept 5 high-risk rows (out-of-policy return, sizing with medical edge, billing dispute, medical, GDPR) to make sure the most dangerous cases are tested. Risk levels: 4 low, 3 medium, 5 high.

**What we found:** the 12 rows are not a comprehensive sample of production traffic. They are the rows we *absolutely cannot get wrong*. That's the right scope for a reference dataset. The pilot (Ch 6) gave us the production-distribution view; the refset gave us the must-pass view.

**What we changed:** the refset grew from 8 to 12 rows after Ch 3 to cover 4 cases we missed initially (exchanges, pet damage goodwill, off-script review asks, PO box shipping). Each row has a stakeholder assignment and an "unacceptable failure" column that our code metric uses for tripwires.

---

## Step 3 — Evaluation metrics

We built **4 metrics** in a deliberate 2+2 mix:

| Metric | Type | What it catches | Cost |
|---|---|---|---|
| `policy_accuracy` | code (regex) | Hard "NEVER" violations: medical advice, refund-before-verify, hallucinated specs, wrong return window | Free, instant |
| `information_gathering` | code (per-intent) | Whether the bot asked the right clarifying questions | Free, instant |
| `escalation` | LLM judge | Whether escalation is right AND whether context is attached on handoff | ~5s/call |
| `tone` | LLM judge | Warm + brief + honest + calm + non-judgmental (5 sub-dimensions) | ~5s/call |

**What we found:** the two code metrics caught catastrophic failures. The two LLM judges caught soft judgment errors. Neither was sufficient on its own — together they cover the failure modes we care about.

**What we changed:** we iterated the `policy_accuracy` metric twice (Ch 6 tightened the `medical_advice` regex to require co-occurrence of a shoe term AND a medical term, cutting 4 false positives on legitimate sizing advice) and iterated the `escalation` rubric once (Ch 5 added the "context attached" check after we saw the bot escalating without the customer's order context). The `information_gathering` code metric remains too strict and is a known limitation — we'd migrate it to an LLM judge in v2.

---

## Step 4 — Log filtering

We can't review every production interaction, so we built a 7-signal log filter that scores each conversation by "interestingness." The 7 signals are: competitor mention, legal keywords (lawyer/sue/chargeback/fraud), medical keywords, refund amount over $100, sentiment (frustrated/angry words), message length, retry count. Plus an intent-based priority baseline (billing +30, return-out-of-policy +20, etc.). The function returns 0-100; ≥60 is must-review, 30-59 should-review, <30 low-priority.

**What we found on the 100-row pilot:**

| Tier | Rows | % |
|---|---|---|
| Must-review | 1 | 1% |
| Should-review | 19 | 19% |
| Low-priority | 80 | 80% |

**The 1 must-review row** was the "duplicate charge + this is fraud + $250 refund" case. The bot did the right thing (escalated, didn't refund) but we want a human to verify the response and follow up with the customer. **The log filter caught a case the policy code metric would have skipped.**

**What we changed:** the filter is now wired to a 2-tier human review queue. Must-review rows go to the top of the queue; should-review rows are batched into a daily review; low-priority rows are spot-checked at 5%. We save ~80% of the human review time compared to reviewing every interaction.

---

## Step 5 — Production metrics deployment

We split the 4 metrics into online (guardrails, run on every production interaction) and offline (improvement, run on a sampled subset):

| Metric | Online? | Why |
|---|---|---|
| `policy_accuracy` (code) | **Yes** | Catches catastrophic failures, free to run, fast enough for real-time |
| `information_gathering` (code) | **Yes** | Same |
| `escalation` (LLM judge) | No | Too slow (~5s), too expensive; sample 5% weekly |
| `tone` (LLM judge) | No | Same; runs on the top-20 most-interesting rows from log filter |

**What we found:** the online metrics are fast and cheap. The offline metrics are slow and expensive but catch issues the online ones miss. The two-tier split is exactly what the source chapter recommends.

**What we changed:** we wired the log filter as the trigger for the LLM judges. Every must-review and should-review row gets the LLM judges applied automatically. Low-priority rows get the LLM judges on a 5% random sample. This is the discovery loop in production: a customer interaction comes in, the log filter scores it, the LLM judges evaluate it (if it scores high), and the findings feed back into the next prompt iteration.

---

## Step 6 — Guardrails + improvement loops

The v3.1 prompt is the **guardrail**: it's the version of the system prompt that's in production, vetted across 100 pilot rows + 20 LLM-judge-evaluated rows, and known to hold the policy line + escalate billing correctly. New prompt versions don't go to production until they've been re-evaluated on the same pilot + judge suite.

The **improvement loop** is the 3 prompt iterations we did in this chapter:

| Version | What we changed | Result |
|---|---|---|
| v2 | Added: 1-sentence context on escalation, no over-escalation, max 2 sentences + 1 follow-up | Escalation 33% → 83% on the 12-row refset |
| v3 | Added: no competitor products, no sizing equivalences, always-escalate billing, no pricing claims | Escalation 100% on top 20; revealed 3 WARM-on-escalation failures |
| v3.1 | Added: structured 3-step warm-escalation (acknowledge → summarize → handoff) | Latency back to 4.7s; WARM-on-escalation fixed; revealed 3 WARM-on-non-escalation failures |

**What we found:** each iteration peels off one layer of issues and reveals a new one. The v3.1 prompt is the right *production baseline*; the v4 prompt fix is queued for next quarter.

**What we changed:** we now require every prompt change to be re-evaluated on the 100-row pilot + the top-20 LLM judge run before it ships. That keeps the guardrail trustworthy.

---

## Step 7 — Emerging issue discovery

The most important finding from this chapter: **the discovery loop surfaced 3 issues we didn't anticipate when we wrote the charter.** None of these were in the original 12-row refset, the 8-row eval table, or the original v1 prompt.

| Issue | Discovered via | What we did |
|---|---|---|
| Bot recommends competitor products (Brooks Ghost, ASICS Gel-Nimbus) | LLM judge on top 20 | Added "do not name specific competitor products" to v3 prompt |
| Bot invents sizing equivalences ("true to Nike sizing") | LLM judge on top 20 | Added "no sizing equivalences, link to size guide instead" to v3 prompt |
| Bot doesn't escalate billing disputes (refund-for-wrong-amount, duplicate charge) | LLM judge on top 20 | Added "for billing disputes, ALWAYS escalate" to v3 prompt |
| Bot's escalations feel cold / IVR-like | LLM judge on v3 top 20 | Added structured 3-step warm-escalation in v3.1 |
| Bot uses generic warm openers ("I'd love to help") on non-escalation rows | LLM judge on v3.1 top 20 | Queued for v4 prompt (next quarter) |

**What we found:** the 3 prompt iterations produced 5 discovered issues. The 4 of those got fixed; 1 (the IVR-opener pattern) is in the v4 backlog. That's the right pace — we're not shipping 10 fixes a week (chaotic), we're shipping 2-3 substantial fixes per chapter (sustainable).

**What we changed:** we now treat the LLM judge's NOT_ACCEPTABLE / FAIL outputs as the *primary signal* for prompt iteration, ahead of code metric findings. The code metric is the safety floor; the LLM judge is the quality bar.

---

## What we'd do differently next quarter

Three concrete improvements with expected metric movement:

| # | Improvement | Expected impact | Status |
|---|---|---|---|
| 1 | **Apply the v4 prompt fix for the IVR-opener pattern.** Add: "When answering directly (not escalating), open by acknowledging the *specific* question, not a generic 'I'd love to help'. Lead with the answer in sentence 1." | Tone WARM FAILs: 3 → 0 on non-escalation rows. Overall tone pass rate: 50% → 65%. | Queued, v4 prompt draft ready. |
| 2 | **Run the Ch 9 calibration round on the 5 persistent HONEST failures.** Have 2 humans label the rows independently. If the LLM judge agrees with humans > 80%, the judge is calibrated; if not, refine the rubric. | Remove false-positive HONEST failures (estimated 2-3 of 5). Overall tone pass rate: 50% → 60% (or more, depending on #1). | Queued, calibration set ready (5 rows + 10 adversarial cases from Ch 5). |
| 3 | **Scale the pilot from 100 to 1,000 queries with the v3.1 prompt.** Run the full metric suite (2 code + 2 LLM judge) on all 1,000. Expected wall time: ~2.5 hours. | Confirms the v3.1 baseline holds at scale. May surface 1-2 new failure modes (the 10× sample size usually does). | Queued, generator + simulator already exist (Ch 6). |

**Success criteria for v2 of this runbook (next quarter):**
- Tone pass rate: 65-70% (up from 50%)
- All 5 HONEST failures either fixed or confirmed as judge misreads
- 1,000-row pilot run with full metric suite, results consistent with the 100-row pilot
- v4 prompt shipped as the new guardrail
