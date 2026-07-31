# Chapter 11 — Capstone: SoleMates Eval Report v1

> Sources: pulls from every prior chapter.
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- This is the integration test. You've built pieces across 10 chapters. Now bundle them into a single artifact a stakeholder (CEO, eng lead, legal, your future self) could actually read.
- A good eval report answers 5 questions in this order:
  1. **What is the system?** (scope, charter, what's in/out)
  2. **What does "good" look like?** (rubric, expected behaviors, dimensions)
  3. **How do we measure it?** (metrics, with reliability + cost noted)
  4. **How is it doing right now?** (current pass rates, top failure modes)
  5. **What are we doing about it?** (guardrails, monitoring, next-quarter plan)
- The hardest section is usually #4. You need to actually **run** the system and report real numbers, not vibes.
- An eval report isn't a one-time document. It's a **versioned artifact** (note the "v1"). You'll do v2 next quarter. The structure stays; the numbers change.

## Main takeaway

> **An eval report is the artifact that turns 10 chapters of theory into a single page a stakeholder can act on. If you can write v1, you can run a real AI product. If you can revise it quarterly, you can run a real AI business.**

## Vibe-coding challenge

Produce **`sole_mates_eval_report_v1.md`**. Required sections (in order):

1. **System overview** — 1 paragraph: what SoleMates' support bot does, what's in scope, what's not. (Pull from your Ch 1 charter.)
2. **Definition of "good"** — the rubric: 3-5 evaluation dimensions, each with a 1-sentence "good" and "bad" definition. (Pull from Ch 3 table + Ch 5 rubrics.)
3. **Reference dataset** — short table: 5 example inputs, expected behaviors, and which dimension each tests. (Pull from Ch 4 refset.)
4. **Metrics in production** — table of your 3-5 production metrics. For each: name, type (code/LLM/human), online or offline, cost tier, last week's pass rate. (Pull from Ch 5 + Ch 7.)
5. **Current state** — the real numbers: overall pass rate, top 3 failure clusters, one example failure per cluster. (Pull from Ch 6 simulation.)
6. **Guardrails** — list of online metrics that trigger immediate action, and what each guardrail does. (Pull from Ch 7.)
7. **Discovery loop** — 1-2 emerging issues you didn't anticipate in earlier chapters, and how you caught them. (Invent for this report.)
8. **Next quarter** — 3 concrete improvements you'll make, and the metric movement you expect. (Pull from Ch 8.)
9. **Open questions** — 2-3 things you still don't know how to evaluate, and what you'd need to find out. (Honest is better than complete.)

**Length budget: 3-5 pages.** If it's longer, you're writing an essay, not a report.

### How to start
Tell me one of:
- *"Scaffold the 9-section `sole_mates_eval_report_v1.md` with placeholder text"*
- *"I want to write section 4 (metrics) first, you scaffold the rest"*
- *"Walk me through how to fill in section 5 (current state) honestly"*
- *"Show me a stretch: add a 1-page 'board-ready' summary at the top"*

### Bonus
**Run the report by a real audience.** Show it to a friend, a coworker, or paste it into opencode with *"pretend you're a CEO — what 3 questions does this raise?"* The questions you can't answer are your v2 backlog.
