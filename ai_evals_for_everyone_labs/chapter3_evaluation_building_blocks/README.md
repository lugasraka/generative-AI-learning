# Chapter 3 — The Evaluation Framework (Input / Expected / Actual)

> Source: [../ai_evals_for_everyone/chapters/03_evaluation_building_blocks.md](../ai_evals_for_everyone/chapters/03_evaluation_building_blocks.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- Every AI evaluation boils down to three things: **Input** (everything that affects the system — user query, history, retrieved docs, config), **Expected** (what should happen, written in plain language), **Actual** (what really happened, including intermediate steps).
- "Input" is more than the user's question. If you change the system prompt and your tests still pass, your tests weren't really testing that change.
- "Expected" is the hardest part. For a SoleMates "is this shoe safe for kids?" question, good behavior includes disclaimers, not just facts.
- "Actual" includes more than the final response — which tools got called, what data was retrieved, how confident the model sounded. Log all of it.
- One metric ("correctness") can't capture multiple dimensions. SoleMates needs separate scoring for policy accuracy, escalation, tone, and business risk.
- A **rubric** turns vague words like "tone" or "helpful" into concrete, debatable criteria. Without one, three reviewers give three different scores.
- Evaluation is **collaborative**: domain experts define good, PMs define user impact, engineers define what's measurable. No single role can do it alone.

## Main takeaway

> **Before you can measure anything, you have to agree on what "good" means in your context. The Input / Expected / Actual frame forces that conversation — and a rubric is how you keep it honest.**

## Vibe-coding challenge

Build the **first evaluation table** for SoleMates' support bot. Save as `sole_mates_eval_table.md` (or `.csv` if you want to vibe-code a loader).

For 8 realistic customer queries, fill in:
- **Input** — the customer message (be specific, include the messy bits)
- **Context that matters** — what else influences the answer (order history available? vip customer? competitor mentioned?)
- **Expected behavior** — in plain language, what should the bot do?
- **Acceptable response shape** — bullet list, JSON, escalation tag, etc.
- **Unacceptable failure modes** — what would make you pull the bot offline for that query?
- **Dimension tags** — which evaluation metric does this test (policy accuracy, tone, escalation, etc.)?

### How to start
Tell me one of:
- *"Scaffold an empty markdown table with 6 columns"*
- *"I want to write the 8 queries first — give me 4 starter scenarios"*
- *"Walk me through a single row in detail"*
- *"Convert this to a CSV + Python loader"*

### Bonus
Tag each row with the **stakeholder(s)** who should review the Expected behavior (CS ops, legal, sizing expert, retention). Notice where they disagree — that's the rubric gold.
