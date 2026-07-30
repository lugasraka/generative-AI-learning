# AI Evals for Everyone — Vibe-Coded Labs

A hands-on, vibe-coding companion to the [AI Evals for Everyone](../ai_evals_for_everyone/) course.

## What this is

The original course is conceptual — 10 chapters, all theory, no code. This folder gives you a **vibe-coding challenge per chapter** plus a capstone. You make the product calls; I help you build the artifacts.

**Persona:** You're a PM at **SoleMates**, a direct-to-consumer online shoe retailer. You're shipping an AI customer support agent. Every chapter adds another layer to that product's evaluation system.

## How to use

1. Open a chapter folder (e.g. `chapter1_wth_are_ai_evals/`).
2. Read the `README.md` — concept summary, main takeaway, vibe-coding challenge.
3. Tell me one of the "How to start" prompts at the bottom.
4. We iterate. You run things, I adjust.
5. Mark the chapter done in `PROGRESS.md` when it feels right.

## Rules of the road

- **No API keys required.** We use opencode itself as the LLM, or pure logic.
- **No production code expected.** Goal is to internalize the concept, not ship.
- **PM first.** You write rubrics, datasets, and acceptance criteria. I help turn them into runnable code.
- **One product, ten chapters.** SoleMates is the anchor. Reuse what you build — it should compound.
- **Vibe coding welcome.** Prompts like *"make it tighter"*, *"add a column"*, *"why did this fail?"* are the whole point.

## Setup

You need:
- `python3` (3.10+)
- The `opencode` CLI (or any local LLM runner)

That's it. No `pip install`, no API keys, no cloud.

## Folder layout

```
ai_evals_for_everyone_labs/
  README.md                          # this file
  PROGRESS.md                        # checklist of 11 chapters
  chapter1_wth_are_ai_evals/
  chapter2_model_vs_product_evaluations/
  chapter3_evaluation_building_blocks/
  chapter4_building_reference_datasets/
  chapter5_building_evaluation_metrics/
  chapter6_production_challenge/
  chapter7_production_monitoring_strategies/
  chapter8_evaluation_process/
  chapter9_common_misconceptions/
  chapter10_glossary_of_terms/
  chapter11_capstone_eval_report/
```

## Suggested pace

- 20-40 min per chapter
- 1 chapter per sitting is fine; binge if you're feeling it
- Don't skip the capstone — it ties everything to one artifact
