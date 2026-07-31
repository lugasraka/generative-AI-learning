# Chapter 8 — The Complete Evaluation Process

> Source: [../ai_evals_for_everyone/chapters/08_evaluation_process.md](../ai_evals_for_everyone/chapters/08_evaluation_process.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- The complete process has **two phases**: pre-deployment validation (build confidence) and production monitoring (maintain quality + discover new issues).
- **7 steps** total:
  1. Understand your evaluation context (Ch 1-3)
  2. Build your reference dataset (Ch 4)
  3. Implement your evaluation metrics (Ch 5)
  4. Deploy smart log filtering (Ch 7)
  5. Select and deploy production metrics (Ch 7)
  6. Implement guardrails + improvement loops (Ch 7)
  7. Build emerging issue discovery (Ch 7)
- **Principles throughout**: start simple, focus on your context, collaborate across teams, embrace evolution, connect evaluation to improvement.
- The output of the whole process isn't a perfect system — it's a **continuously improving** system. The framework you build today will look different in 6 months.
- You already have 7 of the 7 pieces from earlier chapters. This chapter is about **running them in order** on one product, end-to-end.

## Main takeaway

> **The 7-step process is a loop, not a checklist. You do it once to launch, then you do it forever — each production insight feeds back into a better reference dataset, a sharper metric, a smarter filter.**

## Vibe-coding challenge

Run the **complete 7-step process** on SoleMates and produce a single artifact: `sole_mates_eval_run_v1.md`.

For each of the 7 steps, write 1-2 paragraphs answering:
- What did you do?
- What did you find?
- What did you change as a result?

**Reuse everything from earlier chapters.** This is the integration test:
- Step 1-2: pull from your AI Charter (Ch 1) + eval table (Ch 3)
- Step 3: pull from your reference dataset (Ch 4) + metrics (Ch 5)
- Step 4-6: pull from your production simulation (Ch 6) + log filter + metric plan (Ch 7)
- Step 7: invent one emerging issue you didn't anticipate in earlier chapters

### How to start
Tell me one of:
- *"Scaffold the 7-step `sole_mates_eval_run_v1.md` template"*
- *"I want to write steps 1-3 first, you scaffold 4-7"*
- *"Walk me through what step 1 should look like"*
- *"Show me a stretch: turn this into a quarterly review cadence"*

### Bonus
Add a **"What we'd do differently next quarter"** section at the end. This is the seed of your improvement flywheel — and the input to Chapter 11.
