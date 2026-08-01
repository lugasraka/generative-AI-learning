# Part 7 — LLM Evaluation

> Source: [week6_llm_evaluation.md](../../Applied_LLMs_Mastery_2024/week6_llm_evaluation.md)

## Concept in 10 lines

- LLM evaluation has two dimensions: **pipeline evaluation** (are we using the right prompts, retrieval, and tools?) and **model evaluation** (is the model output good?).
- **Pipeline evaluation** covers: prompt quality (does the prompt produce consistent results?), retrieval quality (are the right chunks being retrieved?), and tool quality (are tool calls accurate?).
- **Retrieval metrics**: Context Precision (what fraction of retrieved docs are relevant?), Context Recall (did we retrieve all relevant docs?), Context Relevancy (how relevant are retrieved docs to the query?).
- **Generation metrics**: Faithfulness (does the answer stay grounded in the context?), Answer Relevance (does the answer address the question?), Answer Semantic Similarity (how close is the answer to a reference?).
- **Classic NLP metrics**: BLEU (precision of n-grams vs reference), ROUGE (recall of n-grams vs reference), Perplexity (how surprised is the model by the text?).
- **Alignment metrics** cover 9 dimensions: Truthfulness, Safety, Fairness, Robustness, Privacy, Machine Ethics, Transparency, Accountability, and Compliance.
- **LLM-as-judge**: use a strong model to rate outputs on a scale (1-5) with a rubric. Cheap, scalable, but can have its own biases.
- **Human evaluation** is the gold standard but expensive and slow. Best practice: use LLM-as-judge for iteration, human eval for final validation.
- The best evaluation approach combines automated metrics, LLM judges, and spot-check human reviews.

## Vibe-coding challenge

**Build an evaluation metrics calculator.** Create a Python script called `eval_metrics.py` that:

1. Defines 10 test samples as `(question, source_context, reference_answer, generated_answer)` tuples. Create realistic examples:
   - 3 where the generated answer is clearly correct and faithful
   - 3 where it's partially correct (some hallucination or missing info)
   - 2 where it's incorrect or contradicts the source
   - 2 where it's a refusal ("I don't know")

2. Implements these metrics as pure Python functions:
   - `exact_match(pred, ref)` — returns 1.0 if identical (after normalization), 0.0 otherwise
   - `token_overlap_f1(pred, ref)` — token-level F1 score (split on whitespace, compute precision/recall/F1)
   - `rouge_l(pred, ref)` — longest common subsequence ratio
   - `brevity_ratio(pred, ref)` — `min(len(pred), len(ref)) / max(len(pred), len(ref))`
   - `faithfulness(answer, source)` — fraction of named entities (capitalized words) in the answer that also appear in the source
   - `relevance(answer, question)` — fraction of question words that appear in the answer

3. Runs all 10 samples through all 6 metrics and stores results in a list of dicts.

4. Sends 3 samples to `opencode run -m <model>` with this prompt: "Rate this answer on a scale of 1-5 for faithfulness (sticking to the facts) and relevance (addressing the question). Return JSON: {\"faithfulness\": N, \"relevance\": N, \"reasoning\": \"...\"}". Parse the JSON responses.

5. Prints a **full results table**: for each sample, shows all 6 metric scores + the LLM judge scores.

6. Prints a **correlation summary**: for each metric, how well does it correlate with the LLM judge? (You can use a simple rank correlation — do the high/low scores align?)

> Bonus: implement a **threshold-based evaluator** that flags samples where faithfulness < 0.5 or relevance < 0.3, and prints a "needs review" alert list. Also implement `context_precision(retrieved_docs, relevant_docs)` and `context_recall(retrieved_docs, relevant_docs)` for retrieval evaluation.

### How to start

Tell me one of:
- *"Scaffold eval_metrics.py in Python"*
- *"Start with just exact_match and token_overlap_f1"*
- *"I want to write the 10 test samples together first"*
- *"Use opencode CLI for the LLM judge"*
