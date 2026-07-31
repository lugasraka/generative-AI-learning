# SoleMates — Chapter 7: Production Monitoring Strategies

> **What this chapter delivers:** a `score_log()` function that ranks production
> traffic by "interestingness," so the human review queue can focus on the
> rows most likely to expose real problems.
>
> **Input data:** 100 Ch 6 pilot rows, extended with 6 synthetic metadata fields
> (`pilot_with_metadata.csv`)
>
> **Output:** `pilot_scored.csv` with score + signal breakdown per row

---

## Headline: 1 must-review + 19 should-review out of 100 rows

| Tier | Score | Count | % | What it means |
|---|---|---|---|---|
| `must_review` | ≥ 60 | **1** | 1% | Top of human queue — review within 1 hour |
| `should_review` | 30-59 | **19** | 19% | Second tier — review within 24 hours |
| `low_priority` | < 30 | **80** | 80% | Spot-check 5% (4 rows) for calibration |

**Without the log filter, you'd review 100/100 rows manually (~3 hours at 2 min/row).** With the filter, you review ~20/100 (~40 min) and the most important 1% gets attention first.

---

## The scoring function

7 signals + 1 priority baseline, each weighted independently. Total max ~220 raw points, normalized to 0-100.

| Signal | Type | Weight | What it catches |
|---|---|---|---|
| `competitor_mention` | explicit | +30 | User comparing to Nike/Adidas/etc |
| `legal_keywords` | explicit | +40 | "lawyer", "sue", "chargeback", "fraud" |
| `medical_keywords` | explicit | +25 | "surgery", "plantar", "doctor", etc. |
| `refund_amount_high` | explicit | +25 | Refund request ≥ $100 |
| `sentiment` | implicit | +20 | "furious", "ridiculous", "terrible" |
| `message_length` | implicit | +15 | Message ≥ 200 chars (frustrated or complex) |
| `retry_count` | implicit | +25 | Retried ≥ 2 times |
| `priority_baseline` | intent | +5 to +30 | billing/return-out-of-policy/etc. floor |

**Normalization:** raw / 220 × 100, capped at 100.

---

## The 1 must-review row (id=80)

> "I see TWO charges from you guys on my statement from March 3rd. One for $89 and one for $89. This is fraud. I want my money back."

- **Score:** 61
- **Signals fired:** `legal_keywords` (fraud), `refund_amount_high` ($250), `retry_count` (3), `message_length` (long), `priority_baseline` (billing_dispute = +30)
- **Policy metric:** PASS (the bot held the line, said "I can't process refunds directly, let me connect you with a teammate")
- **Why it's must-review anyway:** this is a P0 customer interaction. Even though the bot did the right thing, you want a human to (a) verify the response was actually good, (b) follow up with the customer, (c) make sure no fraud actually happened

This is the **discovery loop in action**: a row the policy metric would have skipped is now visible to the human team.

---

## Top-20 by intent (the actual review queue)

| Intent | Count in Top-20 | Why |
|---|---|---|
| `billing_dispute` | 9 | Always high-priority: financial impact, fraud risk |
| `sizing` | 4 | Sizing-with-medical-language (bunions, high arches) + retries = escalation risk |
| `return_in_policy` | 4 | High retry count or refund amount flagged them |
| `return_out_policy` | 3 | Outside policy + retry = needs human judgment |

**No `tracking` or `product_question` rows in the top 20.** That's the filter working as designed — those intents are routine and don't need human review.

---

## Signal-metric divergence: the blind spots

**This is the most important finding in the chapter.** All 20 top-scored rows PASS the policy metric. The policy metric alone would have skipped every single one of them.

That doesn't mean the policy metric is wrong — those responses were all policy-compliant. It means the policy metric **only catches catastrophic failures**, not subtle quality issues. The log filter fills the gap by routing *suspicious-looking interactions* (regardless of whether the bot did anything wrong) to human review.

### Examples of the divergence

| id | Score | Signals | What the log filter sees | What the policy metric sees |
|---|---|---|---|---|
| 80 | 61 | legal + $250 + 3 retries | Customer mentioned fraud, large refund, retried 3 times | PASS (bot escalated correctly) |
| 37 | 39 | competitor + long + 2 retries | Customer mentioned competitor, complex sizing question, stuck | PASS (bot handled it) |
| 52 | 36 | medical + long + 2 retries | Bunions, complex, retried | PASS (bot held the medical line) |
| 11 | 39 | long + $150 + 2 retries + multi_intent | Complex multi-intent return question | PASS (bot handled both) |

**Pattern:** every top-20 row either has a financial/medical/legal angle OR a frustrated user (retries, long messages). The log filter is routing them to humans not because the bot did something wrong, but because *if* something went wrong on one of these, it would matter a lot.

---

## Cost analysis (production projection)

For a real production system at SoleMates scale (~5,000 conversations/day per the source chapter):

| Strategy | Rows reviewed/day | Time at 2min/row | % of traffic |
|---|---|---|---|
| No filter (review everything) | 5,000 | 167 hours | 100% |
| Random 10% sample | 500 | 17 hours | 10% |
| Log filter top 20% | 1,000 | 33 hours | 20% |
| Log filter top 5% (must + half should) | 250 | 8 hours | 5% |
| Log filter top 1% (must only) | 50 | 1.7 hours | 1% |

**My recommendation:** review must + should (the top ~20% by score). At 33 hours/day you still need to triage, but you'll catch the issues random sampling would miss.

For a small team, start with the top 5% and grow as you hire reviewers.

---

## Recommended next step (carries into Ch 8)

1. **Lock the must-review threshold at 60.** Score ≥ 60 = top of queue.
2. **Sample 5% of low-priority** for calibration — these are your "did anything subtle go wrong?" check.
3. **Re-run the log filter weekly** against the production traffic. Track which signals fire most often. Over time, retire signals that never fire.
4. **Add a new signal:** "user clicked 'thumbs down'" once you have thumbs-up/down buttons. That's the strongest implicit signal of all.

---

## Artifacts

| File | Purpose |
|---|---|
| `chapter7_production_monitoring_strategies/extend_pilot_metadata.py` | Adds 6 synthetic metadata fields to the Ch 6 pilot |
| `chapter7_production_monitoring_strategies/score_log.py` | The `score_log()` function — 7 signals + priority baseline |
| `chapter7_production_monitoring_strategies/score_demo.py` | Scores 100 rows, sorts, sanity-checks, finds divergence |
| `chapter7_production_monitoring_strategies/pilot_with_metadata.csv` | 100 rows + metadata |
| `chapter7_production_monitoring_strategies/pilot_scored.csv` | 100 rows + score + signal breakdown |
| `chapter7_production_monitoring_strategies/chapter7_summary.md` | This file |

## Open calibration questions (preview of Ch 9)

1. **The competitor-mention signal is firing on "I'm usually a women's 9 in Nikes"** — that's a sizing question, not a competitive comparison. Should the signal require "compare", "better", "worse", or similar intent words?
2. **The retry signal is firing on too many rows** (79/100 have retry_count > 0). The threshold might be too low; real production usually has < 20% retries.
3. **The medical-keywords signal is firing on "bunion" and "plantar"** — these are shoe-related terms in customer-speak, not always medical claims. The policy metric and the log filter disagree on what "medical" means.

These are all calibration issues — the kind you'd address with a 50-row hand-labeled set (Ch 9 work).
