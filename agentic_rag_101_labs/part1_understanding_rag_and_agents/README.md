# Part 1 — Understanding RAG and Agents

> Source: [../agentic_rag_101/part1_understanding_rag_and_agents.md](../../agentic_rag_101/part1_understanding_rag_and_agents.md)

## Concept in 10 lines

- **RAG** = Retrieval Augmented Generation. Gives LLMs access to real-time data from external sources (databases, web searches, documents).
- LLMs alone rely only on training data — RAG fixes this by pulling fresh, relevant information before generating an answer.
- **Agents** = systems that can make decisions and act autonomously. They assess, choose, and execute.
- A plain LLM answers. An agent **does**.
- **Agentic RAG** = RAG + agents working together. The agent decides *how* and *when* to retrieve, not just *what* to retrieve.
- RAG is especially valuable where up-to-date info matters: customer support, finance, healthcare.
- The combination makes systems more flexible and able to handle complex, multi-step queries.
- Start simple: RAG is a tool — agent is the brain that uses it.

## Vibe-coding challenge

**RAG vs Agent vs Agentic RAG — side-by-side comparison.** Build a Python script that implements three systems and runs the same question through each:

1. **Plain LLM** — a function that can only answer from hardcoded knowledge. When asked something outside its knowledge, it guesses or says "I don't know."
2. **Basic RAG** — a function that retrieves from a hardcoded document store (5-10 short texts) before answering. It retrieves the most relevant chunk and includes it in the response.
3. **Agentic RAG** — a function where an agent first analyzes the query, decides which of 2-3 data sources to query, retrieves from each, then assembles a response.
4. Run all three on the same 3 questions (one easy, one requiring retrieval, one needing multiple sources).
5. Print a comparison table showing: question, system, answer, whether it used retrieval, whether it was correct.

> Bonus: add a 4th system — "Agentic RAG with follow-up" — where the agent can ask a clarifying question if the initial query is ambiguous.

### How to start

Tell me one of:
- *"Scaffold all 3 systems in Python"*
- *"Start with just RAG, add the agent later"*
- *"Show me the document store structure first"*
- *"Use opencode CLI as the LLM backend"*
