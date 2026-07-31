# SoleMates — Reference Dataset Sidecar v0.1

> Sidecar to `sole_mates_refset.csv`. This file explains the **calls** I made so you can challenge them.
> Source chapters: 1 (charter), 2 (model choice), 3 (eval table).

---

## How the CSV was built

I pulled 8 rows from `sole_mates_eval_table.md` (Ch 3) and added 4 more that Ch 3 didn't cover but your real support distribution probably hits:

| Source | Rows | Why included |
|---|---|---|
| Ch 3 eval table | 1, 2, 3, 4, 5, 6, 7, 8 | Direct mapping; this is the core |
| Ch 2 stress tests | (folded into 3, 4, 6) | Same scenarios, reformatted for the CSV |
| Ch 1 charter gaps | 9, 10, 11, 12 | Exchange flow, goodwill / pet damage, off-script review ask, shipping logistics |

**Total: 12 rows.** Within the 10-20 sweet spot from the source chapter.

---

## Risk-level calls

| Level | Meaning | Rows |
|---|---|---|
| `low` | Bot fails → minor inconvenience, no business or legal risk | 1, 9, 11, 12 |
| `medium` | Bot fails → customer effort spike or single-instance brand damage | 2, 5, 10 |
| `high` | Bot fails → P0 incident: legal liability, refund fraud, medical issue, or data privacy breach | 3, 4, 6, 7, 8 |

**Reasoning per high-risk row:**

- **Row 3 (60-day return):** The trap from Ch 1. If the bot refunds, we lose $89+ and set a precedent. If it argues, we lose the customer and possibly get a chargeback.
- **Row 4 (sizing + medical):** Borders on orthopedic advice. A wrong recommendation here could literally hurt someone.
- **Row 6 (billing fraud claim):** Refund-before-verifying is a fraud vector. The word "fraud" alone raises legal exposure.
- **Row 7 (medical):** Charter Section 2 hard rule. Any medical advice is a P0.
- **Row 8 (GDPR):** Identity verification + data deletion is the worst possible thing to do wrong. Legal owns this row outright.

---

## Dimension frequency

How many rows each dimension tag appears in (these become your Ch 5 candidate metrics):

| Dimension | Rows | Total |
|---|---|---|
| `policy_accuracy` | 1, 2, 3, 5, 7, 8, 10, 12 | 8 |
| `information_gathering` | 1, 2, 4, 6, 9 | 5 |
| `escalation` | 3, 4, 6, 7, 8, 10 | 6 |
| `tone` | 3, 4, 5, 6, 10 | 5 |

**Insight:** `policy_accuracy` is the dominant dimension (8/12 rows). That's your #1 metric. The other three are roughly equal — they're the rubric, not the headline.

---

## What I changed vs. Ch 3

1. **Risk_level** is a new column — Ch 3 didn't have it. I added it so the refset is **actionable**, not just descriptive.
2. **Stakeholders** got squished into a single comma-separated column for CSV cleanliness. See Ch 3's table for the full per-cell breakdown.
3. **Added rows 9-12** to cover the cases Ch 3 missed:
   - Row 9: **exchanges** (different from returns — Ch 1 mentioned returns but not exchanges)
   - Row 10: **goodwill / pet damage** (off-policy but emotionally loaded — Ch 2 scenario 1 hinted at this)
   - Row 11: **off-script asks** (review links, etc. — not in the 5 in-scope intents)
   - Row 12: **logistics** (shipping questions — easy to hallucinate an answer to)
4. **Row 4 (sizing)** was promoted to `high` risk. Ch 3 had it as `medium` implicitly, but the medical-adjacent nature tips it to P0 territory.

---

## Things you'll want to challenge

1. **The 30-day return window.** I made that up. If it's actually 45 or 60 days, rows 3 and 10 change.
2. **Row 10's "no goodwill discount" rule.** If your CS team has a standard 10% goodwill credit the bot *can* offer, that row's expected_behavior is wrong.
3. **Row 11 (review links).** If you don't have a review page, this is "escalate" not "direct."
4. **Stakeholder assignment for row 6.** I put Legal as a consult. If your legal team wants to own any mention of the word "fraud" in customer-facing text, move them to "owns."

---

## What's next (Ch 5)

You'll turn these 4 dimensions into 4 evaluation metrics:
- `policy_accuracy` → code-based metric (regex on policy terms, fact-check against spec doc)
- `information_gathering` → LLM judge (did it ask the right questions?)
- `escalation` → code-based metric (was the right tag emitted?)
- `tone` → LLM judge with rubric (calibrated against human reviewers)

That's 2 code-based + 2 LLM-judge — exactly the mix the source chapter recommends.
