# SoleMates — AI Evaluation Misconception Audit v0.1

> **Date:** [today]
> **Scope:** All 12 misconceptions from the source chapter, each with one row grounded in either (a) work we did for SoleMates or (b) a realistic public artifact in the AI evaluation industry.
> **Purpose:** Internalize the misconceptions by seeing them next to corrections. This is not a literature review — it's a defense of what we actually did and a calibration of what we'd push back on in vendor pitches / blog posts.
> **Tone:** Direct. "This is wrong" not "one could argue."

---

## How the 12 are split

- **6 rows grounded in our work** (Ch 1-8 artifacts) — corrections we lived
- **6 rows grounded in hypothetical public artifacts** — corrections to vendor pitches, blog posts, and tweets that promote the misconceptions

**The split matters.** The "our work" rows are receipts. The "public artifact" rows are what we'd say in a vendor meeting when someone tries to sell us a 47-metric dashboard.

---

## The 12 rows

### 1. "Engineers can design metrics alone"

**Source (hypothetical):** Medium article — *"You don't need a PM to design your evals. We did it in one sprint and shipped 12 metrics that catch every failure mode. PMs slow you down."*

**What's missing:** Engineers can build the metric mechanism (the regex, the LLM judge prompt), but the *rubric* — what counts as good behavior — is a product decision. Engineers alone will optimize for things they can measure (latency, structure) and miss things only domain experts care about (empathy, escalation judgment, policy nuance).

**SoleMates correction:** We hit this in Ch 3. The eval table row for the 60-day out-of-policy return had a stakeholder disagreement: CS Ops wanted the bot to hold the policy hard; Retention wanted softer "is there anything we can do" language; Legal wanted a specific disclaimer. An engineer-only design session would have picked one side and shipped. The PM-facilitated session picked "policy-strict unless explicit retention override authority" — the right call for a real product. **Engineers build the mechanism; PMs + domain experts define the rubric.**

### 2. "Detailed criteria alone make LLM judges work"

**Source (hypothetical):** Vendor pitch — *"Our LLM judge is calibrated out of the box. We trained it on 50,000 examples with detailed rubrics covering 12 sub-dimensions. Just plug it in."*

**What's missing:** A detailed rubric is *necessary but not sufficient* for a calibrated judge. The judge still has to be tested against *your* product's responses, *your* domain's edge cases. A judge calibrated on 50,000 generic examples will still misread your product's specific behaviors — and you'll find out by running it on real data, not by reading the rubric.

**SoleMates correction:** We caught this in Ch 5 v2. Our escalation judge was detailed (5 rules, 4 categories) but still gave a NOT_ACCEPTABLE verdict on row 3 because it read the bot's "I can't process this directly" as a flat refusal, missing that escalation followed. The judge was detailed; it was *not* calibrated to our product. The Ch 7 calibration observations flagged this as a problem to address in v2 of the runbook.

### 3. "Code metrics are too simple"

**Source (hypothetical):** Twitter thread — *"Code-based metrics miss all the nuance. Real AI evaluation requires LLM judges. Anything else is kid stuff."*

**What's missing:** Code metrics are the safety floor. They catch catastrophic failures (medical advice, refund-before-verify, hallucinated specs) at zero cost and sub-millisecond latency. LLM judges are slow, expensive, and add non-determinism. You don't pick one *or* the other — you use code metrics for the objective tripwires, LLM judges for the subjective stuff.

**SoleMates correction:** We lived this in Ch 6. Our `medical_advice` regex was *too* strict in v1 (4 false positives on legitimate sizing advice). After tightening to require co-occurrence of a shoe term AND a medical term, the metric went from 96% to 100% pass rate and correctly flagged 16 of 17 adversarial test cases. The metric isn't "too simple" — it's *exactly the right tool* for catching a class of failures the LLM judge would have caught inconsistently. **The 50ms code metric is doing the work; the 5,000ms LLM judge is the polish.**

### 4. "LLM judges are automatically best"

**Source (hypothetical):** Vendor pitch — *"Our LLM judge replaces all your human review. 99% accurate out of the box. No calibration needed."*

**What's missing:** An uncalibrated LLM judge is *worse* than no judge. It adds another layer of non-determinism that looks like quality control but isn't. You need to test the judge against human labels on at least 50 examples from your product before you can trust its verdicts.

**SoleMates correction:** We hit this in Ch 5 v2. The tone judge gave a FAIL on row 9 because the bot said "you can exchange within 30 days" — the judge read this as inventing a policy, but the 30-day window is the canonical policy from the Ch 1 charter. The judge wasn't calibrated to *our* policies. We documented this as a calibration case for v2 of the runbook.

### 5. "Don't eval every interaction"

**Source (our work):** Ch 7 — `score_log.py` + the 100-row pilot.

**What's missing:** The misconception here is the *opposite* of what the source chapter warns about: "you should eval every interaction." The chapter's actual position is: *sample based on signal*. Eval every "must-review" interaction, sample should-reviews, spot-check low-priority.

