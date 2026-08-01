# Part 5 — Retrieval-Augmented Generation (RAG)

> Source: [week4_RAG.md](../../Applied_LLMs_Mastery_2024/week4_RAG.md)

## Concept in 10 lines

- **RAG** = Retrieval-Augmented Generation. Instead of relying on the model's training data, you retrieve relevant documents at query time and stuff them into the prompt.
- RAG has 3 stages: **Ingestion** (chunk → embed → index), **Retrieval** (query → find relevant chunks), **Synthesis** (generate answer using retrieved context).
- **Chunking** splits documents into manageable pieces. Naive approaches: fixed-size windows, sentence splitting. Smarter: recursive splitting, content-aware chunking.
- **Retrieval** finds the most relevant chunks. Simple: keyword overlap (BM25-style). Better: semantic similarity with embeddings. Best: hybrid (keyword + semantic).
- **Synthesis** feeds retrieved chunks + the user query to the LLM, which generates a grounded answer. The prompt says "answer using ONLY the context below."
- **RAG vs. Fine-tuning**: RAG is cheaper, faster to deploy, easier to update (just swap docs), and more transparent (you can show sources). But it depends on retrieval quality.
- **Common RAG failures**: bad chunking loses context, poor retrieval returns irrelevant docs, LLM ignores the context and hallucinates anyway.
- **Improving RAG**: HyDE (generate a hypothetical answer first, use it to search), reranking (score retrieved results), query transformation (expand/rewrite the query).
- **Agentic RAG**: the model can decide to retrieve multiple times, reflect on its answer, and refine — not just a single retrieve-then-generate pass.

## Vibe-coding challenge

**Build a RAG pipeline from scratch.** Create a Python script called `rag_pipeline.py` that:

1. Defines a **knowledge base** of 15+ short documents (2-5 sentences each) about a topic you care about. Examples: history of a sport, a programming language, a company, a hobby.

2. Implements a **chunker** function:
   - `chunk(text, window=2)` — splits text into overlapping sentence windows
   - Each chunk gets an ID like `d0s0`, `d0s1` (document 0, sentence 0)
   - Each chunk stores its text and a set of keyword tokens (lowercase, stopwords removed)

3. Implements a **retriever** function:
   - `retrieve(query, top_k=3)` — scores chunks by keyword overlap with the query
   - Uses BM25-style scoring: `score = sum(1 / (k1 + tf))` for each matching term
   - Returns the top_k chunks sorted by score

4. Implements a **generator** function:
   - `generate(query, chunks)` — stuffs retrieved chunks into a prompt template and calls `opencode run -m <model>`
   - Prompt template: "Answer using ONLY the context below. If the answer is not in the context, say 'I don't have enough information.' CONTEXT: {chunks} QUESTION: {query} ANSWER:"

5. Tests with 4 queries:
   - 2 queries whose answers are clearly in the docs
   - 1 query that's partially covered
   - 1 query that's completely out of scope (should get "I don't have enough information")

6. For each query, prints: the query, the top 3 retrieved chunks (with IDs and scores), and the generated answer.

> Bonus: implement **agentic RAG** — after the first answer, ask the LLM "What follow-up search query would help you verify or refine this answer?" If it returns something other than "NONE", run a second retrieval pass and refine the answer using both sets of chunks.

### How to start

Tell me one of:
- *"Scaffold rag_pipeline.py in Python"*
- *"Start with just chunking and retrieval, skip the LLM generator"*
- *"Use opencode CLI for the generator"*
- *"I want to build it about [topic] — help me write the docs first"*
