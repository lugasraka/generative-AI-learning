# Part 7 — LLM Evaluation Results

> **Model:** `opencode-go/deepseek-v4-flash`  
> **Date:** 2026-08-02 09:49:14

## Metric Results

| # | Type | Exact | Token F1 | ROUGE-L | Brevity | Faithfulness | Relevance | Judge F | Judge R |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | correct | 0.00 | 1.00 | 0.67 | 1.00 | 1.00 | 0.83 | 5/5 | 5/5 |
| 2 | correct | 0.00 | 0.62 | 0.62 | 0.48 | 1.00 | 0.33 | -- | -- |
| 3 | correct | 0.00 | 0.42 | 0.42 | 0.54 | 1.00 | 0.25 | -- | -- |
| 4 | partial | 0.00 | 0.59 | 0.35 | 0.79 | 0.33 | 0.75 | -- | -- |
| 5 | partial | 0.00 | 0.75 | 0.75 | 0.60 | 1.00 | 0.29 | 4/5 | 5/5 |
| 6 | partial | 0.00 | 0.50 | 0.50 | 0.43 | 1.00 | 0.50 | -- | -- |
| 7 | incorrect | 0.00 | 0.82 | 0.82 | 0.80 | 1.00 | 0.88 | 1/5 | 2/5 |
| 8 | incorrect | 0.00 | 0.19 | 0.19 | 0.60 | 1.00 | 0.29 | -- | -- |
| 9 | refusal | 0.00 | 0.00 | 0.00 | 0.41 | 1.00 | 0.00 | -- | -- |
| 10 | refusal | 0.00 | 0.11 | 0.11 | 0.85 | 1.00 | 0.14 | -- | -- |

## Correlation Summary

| Metric | Judge faithfulness | Judge relevance |
|---|---:|---:|
| exact_match | +0.00 | +0.00 |
| token_f1 | +0.50 | +0.00 |
| rouge_l | -1.00 | -0.87 |
| brevity | +0.50 | +0.00 |
| faithfulness | +0.00 | +0.00 |
| relevance | -0.50 | -0.87 |

## Needs Review

- Sample 3: faithfulness or relevance is below threshold.
- Sample 4: faithfulness or relevance is below threshold.
- Sample 5: faithfulness or relevance is below threshold.
- Sample 8: faithfulness or relevance is below threshold.
- Sample 9: faithfulness or relevance is below threshold.
- Sample 10: faithfulness or relevance is below threshold.

## Metric Notes

- Faithfulness uses capitalized-word entity overlap as a transparent heuristic.
- Relevance is the fraction of unique question words found in the answer.
- Correlations are exploratory because the LLM judge scores only three samples.