**SoleMates correction:** We built a 7-signal log filter that scored 100 pilot rows: 1 must-review, 19 should-review, 80 low-priority. The filter is the gating mechanism: LLM judges run on the top 20, not on all 100. **Without the filter, we'd spend ~5 hours/100 conversations reviewing everything. With it, we spend ~40 min on the highest-priority 20%.** That's the discovery loop in production.

### 6. "Online is always better than offline"

**Source (our work):** Ch 5/7 — the online/offline split.

**What's missing:** Online metrics run on every production interaction. They're fast and catch issues in real-time, but they're expensive. The right question isn't "online or offline" — it's "which behaviors need real-time intervention and which can be batch-analyzed weekly?" Catastrophic failures (medical advice, refund fraud) need online guardrails. Subtle quality issues (tone, empathy) can wait for offline batch analysis.

**SoleMates correction:** We split our 4 metrics deliberately. `policy_accuracy` and `information_gathering` (code, sub-millisecond) are online guardrails — they fire on the catastrophic failures that need immediate action. `escalation` and `tone` (LLM judge, ~5s each) are offline — they run on the log-filter-selected 20% of traffic and feed the next prompt iteration. Putting all 4 online would be 5× the cost for marginal benefit; putting all 4 offline would miss the catastrophic failures. **The split is the design.**

### 7. "Eval is one-time setup"

**Source (our work):** 3 prompt iterations in 1 week (Ch 5/7: v2 → v3 → v3.1).

**What's missing:** Evaluation is a continuous practice, not a launch deliverable. The metrics, the reference dataset, and the prompt are all in motion as production teaches you things you didn't know at launch. A team that thinks they're "done" with evals after the first 2 weeks is a team that's about to ship a regression.

**SoleMates correction:** We did 3 prompt versions and 2 metric versions in 8 chapters. Each iteration peeled off one layer of issues and revealed a new one. The v3.1 prompt is "done" only in the sense that it's the right *baseline for production launch* — not in the sense that we stop iterating. The v4 prompt is queued for next quarter (the IVR-opener pattern). **"Done" means "good enough to launch today." Not "good enough forever."**

### 8. "Metrics are fixed once shipped"

**Source (our work):** 2 metric versions + 3 prompt versions in 8 chapters.

**What's missing:** Metrics are software. They have bugs. They have edge cases. They have calibration drift as the model changes. A "shipped" metric isn't a finished metric — it's a metric you've started watching.

**SoleMates correction:** The `policy_accuracy` metric had a bug (the `medical_advice` regex was too strict), caught in Ch 6 with 4 false positives on legitimate sizing advice. The `wrong_policy_window` regex was over-firing in Ch 7, also fixed. The `information_gathering` code metric is *still* too strict and is queued for replacement with an LLM judge in v2. **Three metric fixes in 4 chapters. None of them would have happened if we'd treated the metric as "shipped."**

### 9. "Build a 50-metric dashboard"

**Source (hypothetical):** Vendor blog post — *"Our 47-metric dashboard gives you complete visibility into your AI's behavior. Track everything."*

**What's missing:** More metrics ≠ better eval. Each metric costs you to build, run, interpret, and maintain. The 80/20 rule applies: 4 well-chosen metrics catch 80% of the issues; the other 43 catch diminishing returns. A 47-metric dashboard is a maintenance burden that hides signal in noise.

**SoleMates correction:** We have 4 metrics total. The other 8 dimensions we care about (empathy, reasoning quality, retrieval accuracy, etc.) are covered by *the rubric*, not separate metrics. When the LLM judge says "this tone fails," we get 5 sub-dimensions of failure in one verdict. **A dashboard that shows 47 numbers is a dashboard no one reads. A dashboard that shows 4 numbers with 5 sub-dims each is a dashboard a PM can act on weekly.**

### 10. "Eval ≠ A/B testing"

**Source (our work):** Implicit — we never ran an A/B test on v2 vs v3 vs v3.1.

**What's missing:** A/B testing measures user behavior under two conditions (e.g. conversion rate, retention). Eval measures *system behavior* against a rubric. They answer different questions: A/B says "which version makes users do X more often?" Eval says "which version is more correct / safer / more on-policy?" You need both. Confusing them leads to shipping the version that *converts better* even if it's *less correct*.

**SoleMates correction:** We compared v2/v3/v3.1 on the same 100-row pilot + the same 20-row LLM judge run. The judges told us "v3.1 escalates better and is warmer on escalations" — but they didn't tell us "users prefer v3.1" because that's not what they measure. In production, we'd add a thin A/B layer (1% of traffic on v3.0 vs v3.1) to measure user preference — but we'd *never* ship a version that fails the LLM judge just because users prefer it. **Eval is the safety floor; A/B is the user-preference signal above it.**

### 11. "Benchmarks = product success"

**Source (our work):** Ch 2 — the model choice decision.

**What's missing:** Benchmarks (MMLU, HumanEval, GSM8K) measure *general capability* on standardized tasks. They help labs and infra teams pick base models. They say nothing about whether the model works for *your* product, *your* users, *your* domain. A model that scores 92% on MMLU can still fail at a customer support agent for shoe retail because it hasn't seen enough retail-CS data.

