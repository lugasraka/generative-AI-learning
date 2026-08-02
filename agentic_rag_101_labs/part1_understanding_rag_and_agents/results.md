# Part 1 — RAG Comparison Results

- **Model:** `opencode-go/deepseek-v4-flash`
- **Generated:** 2026-08-02 23:17:30

## Question 1: What is 2 + 2?

- **Difficulty:** easy
- **Note:** Should be answerable by plain LLM — no retrieval needed

| System | Retrieval | Correct | Answer |
|--------|-----------|---------|--------|
| Plain LLM | No | Yes (100%) | 4 |
| Basic RAG | Yes | No | The context does not contain that information. |
| Agentic RAG | Yes | Yes (100%) | The context doesn't cover arithmetic, but the answer is 4. |

## Question 2: What is the company travel policy?

- **Difficulty:** requires retrieval
- **Note:** Needs retrieval from company_docs

| System | Retrieval | Correct | Answer |
|--------|-----------|---------|--------|
| Plain LLM | No | Yes (100%) | From the Travel Policy doc (rag_comparison.py:31-41): - All domestic flights must be booked at least 14 days in advance.... |
| Basic RAG | Yes | Yes (100%) | - Domestic flights: booked at least 14 days in advance - Hotels: capped at $200/night - Rental cars: manager approval re... |
| Agentic RAG | Yes | Yes (100%) | Based on the context:  - All domestic flights must be booked at least 14 days in advance. - Hotel stays are capped at $2... |

## Question 3: What are the API rate limits and PTO policy?

- **Difficulty:** multi-source
- **Note:** Needs tech_kb AND hr_handbook — only agentic RAG should handle both

| System | Retrieval | Correct | Answer |
|--------|-----------|---------|--------|
| Plain LLM | No | No | I don't know — this repository is a Python learning lab with no documentation of API rate limits or a PTO policy. |
| Basic RAG | Yes | No | The context does not contain information about API rate limits or PTO policy. |
| Agentic RAG | Yes | Yes (80%) | Free tier: 60 req/min, 1000/day. Pro tier: 600 req/min, 50000/day. Enterprise: custom. PTO: 15 days/year (new hires), 20... |

## Summary

- **Total correct:** 6/9
