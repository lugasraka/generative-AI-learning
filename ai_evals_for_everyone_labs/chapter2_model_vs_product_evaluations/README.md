# Chapter 2 — Model vs Product Evaluations

> Source: [../ai_evals_for_everyone/chapters/02_model_vs_product_evaluations.md](../ai_evals_for_everyone/chapters/02_model_vs_product_evaluations.md)
> Anchor product: **SoleMates**, the shoe retailer's customer support AI.

## Summary

- **Model evaluations** (MMLU, HumanEval, GSM8K) measure *general capability* on standardized tasks. They help labs and infra teams pick base models.
- **Product evaluations** measure *whether the system behaves acceptably in your specific context* — your users, your data, your business rules, your risk tolerance.
- A model that scores 92% on MMLU can still be the wrong choice for SoleMates if it hasn't seen enough shoe-retail / customer-service data.
- The "benchmark illusion" — assuming strong model scores = product success — is one of the top reasons AI projects die in production.
- The right mental hierarchy: model capability → domain fit → production readiness → continuous improvement. Most teams overweight step 1 and ignore 2-4.
- Use model evals as a **filter** to eliminate obviously-bad candidates. Use product evals as the **deciding factor**.

## Main takeaway

> **Model benchmarks are a filter, not a verdict. The decision that matters is whether the model works for *your* product, *your* users, and *your* domain — and only product evaluation answers that.**

## Vibe-coding challenge

You're choosing between two model vendors for SoleMates' support bot. You can't afford both. Make a call.

**Step 1: Write the spec.** Create `sole_mates_model_choice.md` with:
- A table comparing **Model A** (high MMLU, expensive) vs **Model B** (lower MMLU, 3× cheaper, fine-tuned on retail CS data).
- 5 SoleMates-specific scenarios that would expose the difference (e.g. "customer furious about 60-day return, asks for manager", "subtle sizing question that needs empathy, not a fact").
- Your **decision** and the 3-sentence justification.

**Step 2: Run a tiny comparison.** Prompt both models (via opencode, or two different system prompts as a stand-in) on 2 of your scenarios. Compare outputs side-by-side. Did your prediction hold?

### How to start
Tell me one of:
- *"Scaffold the comparison table"*
- *"I want to write the 5 scenarios first — give me a starter list to riff on"*
- *"Walk me through how to use opencode to swap between two model personas"*
- *"Show me an insurance-industry stretch variant"*

### Bonus
Add a 6th scenario that's **adversarial** — designed to make the cheaper, fine-tuned model look bad. (Pre-tests your decision against a stress case.)
