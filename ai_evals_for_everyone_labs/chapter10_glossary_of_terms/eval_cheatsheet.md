# SoleMates — Eval Cheat Sheet v0.1

> **Date:** [today]
> **Audience:** PM at SoleMates working on the AI support agent. Also useful as a handoff doc for new team members.
> **Scope:** 5 terms I use most, 3 anti-patterns I now recognize, the 4-step mental model, the 1 thing to remember, 3 questions before shipping a metric, things I still don't fully get, and a glossary of 30+ terms each with a 1-line SoleMates example.
> **Grounded in:** 10 chapters of work. Every example is real, not hypothetical.

---

## Section 1 — The 5 terms I use most

### 1. Input / Expected / Actual
The mental model for every evaluation. Input is everything affecting the system (user query, history, system prompt). Expected is what should happen, in plain language. Actual is what really happened, including intermediate steps. Evaluation = closing the gap between Expected and Actual.
*Example: For the 60-day out-of-policy return (Ch 3), Input = angry customer message + order context; Expected = "acknowledge, hold the policy line, offer escalation"; Actual = the bot's response + whether the policy was held.*

### 2. Guardrail
A metric that runs online (on every production interaction) and triggers an immediate action when it fires.
*Example: `policy_accuracy` is a guardrail — it runs on every SoleMates response, and when it fires (medical advice, refund fraud), the bot's output is blocked or escalated before reaching the customer.*

### 3. Improvement flywheel
A metric that runs offline (sampled, batched, weekly) and feeds the next prompt/model iteration. The output isn't an action — it's a learning.
*Example: The `tone` LLM judge on the top 20 by score fed the v3 → v3.1 prompt iteration. The 3 WARM failures on escalations in v3 became the structured 3-step warm-escalation rule in v3.1.*

### 4. Log filtering
Sampling production traffic by signal to find the rows most worth human review. The opposite of reviewing everything.
*Example: Our 7-signal `score_log` function scores 100 pilot rows: 1 must-review (the duplicate-charge + "fraud" case), 19 should-review, 80 low-priority. We review the top 20, not all 100.*

### 5. Signal-metric divergence
A case where user signals (the log filter) flag a row as interesting, but the existing metrics say everything is fine. This is a blind spot.
*Example: All 20 top-scored rows in our pilot PASS the policy metric. The log filter caught them because of $250 refund / fraud mention / 3 retries — but the policy metric only checks the bot's text. The metric is correct, but it's not the whole story.*

---

## Section 2 — The 3 anti-patterns I now recognize

### 1. Metric overload
Adding more metrics because more = better. Each metric costs you to build, run, interpret, and maintain. The 80/20 rule applies: 4 well-chosen metrics catch 80% of the issues; the other 43 catch diminishing returns.
*Recognition cue: a dashboard that shows 47 numbers is a dashboard no one reads.*

### 2. Calibration neglect
Shipping an LLM judge without testing it against human labels on your product's data. An uncalibrated judge is worse than no judge — it adds a layer of non-determinism that *looks* like quality control.
*Recognition cue: the judge gives you verdicts you don't trust but can't explain. The fix: 50 hand-labeled examples, compute inter-rater agreement with the judge, refine the rubric until agreement > 80%.*

### 3. Coverage obsession
Trying to enumerate every possible input. The input space is unbounded; the output is non-deterministic. You can never eval "all" the cases. Aim for *scenarios you absolutely cannot get wrong* (small refset) + *realistic production distribution* (pilot sample) + *the long tail* (log filter).
*Recognition cue: the team is spending 6 months building a 500-row refset and hasn't shipped the eval work yet.*

---

## Section 3 — The 4-step mental model

1. **Input** — what the system sees (user query, history, system prompt, retrieved docs)
2. **Expected** — what should happen, in plain language, debatable, grounded in your product
3. **Actual** — what really happened, including intermediate steps (tool calls, retrieved docs, the final response)
4. **Metric** — the thing you measure to close the gap between Expected and Actual