**SoleMates correction:** In Ch 2, we chose Model B (80% MMLU, 3× cheaper, retail-fine-tuned) over Model A (88% MMLU, expensive, general). The 8-point MMLU gap was the *filter*, not the verdict. The verdict came from the 5 product-specific scenarios we built (angry 60-day return, sizing with medical edge, billing dispute with fraud claim, out-of-scope medical, out-of-scope GDPR). Model B was the right call because the bottleneck for a CS agent isn't MMLU — it's tone, policy discipline, and escalation judgment. **Benchmarks eliminate obviously-bad candidates. They don't pick your winner.**

### 12. "You need comprehensive coverage"

**Source (our work):** Ch 4 — 12 hand-picked rows in the refset.

**What's missing:** Comprehensive coverage is a mirage. The input space is unbounded; the output is non-deterministic; you can never eval "all" the cases. The right goal isn't comprehensive coverage — it's *scenarios you absolutely cannot get wrong* plus a *sample of realistic production distribution*. The must-pass set is small (12-30 rows); the production-distribution set is a sample (100-1,000 rows); the long tail gets discovered via log filtering.

**SoleMates correction:** Our refset is 12 rows — *not* 200. The 12 cover the 5 in-scope intents, 3 out-of-scope cases, 5 high-risk rows, 4 medium-risk rows. We did *not* try to enumerate all the ways a customer might phrase a return request. We picked the 12 we cannot get wrong, then built the pilot (100 rows, realistic mix) to test against production distribution, then built the log filter to catch the long tail. **12 + 100 + the log filter = comprehensive in practice, not in theory.**

---

## The 12 ranked by how badly they'd hurt SoleMates

If we believed the wrong side of each of these, what would break first?

| Rank | Misconception | Failure mode | Cost to fix |
|---|---|---|---|
| 1 | **#11 — Benchmarks = product success** | Ship the wrong model, see it fail on real retail customers | High — re-pilot, re-launch |
| 2 | **#1 — Engineers can do it alone** | Build a metric that optimizes for the wrong thing; ship a tone-deaf bot | High — re-define rubric, re-build metric |
| 3 | **#5 — Eval every interaction** | Bankrupt the team on LLM judge costs; can't afford to ship | Medium — cut scope, re-prioritize |
| 4 | **#7 — Eval is one-time setup** | Miss regressions as the model and traffic evolve | Medium — re-launch eval work |
| 5 | **#8 — Metrics are fixed** | Miss metric bugs; ship a metric that lies to you | Medium — re-validate, re-launch |
| 6 | **#6 — Online is always better** | 5× the cost for marginal benefit; or 0× the cost for catastrophic failures | Medium — re-architect metrics |
| 7 | **#4 — LLM judges are automatically best** | Trust an uncalibrated judge; ship a regression because the judge said it was fine | High — lose trust in evals, re-pilot |
| 8 | **#2 — Detailed criteria = calibration** | Same as #4 but worse: spend 3 months writing a rubric and skip the validation step | High — wasted work, re-do |
| 9 | **#9 — 50-metric dashboard** | Maintain 47 metrics, no one reads the dashboard, real failures hide in noise | Medium — re-prioritize, re-build |
| 10 | **#3 — Code metrics are too simple** | Replace cheap, fast code metrics with slow, expensive LLM judges; lose the safety floor | Medium — re-architect |
| 11 | **#12 — Comprehensive coverage** | Spend 6 months building 500-row refset; never finish; never ship | High — wasted time, re-scope |
| 12 | **#10 — Eval ≠ A/B testing** | Use A/B test to ship a version that fails the eval (or vice versa) | Low — caught by the other guardrail |

**The top 3 are the ones that would kill the product. The bottom 3 are the ones that would slow us down.**

---

## Calibration observations from this audit

- **#4 and #2 are linked.** A detailed rubric without calibration is worse than no rubric because you trust it. The fix is the same: run the judge on 50 hand-labeled examples before trusting it.
- **#7 and #8 are linked.** Eval-as-one-time and metrics-as-fixed are the same misconception at different time scales. Both fail because they assume the system is stable; it's not.
- **#3 and #5 are linked.** Code metrics are "too simple" is the *excuse* for not running code metrics. Then "eval every interaction" is what you do instead. Both push you toward the expensive, slow path when the cheap, fast path would catch most of the issues.
- **#11 and #12 are linked.** Benchmarks and comprehensive coverage are both *measurement maximalism* — the belief that more measurement is always better. Sometimes 12 hand-picked rows beat 200 generic ones.

---

## What this audit tells us to do next

1. **Address the calibration gaps** in the LLM judges (rows 2 and 4). Run a Ch 9-style calibration round on 50 hand-labeled examples before shipping the next prompt.
2. **Stop adding metrics.** 4 is the right number for now. Resist any vendor pitch for a "comprehensive dashboard."
3. **Treat metrics as software.** They have bugs. We caught 2 in 4 chapters. We will catch more. Each fix gets documented.
4. **Build the v4 prompt with the IVR-opener fix queued for next quarter**, per the Ch 8 runbook.
