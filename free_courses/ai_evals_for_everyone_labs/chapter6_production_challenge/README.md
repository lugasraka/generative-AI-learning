# Chapter 6 — Production Challenges

> Source: [../ai_evals_for_everyone/chapters/06_production_challenge.md](../ai_evals_for_everyone/chapters/06_production_challenge.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- Pre-deployment evaluation happens in a **lab**: chosen examples, clear expected behavior, careful review. Production is a **zoo**: real users, real mess, real scale.
- Real users bring unexpected context (competitor questions, emotional stories, out-of-scope asks), test edge cases you never imagined, evolve their behavior over time, and arrive in **volume** that breaks manual review.
- With 5,000 daily conversations and a 95% pass rate, you still have 250 problematic interactions every day. You can't review them all.
- The question shifts from *"how did we do on this specific set?"* to *"how are we doing overall, and where should we focus?"*
- This is the move from **validation** (before launch) to **monitoring** (after launch). The two work as a flywheel: production issues become new test cases, which improve pre-deployment validation.
- Four core production challenges to plan for: **log filtering** (what to look at), **metric selection** (what to measure), **online vs offline** (when to measure), **emerging issue discovery** (what you didn't anticipate).

## Main takeaway

> **Production breaks your assumptions. The lab gets you ready; production teaches you what "ready" actually means. Plan for the four challenges — filtering, selection, online vs offline, and the unknown unknowns — or drown in data.**

## Vibe-coding challenge

Simulate SoleMates at production scale. Create a small script (`simulate_production.py`) that:

1. Generates 1,000 fake customer queries (mix of intents: 40% tracking, 25% returns, 15% sizing, 10% angry/complaint, 5% out-of-scope, 5% billing disputes). You can hardcode or pull from a small pool.
2. Calls an LLM (via opencode, or use a stub) on a sample of 50 to get `actual_output`.
3. Runs your **Chapter 5 code-based metric** on each output.
4. Reports:
   - Overall pass rate
   - Pass rate per intent
   - Top 3 failure clusters (by intent + a simple error tag)
5. Prints the **10 worst outputs** for manual review.

This is the "5,000 daily conversations" scenario compressed into 1,000. Notice what you would have missed in the lab.

### How to start
Tell me one of:
- *"Scaffold the 1,000-query generator"*
- *"I want to write the failure-clustering logic, you scaffold the data"*
- *"Walk me through how to stub an LLM call when I don't want to wait"*
- *"Show me a stretch: add a 'frustration' signal detector"*

### Bonus
Add a **cost analysis**: how much would it cost to run your LLM judge (from Chapter 5) on all 1,000? On 10%? Argue for your sampling rate.