If you can't fill in Expected, you don't have a metric. You have a vibe.

---

## Section 4 — If you only remember one thing

> **Start simple. Add only when you can name the failure mode.**

We started with 4 metrics. We added 0. We fixed 2 of those 4. We didn't add a 5th because we couldn't name a real failure mode the other 4 would miss. The "add a 5th" pressure comes from vendor pitches and 47-metric dashboards. Resist it until you have a concrete failure mode to point at.

---

## Section 5 — 3 questions before shipping any metric

1. **How will I know when this metric is lying to me?**
   Every metric lies sometimes. Code metrics have false positives (Ch 6: `medical_advice` regex on legitimate sizing). LLM judges have calibration drift. Define the failure mode before you ship.
2. **What's the cost per call?**
   This decides online vs offline. Sub-millisecond code metrics run on every interaction. 5-second LLM judges run on samples. The cost difference is 5,000× and the decision is structural.
3. **What action does the result trigger?**
   If there's no action, why measure? "We track this number weekly" is not an action. "When X crosses threshold Y, we ship a new prompt" is an action. A metric without an action is a dashboard widget.

---

## Section 6 — Things I still don't fully get

These are the concepts I'd want a deeper course on:

1. **Inter-rater agreement statistics.** We talk about "agreement > 80%" but I haven't actually computed Cohen's kappa or Krippendorff's alpha on a real calibration set. I know the names; I haven't run the math.
2. **Drift detection over time.** Our v3.1 prompt is "the baseline" but I don't have a system to detect when it starts drifting. I know drift will happen; I don't know how to alarm on it.
3. **Online guardrail architectures.** I know `policy_accuracy` should be online. I don't know whether that means a separate service, a pre-commit hook, a post-response filter, or an in-prompt instruction. The deployment shape is unclear.

---

## Section 7 — Glossary (30+ terms, 1-line SoleMates example each)

### Framework concepts

**Input / Expected / Actual** — what the system sees, what should happen, what did happen. *Example: see Section 1.1.*

**Guardrails vs Improvement Flywheel** — online metrics that trigger immediate action vs offline metrics that feed the next iteration. *Example: `policy_accuracy` is a guardrail; `tone` judge is the flywheel.*

**Discovery Loop** — the cycle of finding issues in production and feeding them back into better metrics, datasets, and prompts. *Example: the 5 issues surfaced in Ch 5/7 became the v2→v3→v3.1 prompt changes.*

**Pre-Deployment Validation** — the Ch 1-5 work: build the rubric, build the refset, build the metrics, before any user sees the system. *Example: the 12-row refset + the 4-metric suite were the pre-deployment validation for SoleMates.*

### Process terms

**Calibration** — testing an LLM judge against human-labeled examples to confirm it agrees with humans on what "good" means. *Example: the 5 persistent HONEST failures in Ch 7 are the calibration set for v2 of the runbook.*

**Emerging Issue Discovery** — finding issues the existing metrics didn't anticipate. *Example: the 3 prompt iterations surfaced 5 issues the original refset didn't cover.*

**Log Filtering** — sampling production traffic by signal to find the rows most worth human review. *Example: see Section 1.4.*

**Signal-Based Sampling** — sampling based on observable signals (retry count, sentiment, dollar value) rather than random sampling. *Example: the `score_log` function samples by retry count + sentiment + legal keyword + intent priority.*

**Signal-Metric Divergence** — see Section 1.5.

**Metric Selection** — choosing which metrics to build, given value/reliability/cost. *Example: we picked 4 metrics (2 code, 2 LLM judge) over a 47-metric dashboard.*

**Online vs Offline Evaluation** — real-time vs batched. Online catches catastrophic failures in the moment; offline catches subtle quality issues over time. *Example: see Section 1.2 and 1.3.*

**Reference Dataset** — a small, hand-picked set of real-world examples with expected behavior. *Example: 12 rows in `sole_mates_refset.csv`.*

