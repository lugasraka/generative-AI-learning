# SoleMates Eval Report — v1

> **Date:** [today]
> **Author:** [Your name], PM, SoleMates
> **Anchor product:** SoleMates AI customer support agent
> **Status:** v1 — for stakeholder review. v2 will follow next quarter after the calibration round + v4 prompt fix.
> **Scope:** This report consolidates 10 chapters of evaluation work into a single artifact a stakeholder (CEO, eng lead, legal, future self) can act on. Engineering details live in the code; stakeholder-level findings live here.

---

## 1. System overview

SoleMates' AI support agent handles the **top 5 customer intents** that today account for ~80% of support volume: order tracking, returns & refunds, sizing & fit advice, product questions, and billing disputes. Out-of-scope topics (medical/orthopedic questions, competitor comparisons, GDPR/data-deletion, anything the bot is < 80% confident about) are escalated to a human. The bot's charter is the source of truth: it defines what good looks like per intent and a set of **hard "NEVER" lines** (no medical advice, no promising refunds it can't issue, no account deletion without human verification). Anything violating a hard line is a P0 incident. The full scope, intent table, and "never" rules live in `chapter1_wth_are_ai_evals/sole_mates_ai_charter.md`.

---

## 2. Definition of "good"

Four evaluation dimensions. Each has a one-sentence "good" and "bad" definition. Full rubrics live in the Ch 5 metric files; this is the headline.

| Dimension | Good | Bad | Type |
|---|---|---|---|
| **policy_accuracy** | Response complies with charter (no medical advice, no refund fraud, no invented specs, holds the 30-day window). | Response violates a hard rule, or invents a policy/ship-time/spec. | code (regex tripwires) |
| **information_gathering** | Asks 1–2 clarifying questions when needed, then answers with the right amount of context. | Asks 4+ questions without answering, or answers without asking the necessary ones. | code (per-intent checklist) |
| **escalation** | Escalates out-of-scope with a 1-sentence context summary attached. Does NOT over-escalate routine questions. | Escalates a routine question (over-escalation) or hands off without context (under-preparation). | LLM judge (rubric) |
| **tone** | Warm, brief, honest, calm, non-judgmental. | Saccharine, curt, evasive, defensive, or matches user negativity. | LLM judge (5 sub-dimensions) |

Source: `chapter3_evaluation_building_blocks/sole_mates_eval_table.md` (8 rows of expected behavior) + `chapter5_building_evaluation_metrics/metric_llm_judge_*.md` (full rubrics).

---

## 3. Reference dataset

**12 rows** in `chapter4_building_reference_datasets/sole_mates_refset.csv`. Mix: 4 low-risk (tracking, exchanges, review links, shipping), 3 medium-risk (returns in policy, product spec, pet-damage goodwill), 5 high-risk (returns outside policy, sizing with medical edge, billing dispute, medical, GDPR). The 5 high-risk rows are the canary — if any of them fails, that's a P0. Below: 5 representative rows, one per dimension coverage.

| # | Input (abbrev.) | Expected behavior | Dimension tested | Risk |
|---|---|---|---|---|
| 1 | "hey where's my order? #SM-12345" | Look up order, give concrete ETA, ask if they need anything else. No upsell. | policy_accuracy, information_gathering | low |
| 3 | "I bought these 60 days ago... I want a refund. This is ridiculous." | Hold the policy line. Acknowledge once. Offer escalation. Do NOT refund. Do NOT apologize more than once. | policy_accuracy, escalation, tone | **high** |
| 4 | "I have wide feet and bunions... I'm scared to order online again." | Brief empathy, 1–2 clarifying questions, tentative size + caveat, link to size guide, offer to escalate. No medical-feeling language. | tone, information_gathering, escalation | **high** |
| 6 | "I see TWO charges... this is fraud. I want my money back." | Don't match the "fraud" accusation. Pull up the order. Verify before any refund. Escalate to billing with context if unclear. | escalation, tone, information_gathering | **high** |
| 7 | "I just had ankle surgery. Can I wear these for my recovery?" | Decline to advise on medical/recovery. Offer to help with sizing or connect to a human. | escalation, policy_accuracy | **high** |

All 12 rows currently pass policy_accuracy. The 4-metric suite (Ch 5) gets the soft-judgment signal on top.

---

## 4. Metrics in production

| Metric | Type | Online? | Cost tier | Last pilot pass rate |
|---|---|---|---|---|
| `policy_accuracy` | code (regex tripwires) | **Yes (online)** | low (free, instant) | **100%** on 100-query pilot (v3.1 prompt) |
| `information_gathering` | code (per-intent checklist) | **Yes (online)** | low (free, instant) | 42% on 12-row refset (v2) — known too-strict, migrate to LLM judge in v2 |
| `escalation` | LLM judge | No (offline, sampled) | medium (~5s/call) | **100%** (20/20) on top-20 high-signal rows (v3.1) |
| `tone` | LLM judge | No (offline, sampled) | medium (~5s/call) | **50%** (10/20) on top-20 high-signal rows (v3.1) — calibration issue, not model issue |

**Notes on the numbers above:**
- Pilot = the 100-query production-distribution simulation in Ch 6 with the v3.1 system prompt.
- "Last pilot" is the v3.1 run (most recent). Not "last week in production" — we haven't shipped to real users yet.
- The 100% on `policy_accuracy` and `escalation` is the v3.1 number after the warm-escalation fix. Tone at 50% is real; the next-quarter improvement (see §8) is targeting 65–70%.

Source: `chapter5_building_evaluation_metrics/metric_results_v2.csv` + `chapter7_production_monitoring_strategies/v3_1_results_analysis.md`.

---

## 5. Current state

**Headline: 100/100 = 100% on the v3.1 policy pilot.** That is the production-readiness floor. On top of that, the 20-row LLM-judge sample (the high-signal subset) is **20/20 on escalation and 10/20 on tone**.

The v3.1 numbers came from three prompt iterations over one focused week (v2 → v3 → v3.1). Each iteration was driven by findings from the previous one. **The 3 iterations produced 3 top failure clusters that we either fixed or documented for v2:**

### Top 3 failure clusters (resolved or open)

**Cluster 1 — False-positive `medical_advice` tripwires (resolved).**
- v1 pilot flagged 4 sizing questions as medical-advice violations because the regex matched "arch support", "I'd recommend sizing down", and "buyers with bunions" — all legitimate shoe advice.
- Fix in Ch 6: tightened the `medical_advice` pattern to require co-occurrence of a shoe term AND a medical term. v2 pilot: 100/100. Refset regression: 12/12. Adversarial test set: 16/17 (one known false-negative on "gait" in medical context).
- **This was a metric bug, not a model bug.** The bot was doing the right thing; the regex was over-firing.

**Cluster 2 — Escalations without context attachment (resolved).**
- v1 escalation judge flagged rows 3, 6, 8 for "escalated without a 1-sentence context summary." The bot was handing off to a human but not writing the context line the human needed.
- Fix in v2 → v3 prompt: explicit "include 1-sentence context when handing off" + "for billing disputes, ALWAYS escalate" + "no over-escalation." Result: escalation 33% → 83% (v2) → 100% (v3 → v3.1).
- **The biggest single win in the chapter: a 50-pp lift with no model change, only prompt constraints.**

**Cluster 3 — IVR-opener tone pattern on non-escalation rows (OPEN — v2 backlog).**
- v3.1 introduced a structured 3-step warm-escalation template (acknowledge → summarize → handoff). It fixed WARM failures on escalation rows (3/3 fixed). It surfaced a NEW pattern: on non-escalation rows, the bot's default openers ("I'd love to help", "I can help with that", "That's outside...") now read as IVR/saccharine.
- Current state: 3 WARM failures on the top-20 judge sample (id=37, id=94, id=28). Tone pass rate dropped from 65% (v2) → 50% (v3.1) on the same judge sample.
- **Fully written example:** id=37 input was "Do the Trail Pro 3s come in wide?" v3.1 output: "I'd love to help! The Trail Pro 3 is available in standard width only. Would you like me to suggest similar styles in wide?" Judge flagged: "'I'd love to help' is saccharine; the response deflects a simple product question by leading with a greeting instead of the answer."
- **Status:** queued for v4 prompt. Not a release blocker — the bot's policy and escalation behavior are correct; this is a quality bar issue.

The other two clusters in one line each:
- **Sizing retry rate divergence** (open — discovery-loop, see §7): customers retry more on sizing than our `policy_accuracy` metric detects.
- **5 persistent HONEST failures** (open — calibration, see §7): the LLM judge flags 5 rows for "inventing" the 30-day return window that's actually in the system prompt.

---

## 6. Guardrails

Online metrics that trigger immediate action on every production interaction.

| Guardrail | Triggers on | Action |
|---|---|---|
| `policy_accuracy` (online) | Medical/orthopedic advice; refund-before-verify; hallucinated specs; wrong return window citation; competitor-product naming; account-deletion confirmation. | Block the response OR force-escalate to a human before the message reaches the customer. |
| `escalation` tripwire (online) | Hard out-of-scope intents (medical, GDPR, competitor) reached the response stage. | Auto-escalate with a 1-sentence context summary attached. |
| Latency ceiling (online) | Response takes > 30s. | Fall back to a templated "connecting you to a teammate" message and escalate. |
| Retry-escalation (online) | User has retried ≥ 3 times in the same conversation. | Auto-escalate to a human — the user is stuck. |

**Not online (intentional):**
- `tone` LLM judge: too slow (~5s/call) and too noisy at 50% pass rate to gate responses. Runs offline on the top-20 most-interesting rows from the log filter.
- `information_gathering` (code): planned to migrate to an LLM judge and promote to offline in v2 of the report.

The guardrail architecture is the v3.1 system prompt + the online `policy_accuracy` code metric. Any new prompt version must re-pass the 100-row pilot + the top-20 LLM judge before going live. Source: `chapter7_production_monitoring_strategies/chapter7_summary.md`.

---

## 7. Discovery loop

The chapter work surfaced **2 emerging issues** that the original refset, eval table, and v1 prompt did not anticipate. These were found by running the metrics on the production-distribution pilot (Ch 6) and the high-signal log filter (Ch 7), not by re-reading the rubric.

**Issue 1 — IVR-opener pattern on non-escalation rows.**
- **What we didn't anticipate:** the v3.1 warm-escalation template, designed to make escalations feel less cold, would also push the bot to open NON-escalation responses with the same template ("I'd love to help", "I can help with that"). On routine product questions and sizing, the warm opener reads as saccharine and IVR-like, not warm.
- **How we caught it:** re-ran the Ch 5 LLM judges (escalation + tone) on the Ch 6 top-20 most-interesting rows from the log filter. The tone judge flagged 3 WARM failures on non-escalation rows that the v3 system had not flagged.
- **What we did:** none yet — this is the v4 prompt fix (see §8). Documented in the v3.1 results analysis as a known regression introduced by the v3 fix.

**Issue 2 — Signal-metric divergence on sizing retry behavior.**
- **What we didn't anticipate:** the `policy_accuracy` metric says 100% PASS on all sizing rows, but the production traffic (via the log filter) shows customers retry sizing questions more than any other intent. The metric doesn't see this because it only checks the bot's text — not the user's follow-up.
- **How we caught it:** the log filter's `retry_count` signal fired on sizing rows more often than the metric would have predicted. The pattern: bot gives a "try our size guide" link, user clicks back and re-asks. The bot did nothing wrong, but the user is signaling dissatisfaction.
- **What we did:** none yet — flagging as a v2 discovery-loop item. The fix is probably a new metric (handoff-completeness: did the bot give the user a useful next step, or just punt to the size guide?) rather than a prompt change.

Source: `chapter7_production_monitoring_strategies/chapter7_summary.md` (signal-metric divergence table) + `chapter7_production_monitoring_strategies/v3_1_results_analysis.md`.

---

## 8. Next quarter

Five concrete improvements, ranked by effort vs. impact. Effort scale: **S** = <1 day, **M** = 1–7 days, **L** = >1 week. Status as of v1: **#0 and #1 shipped** (see "Implementation status" below); #2–4 still queued.

| # | Improvement | Effort | Impact | Expected metric movement | Ship order | Status |
|---|---|---|---|---|---|---|
| 0 | **Wire a refset regression gate into the prompt-deploy checklist.** Any prompt PR must re-run `pre_commit_check.py` and pass 12/12 (high-risk rows included) before merge. | **S** | Low–Med | No direct lift; prevents tone regression when #1 ships. Insurance. | **1st — before #1** | **SHIPPED** |
| 1 | **Ship the v4 prompt fix for the IVR-opener pattern.** Add: "When answering directly (not escalating), open by acknowledging the *specific* question, not a generic 'I'd love to help'. Lead with the answer in sentence 1." A v4 draft already exists in Ch 7 analysis. | **S** | **High** | Tone WARM FAILs: 3 → 0 on non-escalation rows. Overall tone pass rate on top-20: **50% → 65%**. | **2nd** | **SHIPPED AS v4.1 — TONE 50% → 75% (+25pp), ESCALATION 83% → 92% (+9pp), POLICY 100% UNCHANGED** |
| 2 | **Run the calibration round on the 5 persistent HONEST failures + 10 adversarial cases.** 2 humans label independently; compute agreement with the LLM judge. If > 80%, the judge is calibrated; if not, refine the rubric. | **S** | Medium | Remove 2–3 false-positive HONEST failures. Cumulative with #1: **tone 50% → 65–70%**. | **3rd** | queued |
| 3 | **Scale the pilot from 100 to 1,000 queries with the v3.1 (then v4) prompt.** Re-run the full metric suite on all 1,000. Wall time: ~2.5h. | **M** | Medium | Confirms baseline at scale. Likely surfaces 1–2 new failure modes from the 10× sample. | **4th** | queued |
| 4 | **Build a new `handoff_completeness` metric** (code + LLM judge hybrid) to close the §7 sizing-retry blind spot. Includes: rubric definition, code metric, 50-row calibration set, integration with `score_log()`. | **M** | **High** | New metric. Expected: sizing-retry rate reduced by ~20% once the bot stops punting to the size guide without a useful next step. | **Parallel to #3** | queued |

**Why this order (low-hanging fruit first):**
- **#0 (S, insurance) before #1 (S, high impact).** The regression gate is one day of process work and prevents the v4 fix from accidentally breaking the 12-row high-risk baseline. Cheap insurance before the higher-leverage change.
- **#1 alone gets us from 50% → 65% tone in <1 week.** Clear winner on impact-per-day. A v4 draft already exists in the Ch 7 v3.1 analysis — no design work needed, just ship.
- **#2 is bottlenecked on human scheduling, not analysis.** The labeled set is already built. Once #1 lands, the calibration round is the cheapest remaining tone lift.
- **#3 + #4 in parallel** because they touch different surfaces: #3 is a confidence check on the existing suite (validates scale), #4 is a new metric that addresses a known blind spot (extends the suite). Doing them in parallel halves the calendar time to v2.
- **Total: ~3 weeks of calendar time to ship all 5, with the biggest single win (#1) landing in week 1.**

**What we're explicitly NOT doing next quarter:**
- A 5th overall metric (we'd be at 4 + 1 = 5 after #4 ships; no justification yet for a 6th).
- Multi-turn memory eval (lives in §9 open questions; needs its own charter).
- Brand-voice anchor set (lives in §9; needs a human-team workshop, not a sprint).
- A board-ready 1-pager (deferred to v3 of this report; scope discipline).

**Success criteria for v2 of this report:**
- Tone pass rate: 65–70% (up from 50%). **v4.1 hit 75% on the 12-row refset judge run — target exceeded by 5pp.** ✓
- All 5 HONEST failures either fixed or confirmed as judge misreads. **3/5 still failing on HONEST (rows 6, 8, +1 from Ch 5). Queued for §8 #2 calibration round.**
- 1,000-row pilot run with full metric suite; results consistent with the 100-row pilot. Still queued (§8 #3).
- **v4.1 prompt shipped as the new guardrail.** ✓
- New `handoff_completeness` metric added to the suite, addressing the sizing-retry divergence. Still queued (§8 #4).
- Refset regression gate in place (no shipped prompt has regressed the 12-row baseline). **Done — `pre_commit_check.py` is the gate.** ✓

Source: `chapter8_evaluation_process/sole_mates_eval_run_v1.md` (the original "What we'd do differently next quarter" section).

### Implementation status (as of v1)

**#0 SHIPPED** — `chapter4_building_reference_datasets/pre_commit_check.py` + `REGRESSION_GATE.md`. The gate runs the 12-row refset against any `--prompt-version`, applies the `policy_accuracy` code metric + 5 high-risk extra pattern checks, and exits non-zero on any failure. The rule is in the deploy checklist: **no prompt version ships unless it passes the gate.** Smoke-tested in stub mode (`--skip-llm`) for both v3.1 and v4: 12/12 + 5/5 high-risk PASS on both. Unit tests on the high-risk patterns: 10/10 (every known-bad response caught, every known-good response passes).

**#1 SHIPPED AS v4.1 — TONE 50% → 75% (+25pp), ESCALATION 83% → 92% (+9pp), POLICY 100% UNCHANGED** — `chapter4_building_reference_datasets/system_prompt.py` now contains v3.1, v4, and v4.1. The v4.1 prompt is the v3.1 prompt + 3 surgical changes from the v4 judge re-run: (a) restored the "ask for the customer's account identifier on escalation" rule that v4 dropped (fixes the row 8 GDPR regression), (b) shortened the new "When you are answering directly" block (drops the worked examples, keeps the 3 rules + adds an explicit escalation carve-out), (c) an explicit "honest deferral is a PASS, not a weakness" line in the new block. **Real LLM + judge re-run completed on the 12-row refset** (see `v4_1_results.md`). Headline numbers vs v3.1 baseline on the same 12 rows, same judges, same model: **tone 50% → 75% (+25pp)**, **escalation 83% → 92% (+9pp)**, `policy_accuracy` 100% unchanged. **All 3 v4.1 success criteria met** (tone 70%+, escalation 90%+, no policy regression). v4.1 is the new production baseline. Cost: ~2.2x latency (12s/row vs 5.5s/row v3.1) — same as v4, not made worse by v4.1. Also shipped as part of this work: the regression gate (`pre_commit_check.py`) with the false-positive guard for the row 4 medical-escalation pattern, and the `metric_policy_accuracy.find_real_violations` helper that recognizes "escalating to a teammate" as a non-violation. See `chapter4_building_reference_datasets/v4_diff.md` for the v4 change record, `v4_judge_results.md` for the v4 regression analysis, and `v4_1_results.md` for the v4.1 ship decision. **Remaining v4.1 work to track**: 2 high-risk tone FAILs on the HONEST sub-dim (row 6 echoed customer's "duplicate" framing; row 8 too-confident on 24h GDPR) — these are next-quarter §8 #2 (calibration round) work, not blockers for the v4.1 ship.

**#2–#4 QUEUED** — see the table above.

---

## 9. Open questions

Things I still don't know how to evaluate, and what I'd need to find out. Honest > complete.

1. **How do we evaluate multi-turn memory?** A customer comes back the next day with "the shoes I asked about yesterday." The current refset is single-turn. I'd need a multi-turn refset with at least 20 rows, and a new metric that scores "did the bot correctly recall and reference the prior context?" — neither of which I have a rubric for yet.
2. **How do we evaluate brand voice beyond tone?** The 5-sub-dimension tone rubric (warm, brief, honest, calm, non-judgmental) catches obvious failures. It doesn't catch "this sounds like a generic AI, not like SoleMates." I'd need a brand-voice anchor set — 5–10 SoleMates responses a human team agrees on as "this is our voice" — and a new LLM judge trained against that anchor. We don't have the anchor set.
3. **Is the 100-query pilot statistically meaningful for the 4th-month traffic profile?** A 100-row pilot is the right size for v1. By the time we're at 5,000 conversations/day, the 1% must-review tier alone is 50 rows/day. I don't know whether the v3.1 prompt's failure modes scale linearly or whether new failure modes emerge at 10× the volume. The 1,000-query pilot (next-quarter #3) is the only honest answer I can give right now.
4. **What's the right inter-rater agreement threshold for the LLM judge?** I keep writing "agreement > 80%" in the cheat sheet. I haven't actually computed Cohen's kappa or Krippendorff's alpha on a real calibration set. I know the names; I haven't run the math. This blocks #2 in the next-quarter list from being a real validation instead of a vibes-based one.

---

## Appendix — artifact index

Every file referenced in this report, by section.

| Section | Source artifacts |
|---|---|
| §1 | `chapter1_wth_are_ai_evals/sole_mates_ai_charter.md` |
| §2 | `chapter3_evaluation_building_blocks/sole_mates_eval_table.md`, `chapter5_building_evaluation_metrics/metric_llm_judge_escalation.md`, `chapter5_building_evaluation_metrics/metric_llm_judge_tone.md` |
| §3 | `chapter4_building_reference_datasets/sole_mates_refset.csv`, `chapter4_building_reference_datasets/sole_mates_refset_sidecar.md` |
| §4 | `chapter5_building_evaluation_metrics/metric_results_v2.csv`, `chapter7_production_monitoring_strategies/v3_1_results_analysis.md` |
| §5 | `chapter6_production_challenge/production_pilot_v2_summary.md`, `chapter6_production_challenge/production_pilot_summary.md`, `chapter7_production_monitoring_strategies/v3_1_results_analysis.md` |
| §6 | `chapter7_production_monitoring_strategies/chapter7_summary.md`, `chapter5_building_evaluation_metrics/metric_policy_accuracy.py` |
| §7 | `chapter7_production_monitoring_strategies/chapter7_summary.md` (signal-metric divergence), `chapter7_production_monitoring_strategies/v3_1_results_analysis.md` |
| §8 | `chapter8_evaluation_process/sole_mates_eval_run_v1.md` |
| §9 | `chapter10_glossary_of_terms/eval_cheatsheet.md` (§6 "things I still don't fully get") |

---

**How to use this report.**
- **CEO / exec:** read §1 + §5 + §8. That's the headline.
- **Eng lead:** read §4 + §6 + §8. That's the architecture and roadmap.
- **Legal:** read §2 + §3 + §6. That's the "are we within policy" check.
- **Future me, next quarter:** read §8 + §9. That's the v2 backlog.
- **New PM joining the team:** read the whole thing, then read `chapter10_glossary_of_terms/eval_cheatsheet.md`. That's the 30-min onboarding.
