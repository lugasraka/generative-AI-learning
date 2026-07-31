# Chapter 5 — Implementing Evaluation Metrics

> Source: [../ai_evals_for_everyone/chapters/05_building_evaluation_metrics.md](../ai_evals_for_everyone/chapters/05_building_evaluation_metrics.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- Three ways to measure AI behavior: **human evaluation** (gold standard, doesn't scale), **code-based metrics** (fast, deterministic, perfect for objective checks), **LLM judges** (subjective, scalable, needs calibration).
- Most production systems use a **mix** of all three. Code checks for the easy stuff, LLM judges for nuance, humans for spot-checks and calibration.
- Code-based metrics fit: structure validation (valid JSON, required fields), performance (response time), content detection (required disclaimer present, banned words absent), classification flags (intent = "billing").
- LLM judges fit: tone assessment, escalation decisions, reasoning quality, safety. They need a **rubric** with acceptable / not-acceptable categories and concrete examples.
- **Calibration is everything.** An uncalibrated LLM judge is worse than no judge — it adds another layer of non-determinism. Test against human judgment across hundreds of examples before trusting it.
- LLM judge cost > code cost > nothing. Don't run an LLM judge on every production call; sample or guardrail it.

## Main takeaway

> **Pick the cheapest metric that catches the failure. Code checks for the objective stuff, LLM judges for the subjective stuff, humans for calibration. And never trust an uncalibrated LLM judge.**

## Vibe-coding challenge

Pick **one** behavior from your SoleMates reference dataset (recommend: "escalation accuracy" or "policy compliance for returns") and implement **all three** metric types for it. This is the heart of the chapter.

Create three files:

1. `metric_code.py` — code-based check using regex / string match / JSON validation. Should be < 30 lines.
2. `metric_llm_judge.md` — the LLM judge prompt with rubric (Acceptable / Not Acceptable categories + 3 examples). You'll run it manually or via opencode.
3. `metric_human_eval.md` — a simple human eval sheet (table with 5 sample inputs, columns for the human to mark Acceptable / Not Acceptable + reason).

Then compare all three on the **same 5 inputs** (use rows from your Chapter 4 refset). Where do they agree? Where do they disagree? The disagreements are the calibration gold.

### How to start
Tell me one of:
- *"Scaffold `metric_code.py` for return-policy compliance"*
- *"I want to write the rubric first, you scaffold the code"*
- *"Walk me through what an LLM judge prompt should look like"*
- *"Show me a stretch: a metric for 'appropriate empathy' (very hard)"*

### Bonus
Compute **agreement rates** between the three metrics (e.g. code vs human, judge vs human). If the LLM judge disagrees with humans on > 20% of cases, don't use it in production yet.
