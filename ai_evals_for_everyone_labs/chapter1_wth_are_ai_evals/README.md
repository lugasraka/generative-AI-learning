# Chapter 1 — WTH are AI Evals?

> Source: [../ai_evals_for_everyone/chapters/01_wth_are_ai_evals.md](../ai_evals_for_everyone/chapters/01_wth_are_ai_evals.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- Traditional software is **deterministic**: given input X, you get output Y, every time. You test it once and trust it.
- AI products are **non-deterministic**: same question, different answers, every run. Same user rephrasing "where's my order?" can get 5 different responses.
- The input space is also **unbounded** — users type free text, upload photos, complain in novel ways you never predicted.
- This is why "evals" exists. The word is overloaded: it can mean benchmark scores, dataset labeling, or production dashboards. In this course, we use **evaluation** to mean *does this system behave acceptably in our specific product?*
- The mental model: **Input** (what goes in) → **Expected** (what should happen) → **Actual** (what did happen). Evaluation = closing the gap between Expected and Actual.
- Generic metrics like "helpfulness" are useless without a **rubric** that defines what good means in *your* context.

## Main takeaway

> **AI is non-deterministic and your input space is unbounded — so the only way to know if your product works is to define what "good" looks like in your domain and check the system against it, again and again.**

## Vibe-coding challenge

You're a PM at SoleMates about to ship an AI customer support agent. Before any code, write a **1-page AI Charter** for the bot. It should answer:

1. **What it does** — top 5 customer intents it handles (returns, refunds, sizing, tracking, etc.).
2. **What it must NEVER do** — give medical advice, promise refunds it can't issue, argue with angry customers, etc.
3. **What "good" looks like** — for each intent, one sentence describing the right behavior.
4. **What "bad" looks like** — for each intent, one sentence describing an unacceptable behavior.
5. **Who reviews the bot's outputs** — human-in-the-loop, sampling rate, escalation path.
6. **Why "add tests" isn't enough** — write 2-3 sentences explaining to a skeptical engineer why traditional unit tests won't cover this.

Save it as `sole_mates_ai_charter.md` in this folder.

### How to start
Tell me one of:
- *"Scaffold the charter as a markdown template"*
- *"I want to write it from scratch — give me 3 examples of good/bad pairs first"*
- *"Walk me through it without writing anything yet"*
- *"Give me a stretch variant for a regulated industry (e.g. orthopedic shoes)"*

### Bonus
Add a 7th section: **"What we still don't know"** — 3 open questions you'd want to answer before launch. (This is the seed of your reference dataset in Chapter 4.)
