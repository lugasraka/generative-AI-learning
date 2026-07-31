# SoleMates — Ch 5 Judges on the Ch 7 Top 20

> **What this analysis answers:** now that the log filter flagged 20 "interesting" rows, what do the LLM judges say about the bot's actual behavior on those rows? Are the judges catching things the log filter (and policy metric) missed?

## Headline: judges found real issues on **9/20** rows that the policy metric and log filter both missed

| Metric | Pass rate on top 20 | What it caught |
|---|---|---|
| **policy_accuracy** (code) | 20/20 = 100% | Nothing — all responses were policy-compliant |
| **log filter** (Ch 7) | 20/20 "flagged" | Routed high-signal interactions to humans |
| **escalation** (LLM judge) | 16/20 = **80%** | 4 NOT_ACCEPTABLE (real bot mistakes) |
| **tone** (LLM judge) | 13/20 = **65%** | 7 FAIL (subtle quality issues) |

**The judges' 9 findings (4 escalation + 5 unique tone) are the chapter's biggest result.** The log filter and policy metric *together* would have skipped every one of them.

---

## The 4 escalation NOT_ACCEPTABLE findings

These are cases where the bot *should* have escalated to a human but didn't, or did so without the right context. The policy code metric doesn't catch any of them because they aren't hard "NEVER" violations — they're soft judgment calls.

### id=72 (score 43, billing)
- **Input:** "I think I was double-billed. Order SM-47353. Can you check?"
- **Judge:** "Double-billing is a billing/payment issue requiring human authority, but the bot only asked follow-up questions without offering escalation."
- **Real problem:** the bot *could* have offered escalation, given the customer mentioned a duplicate charge. The judge thinks this is a payment/billing matter requiring human authority.

### id=90 (score 43, billing)
- **Input:** "I want a refund for order SM-97806 - charged me the wrong amount btw what's your favorite color?"
- **Judge:** "Refund request for wrong charge amount is payment-related and outside bot authority, but the bot only asked for more info without escalating."
- **Real problem:** refund for wrong amount = needs human. Bot didn't escalate.
- **Note:** the input also has the "what's your favorite color" off-script add (per Ch 6 generator), which the bot handled gracefully.

### id=28 (score 39, return_out_policy)
- **Input:** "Can I still return SM-94012? It's been like 50 days"
- **Judge:** "Bot offered escalation but did not attach the order context (SM-94012, 50 days past window) for the teammate."
- **Real problem:** v2 prompt fix #1 was "attach context on escalation." This is a v2 regression — the bot is offering escalation but losing the order context. **This is the Ch 5 v2 fix NOT working consistently.**

### id=43 (score 32, billing)
- **Input:** "I was charged $50 for shipping but my order SM-39451 said free shipping"
- **Judge:** "Billing dispute over a $50 charge requires human/payment authority, but the bot only asked for more info without escalating."
- **Real problem:** same as id=72 — refund/credit request needs human, bot didn't escalate.

**Pattern:** 3 of 4 escalation failures are billing disputes where the bot didn't escalate. This is a **systematic issue**, not a one-off.

---

## The 7 tone FAIL findings (with sub-dim breakdown)

| Sub-dim | Count | What it means |
|---|---|---|
| `HONEST` | 5 | Bot said something it shouldn't have (specifics, claims, false confidence) |
| `BRIEF` | 3 | Bot was too long or repetitive |
| `NON_JUDGMENTAL` | 1 | Bot asked unnecessary clarifying questions |

### HONEST failures (the most actionable)

