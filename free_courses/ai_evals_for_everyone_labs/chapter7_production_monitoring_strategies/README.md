# Chapter 7 — Production Monitoring Strategies

> Source: [../ai_evals_for_everyone/chapters/07_production_monitoring_strategies.md](../ai_evals_for_everyone/chapters/07_production_monitoring_strategies.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- **Log filtering** is how you find signal in the noise. Define priority levels (high/medium/low) for your events, then add **signal-based sampling** on user behavior (very long or short conversations, retries, extensive editing, frustration language).
- Filter **dynamically**: increase sampling during error spikes, new launches, or seasonal events. Decrease when the system is stable (but never to zero).
- **Metric selection** is a value / reliability / cost trade-off. Plot each candidate metric on a 2×2 matrix: high-impact + low-cost = must have; high-impact + high-cost = strategic investment; low-impact = skip.
- **Online vs offline** is the guardrails vs improvement flywheel decision. **Online** = real-time, fast, for business-critical behaviors where failure = immediate harm (safety, compliance, escalation). **Offline** = batch, slower, for trend analysis and improvement.
- A guardrail triggers **immediate action** (handoff, block, escalation). An offline metric triggers a **learning cycle** (next sprint's improvement).
- **Emerging issue discovery** happens when user signals flag trouble but your metrics don't. That's a sign your evaluation framework has a blind spot. Investigate manually, find the hidden dimension, build a new metric.
- The full **discovery loop**: signals → filtering → metrics → investigation → new metrics → updated framework. It never ends.

## Main takeaway

> **Pick a handful of high-impact, low-cost metrics, run the critical ones online as guardrails, the rest offline as a learning flywheel, and always watch for the signal-metric divergences that reveal your blind spots.**

## Vibe-coding challenge

Build a **log filter + metric selection plan** for SoleMates. Two files:

1. `log_filter.py` — a function `score_log(log_line: dict) -> int` that returns an "interestingness" score (0-100). It should combine:
   - **Explicit signals**: mentions competitor name, mentions refund/chargeback, contains "lawyer" or "sue"
   - **Implicit signals**: conversation length anomaly (>3× median), retry count, sentiment (you can fake this with a tiny lexicon)
   - **Priority baseline**: billing dispute > return request > tracking question
   - Sort a list of 100 fake logs by score. Top 20 = the queue for human review.

2. `metric_plan.md` — a 1-page table listing your **5 chosen production metrics** for SoleMates. For each: name, online or offline, cost, reliability, why this one.

### How to start
Tell me one of:
- *"Scaffold the `score_log` function with stubbed signals"*
- *"I want to define the 5 metrics first, you scaffold the code"*
- *"Walk me through the online vs offline decision for one metric"*
- *"Show me a stretch: add a 'metric drift' detector over time"*

### Bonus
Add a **signal-metric divergence scenario** to `metric_plan.md`: describe a case where user behavior signals flag trouble but your chosen metrics show no problem. How would you investigate?
