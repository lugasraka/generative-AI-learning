# Chapter 9 — Common Misconceptions

> Source: [../ai_evals_for_everyone/chapters/09_common_misconceptions.md](../ai_evals_for_everyone/chapters/09_common_misconceptions.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- The 12 misconceptions cluster into 3 groups: **foundation** (Ch 1-3), **pre-deployment** (Ch 4-5), **production** (Ch 6-7).
- Foundation: benchmarks ≠ product success, engineers can't design metrics alone, eval is not one-time setup.
- Pre-deployment: you don't need comprehensive coverage, code metrics aren't too simple, LLM judges aren't automatically best, detailed criteria alone don't make LLM judges work.
- Production: don't eval every interaction, don't build a 50-metric dashboard, online isn't always better than offline, eval ≠ A/B testing (they complement), metrics aren't fixed once shipped.
- The **right mindset**: start simple and evolve, focus on your context, collaborate across teams, expect continuous evolution, prioritize actionable insights over measurement.
- The reason misconceptions persist: AI eval is young, complexity creates uncertainty, tool vendors oversell sophistication, success stories hide the iterations.

## Main takeaway

> **Most AI eval failures come from over-rotating on one approach — too many metrics, too much LLM-judge magic, too much dashboard, not enough of *your* context. The right move is always: start simple, focus on your product, and let the system evolve.**

## Vibe-coding challenge

Hunt the misconceptions in the wild. Find **5 public artifacts** (blog posts, tweets, vendor docs, conference talks) that commit at least one of the 12 misconceptions from the source chapter. For each, write a 1-paragraph correction.

Save as `misconception_audit.md` with columns:
- **Source** — link or quote
- **Misconception(s) committed** — number(s) from the source chapter's list
- **What they're missing** — 1-2 sentences
- **SoleMates-specific correction** — how the same advice would land differently in *your* context

If you can't find real public examples, write 5 hypothetical ones (e.g. "A vendor pitch that says 'our 47-metric dashboard replaces your eval team'").

### How to start
Tell me one of:
- *"Give me a starter list of the 12 misconceptions to grep for"*
- *"I want to find 5 sources first, you help me classify them"*
- *"Walk me through one misconception in detail"*
- *"Show me a stretch: write a public-response blog post calling out 3 of the worst"*

### Bonus
Rank your 5 sources by "most harmful to a PM who reads it" and add a 1-sentence warning at the top of your audit.