| id | Score | What the bot said | Judge's concern |
|---|---|---|---|
| 32 | 43 | "Free shipping was definitely part of your offer" | Confirmed a claim it couldn't verify |
| 72 | 43 | "I can't pull up the order directly" without explaining why | Hedging, not honest about limitations |
| 37 | 39 | "Brooks Ghost, ASICS Gel-Nimbus" for a SoleMates customer | Recommending competitor products specifically (the system prompt says don't) |
| 89 | 39 | "True to Nike sizing" | Invented a sizing equivalence not in the catalog |
| 94 | 39 | "Nike women's run narrow → size 9.5" | Fabricated a fitting heuristic |

**Pattern:** the bot is making specific product claims it can't back up. **This is hallucination territory** — the policy code metric has a `hallucinated_spec` tripwire for "carbon plate" but doesn't catch sizing or shipping claims. **New metric needed.**

### BRIEF failures

| id | Score | Judge's concern |
|---|---|---|
| 11 | 39 | "Repetitive, restating the same handoff to a teammate twice" |
| 94 | 39 | "Wordier than necessary for a sizing question" (also HONEST) |
| 16 | 30 | "Unnecessary clarifying questions" (also NON_JUDGMENTAL) |

**Pattern:** the v2 prompt's "max 2 sentences + 1 follow-up question" rule is being violated in specific ways. The bot sometimes restates the handoff or asks 2-3 questions when 1 would do.

### NON_JUDGMENTAL failure

| id | Score | Judge's concern |
|---|---|---|
| 16 | 30 | "Bot ignores the stated intent (return) and asks unnecessary clarifying questions" |

Same row as the BRIEF failure. The bot ignored "I want to return my order" and asked about the size instead. **This is a real UX bug** — the bot should have acknowledged the return intent first.

---

## The 3-way metric comparison

This is what the full Ch 5 + Ch 7 picture looks like on 20 high-priority rows:

| | Caught issues? | False positives? | Cost |
|---|---|---|---|
| **policy_accuracy** (code) | 0/20 — never catches soft issues | 0/20 (per Ch 6 fix) | Free, instant |
| **log filter** (Ch 7) | Routes 20 "interesting" rows to humans; doesn't evaluate | N/A — it's a router, not a judge | Free, instant |
| **escalation judge** (LLM) | 4/20 — catches the real judgment errors | Some (row 32's "free shipping" wasn't actually a hallucination) | ~5s/call |
| **tone judge** (LLM) | 7/20 — catches subtler quality issues | 5 of the 7 HONEST fails look real; 1-2 are calibration-sensitive | ~5s/call |

**No single metric is sufficient. The mix catches different things.** This is the chapter's intended takeaway.

---

## What to do with these findings

1. **Add a new code-metric tripwire** for "specific competitor product recommendations" (catches the Brooks Ghost / ASICS Gel-Nimbus pattern). Quick fix: `\b(brooks|asics|gel-nimbus|ghost|pegasus|ultraboost)\b` outside of the user's input.
2. **Add a new code-metric tripwire** for "sizing equivalences" (catches "true to Nike sizing"). Quick fix: `\b(true to|equivalent to|runs like|fits like)\b.{0,40}\b(nike|adidas|new balance|brooks|asics)\b`.
3. **Tighten the v2 prompt** to add: "Do not name specific competitor products in your response, even if the user did." + "Do not make sizing equivalences (e.g. 'true to Nike sizing') — instead, link to the size guide."
4. **Run the calibration set** (Ch 9) on the 5 HONEST failures. Some might be judges being too strict; some might be real bugs.
5. **Track escalation-dispute rate** as a new metric. The 3-of-4 billing-dispute failure pattern is a real signal that the bot is under-escalating billing.

---

## Calibration observations (preview of Ch 9)

- The tone judge flagged "Brooks Ghost, ASICS Gel-Nimbus" as a HONEST failure because they sound like hallucinated products — but a sales rep at a shoe store *would* recommend competitor products as benchmarks. **Need to clarify in the rubric**: is the policy "no competitor products" or "no specific competitor product claims"? Currently the v2 prompt is ambiguous.
- The judge flagged "true to Nike sizing" as HONEST — this is a *legitimate* business claim that SoleMates' product team should be the source of truth on, not the LLM. The right fix is "always link to the size guide, don't make equivalences" — not "never use the word Nike."
- The judge flagged "free shipping was definitely part of your offer" as HONEST — but if the user *was* promised free shipping, the bot is right. **Hard to detect without access to the order's actual promotion history.** The right answer is: the bot should not make definitive claims about promotions; it should look up the order.

These are exactly the calibration issues the Ch 5 source chapter warned about: the LLM judge is "powerful but needs extensive validation." The findings here are real signals, but the rubric needs refinement before the judge can be trusted in production.

---

## Files

- `chapter7_production_monitoring_strategies/top20_judged.csv` — per-row escalation + tone verdicts
- `chapter7_production_monitoring_strategies/run_judges_on_top20.py` — the runner
- This analysis: `chapter7_production_monitoring_strategies/top20_judges_analysis.md`
