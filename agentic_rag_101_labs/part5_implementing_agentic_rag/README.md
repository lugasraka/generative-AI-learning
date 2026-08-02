# Part 5 — Implementing Agentic RAG

> Source: [../agentic_rag_101/part5_implementing_agentic_rag.md](../../agentic_rag_101/part5_implementing_agentic_rag.md)

## Concept in 10 lines

- Implementation options: LangChain, LlamaIndex, Pinecone, LangGraph, Vertex AI.
- LangChain provides the building blocks; Pinecone provides the vector store; LangGraph adds orchestration.
- LlamaIndex has built-in Agentic RAG support via its agent and retriever abstractions.
- LangGraph is best for complex, multi-step workflows with conditional routing.
- Start simple: basic RAG first, then add agentic behavior.
- The core pipeline: chunk documents → embed → store in vector DB → retrieve top-k → generate.
- Agentic twist: the agent decides *when* to retrieve, *which* index to query, and *whether* to re-retrieve.
- No single framework is "best" — pick based on your team's familiarity and the complexity you need.
- These resources are starting points — the field moves fast.

## Vibe-coding challenge

**Mini RAG pipeline from scratch.** Build a minimal RAG system in pure Python (no external DB or embeddings):

1. Hardcode 5-10 short documents (3-5 sentences each) about a topic you care about.
2. Implement a naive **chunker** — split each document into sentences or fixed-size windows.
3. Implement a **retriever** using keyword overlap (set intersection, no embeddings).
4. Implement a **generator** — given a query + retrieved chunks, assemble a response using a template (or opencode CLI).
5. Test with 3 questions where the answer exists in the docs and 1 where it doesn't.
6. Print: query, retrieved chunks, generated answer, whether it was correct.

> Bonus: extend with a second retrieval pass — after generating the first answer, the agent evaluates whether it's confident enough or needs to re-retrieve with different keywords. That's your first taste of agentic RAG.

### How to start

Tell me one of:
- *"Scaffold the chunker and retriever"*
- *"Use a specific topic for the document store"*
- *"Show me the pipeline diagram first"*
- *"I want to understand chunking strategies first"*
