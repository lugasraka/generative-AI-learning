# Chapter 4 — Building Reference Datasets

> Source: [../ai_evals_for_everyone/chapters/04_building_reference_datasets.md](../ai_evals_for_everyone/chapters/04_building_reference_datasets.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- A **reference dataset** is 10-20 hand-picked real-world examples (input + expected behavior). It's the foundation of pre-deployment validation.
- Don't aim for comprehensive coverage. Aim for **scenarios you absolutely cannot get wrong**: high-risk situations, common workflows, edge cases that expose specific metrics.
- Source examples from real data (support tickets, chat logs) and from **domain experts** — engineers alone miss nuance. AI-generated synthetic data is shallow and misses the mess.
- The 6-step process: (1) generate examples → (2) run the system → (3) review with experts → (4) cluster errors → (5) decide which behaviors need ongoing metrics → (6) iterate.
- Use **yes/no** judgments from experts, not 1-5 scores. Scores hide reasoning. Explanations reveal it.
- One-off bugs get fixed once. **Recurring risks** need a metric. Don't measure what you wouldn't change the system over.
- A reference dataset is a **living document** — it grows as you discover new failure modes in production.

## Main takeaway

> **Start with 10-20 hand-picked, real-world examples — not 200 generic ones. Get domain experts to label them, cluster the failures, and turn the recurring patterns into metrics. Everything else is noise.**

## Vibe-coding challenge

Hand-craft a 12-row reference dataset for SoleMates. Save as `sole_mates_refset.csv` with these columns:

| input | expected_behavior | risk_level | dimension |
|-------|-------------------|------------|-----------|

Where:
- `input` — a realistic customer message (the messier, the better)
- `expected_behavior` — plain-language description, 1-2 sentences
- `risk_level` — `low` / `medium` / `high` (based on what happens if the bot fails)
- `dimension` — which evaluation metric this tests (e.g. `policy_accuracy`, `escalation`, `tone`, `information_gathering`)

Cover at least these scenarios:
- Lost receipt return
- Tracking question
- 60-day-late return request (outside policy)
- Anger + competitor mention
- Sizing question with empathy need
- Billing dispute
- Out-of-scope question (e.g. medical, competitor product)
- Edge: the customer is right and the policy is wrong

### How to start
Tell me one of:
- *"Scaffold the CSV with headers + 2 example rows"*
- *"I want to write 4 high-risk rows first, you fill in the rest"*
- *"Walk me through a single row's risk_level decision"*
- *"Convert to JSONL for an eval harness"*

### Bonus
After writing, **run the dataset** against an LLM (via opencode) and record the `actual_output` in a 5th column. Cluster the failures into 3-5 themes. These themes become your next chapter's metrics.