**Rubric** — the definition of "good" for a specific behavior, in plain language with concrete examples. *Example: the Ch 5 escalation rubric has "Acceptable" and "Not acceptable" categories with 5 worked examples each.*

**Production Monitoring** — the Ch 6-7 work: how the system behaves in real traffic, at scale, with real users. *Example: the 100-row pilot run through the simulator is production monitoring at a small scale.*

**Stakeholder Tagging** — marking each eval row with who should review the "expected behavior." *Example: the 8 Ch 3 rows each have a stakeholder (CS Ops, Legal, Billing, etc.) who owns the Expected column.*

**Adversarial Test** — a test case specifically designed to catch a known failure mode. *Example: the 17 Ch 5 adversarial test cases for the `medical_advice` regex.*

**False Positive** — the metric says FAIL when the response was actually fine. *Example: the Ch 6 v1 metric flagged "I'd recommend sizing down" as medical advice.*

**False Negative** — the metric says PASS when the response was actually broken. *Example: none caught yet, but the 5 HONEST failures in Ch 7 are likely this category.*

**Drift** — the slow change in model behavior (model drift) or in the metric's relationship to reality (metric drift) over time. *Example: the v3.1 prompt is the baseline; we expect drift over 3-6 months that requires v4 or v5.*

**Inter-Rater Agreement** — a statistic for how often two reviewers (humans or LLM judges) agree on the same examples. *Example: not yet computed for SoleMates; this is in the Section 6 "still don't get" list.*

**Tripwire** — a code metric that fires on a specific pattern, usually a known failure. *Example: the `hallucinated_spec` regex in `policy_accuracy` fires on "carbon plate."*

**Priority Baseline** — a floor score in the log filter based on intent, before any other signals are counted. *Example: billing disputes start with +30, returns-out-of-policy with +20, tracking with +5.*

**High-Risk Row** — a refset or pilot row where a bot failure would have serious consequences. *Example: rows 3, 4, 6, 7, 8 in the Ch 4 refset are flagged high-risk.*

**LLM Judge vs Human Eval vs Code Metric** — three ways to score a response. *Example: see Section 1 — the 4 SoleMates metrics are 2 code + 2 LLM judge; human eval would be the "calibration" set.*

### Anti-patterns

**Evaluation Drift** — the metric stays the same but the system changes, and the metric stops catching real failures. *Example: not yet seen in SoleMates; the v3.1 prompt will drift.*

**Metric Overload** — see Section 2.1.

**Calibration Neglect** — see Section 2.2.

**Coverage Obsession** — see Section 2.3.

### Principles

**Context is King** — generic metrics (helpfulness, accuracy) are useless without a product-specific definition of good. *Example: "helpfulness" in a billing dispute means "escalate with context," not "answer the question."*

**Start Simple and Evolve** — begin with 2-3 metrics, add only when you can name a real failure mode the others miss. *Example: 4 metrics after 8 chapters; no 5th yet because no failure mode justified it.*

**Collaboration is Essential** — no single role can design evals alone; you need PM (rubric), engineer (mechanism), domain expert (real-world context). *Example: the Ch 3 stakeholder disagreements forced us to surface tradeoffs engineers alone would have missed.*

**Continuous Learning** — the eval framework is software, not a launch deliverable. Iterate as the system and traffic evolve. *Example: 2 metric versions + 3 prompt versions in 8 chapters.*

**Action Over Measurement** — a metric without an action is a dashboard widget. *Example: see Section 5 question 3.*

---

## How to use this cheat sheet

- **New PM joins SoleMates** → send them this file. The 5 use-most terms + 3 questions + glossary = 30 min to productive.
- **Before a stakeholder meeting** → re-read Section 4 ("if you only remember one thing").
- **Before shipping a new metric** → answer Section 5's 3 questions first. If you can't, don't ship.
- **Quarterly review** → re-read Section 6 ("things I still don't get"). The list should shrink over time.
- **For the Ch 11 capstone** → pull Section 1 + Section 4 + Section 5 directly into the eval report.
