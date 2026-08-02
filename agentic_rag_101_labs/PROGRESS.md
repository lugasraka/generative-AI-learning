# Progress

Track your journey through the 6 parts. Check off as you go.

- [x] **Part 1** — Understanding RAG and Agents — `rag_comparison.py`
- [x] **Part 2** — What is Agentic RAG? — `customer_support_agent.py`
- [x] **Part 3** — Agentic RAG Capabilities — `capability_demo.py`
- [x] **Part 4** — Types of Agentic RAG — `architecture_selector.py` + `.html`
- [x] **Part 5** — Implementing Agentic RAG — `mini_rag_pipeline.py`
- [x] **Part 6** — Challenges and Future Directions — `risk_audit.py` + `.html`

## Recap

- **Keyword routing > LLM routing** — skip LLM calls for source selection when keywords map clearly. Save LLM for analysis/generation only.
- **Chunk quality > retriever sophistication** — a good chunker with keyword overlap beats a bad chunker with embeddings.
- **Confidence scoring prevents hallucination** — even simple retrieval-count heuristics catch most "no data" cases before the LLM fabricates.
- **Context-aware retrieval is the real win** — adding one keyword ("flight") to a query meaningfully changed what was retrieved and how good the answer was.
- **Multi-step reasoning needs vector search** — LLM decomposition produces verbose sub-queries that keyword retrieval can't match. Real fix: embeddings.
- **Mimo v2.5: good generation, weak structured output** — solid for free-form answers, struggles with JSON extraction.
- **Interactive HTML beats CLI for demos** — worth the extra effort for learning tools.

## Open items

- Keyword retrieval gaps — hybrid approach (keyword + embeddings) would fix Part 3 and Part 5 misses
- Re-retrieval reformulation — appending generic terms hurt; try LLM-based query rewriting instead
- HTML apps need mobile responsiveness + error states
