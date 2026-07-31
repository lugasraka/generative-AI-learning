# Part 4 — What Is RAG, and What Does It Mean to Make It Agentic?

## Concept in 10 lines

- **RAG** = Retrieval-Augmented Generation. Give the LLM relevant info *before* it answers.
- It solves the "model doesn't know my stuff" problem without expensive fine-tuning.
- Pipeline: data → chunk → index → retrieve top-k → stuff into prompt → generate.
- ~70% of enterprise GenAI use cases use RAG.
- **Traditional RAG** = one query, one retrieve, one answer. Good for Q&A.
- **Agentic RAG** = retrieve, reflect, re-retrieve, as many times as the task needs.
- RAG is essentially a *tool* — just one that returns knowledge instead of triggering an action.
- In agentic systems, RAG handles: missing context, hallucination checks, mid-task adaptation.

## Vibe-coding challenge

**Build a mini RAG pipeline in pure Python (no external DB).**

1. Hardcode 5-10 short "documents" (a few lines each) about a topic you care about — e.g., your favorite video game, a hobby, a company you know well.
2. Implement:
   - A naive **chunker** (just split by sentences or fixed-size windows).
   - A **retriever** using keyword overlap (no embeddings — just `set(words).intersection(...)`).
   - A **generator** that takes a query + retrieved chunks and produces a final answer (use the opencode CLI, or just template the answer).
3. Test with 2-3 questions where the answer exists in the docs and 1 where it doesn't.

> Bonus: extend with a second "retrieval" pass that runs *after* the first answer is generated — to check/refine. That's your first taste of agentic RAG.

### How to start

Tell me one of:
- *"Scaffold it in Python, no LLM"*
- *"Use opencode CLI as the generator"*
- *"Show me the diagram first"*
- *"I want to understand chunking — start there"*
