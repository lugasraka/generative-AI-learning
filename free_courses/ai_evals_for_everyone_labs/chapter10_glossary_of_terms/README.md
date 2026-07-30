# Chapter 10 — Glossary of Terms

> Source: [../ai_evals_for_everyone/chapters/10_glossary_of_terms.md](../ai_evals_for_everyone/chapters/10_glossary_of_terms.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- The source chapter defines 30+ terms used throughout the course. The four big framework concepts: **Input-Expected-Actual**, **Guardrails vs Improvement Flywheel**, **Discovery Loop**, and **Pre-Deployment Validation**.
- Process terms worth memorizing: calibration, emerging issue discovery, log filtering, signal-based sampling, signal-metric divergence, metric selection.
- Anti-patterns to recognize: **evaluation drift** (measuring what's easy instead of what matters), **metric overload** (more ≠ better), **calibration neglect** (shipping LLM judges without validating them), **coverage obsession** (trying to eval everything).
- 5 key principles: context is king, start simple and evolve, collaboration is essential, continuous learning, action over measurement.
- The vocabulary matters less than the concepts — but shared vocabulary is how teams align on the concepts.

## Main takeaway

> **A shared vocabulary is how you turn "evals" from a vague buzzword into a precise conversation. You don't need to memorize all 30+ terms — you need to know which 5-10 you'll actually use as a PM, and be able to spot the anti-patterns when they sneak in.**

## Vibe-coding challenge

Build your **personal eval cheat sheet** — a quick-reference doc you can hand to a new PM on your team and have them productive in 30 minutes.

Save as `eval_cheatsheet.md`. Structure:
1. **The 5 terms I use most** (pick the 5 you reached for most across Chapters 1-9) — definition in your own words + a 1-line SoleMates example.
2. **The 3 anti-patterns I now recognize** — short description + a sentence on how to spot each.
3. **The 4-step mental model** (your own compressed version of Input → Expected → Actual → Metric) — 4 bullets, max.
4. **My "if you only remember one thing"** — your single best takeaway from the course, written to future-you.
5. **The 3 questions I ask before shipping any new metric** — make them sharp and reusable.

### How to start
Tell me one of:
- *"Scaffold an empty `eval_cheatsheet.md` with 5 sections"*
- *"I want to write the '5 terms' section first — help me pick which 5"*
- *"Walk me through what makes a good anti-pattern callout"*
- *"Show me a stretch: turn this into a 1-page printable PDF"*

### Bonus
Add a 6th section: **"Things I still don't fully get"** — 2-3 concepts you'd want a deeper course on. (Good signal for which advanced topic to study next.)
