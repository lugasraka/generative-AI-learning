# Part 2 — What is Agentic RAG?

> Source: [../agentic_rag_101/part2_what_is_agentic_rag.md](../../agentic_rag_101/part2_what_is_agentic_rag.md)

## Concept in 10 lines

- When RAG and agents combine, the **agent takes charge** of the entire retrieval-and-generation pipeline.
- The agent decides: *where* to get data, *what* is most important, *how* to integrate it.
- The 7-step flow: Query → Agent analyzes → Decides retrieval strategy → Data retrieval → LLM generates → Response delivery → Follow-up actions.
- The agent autonomously decides which sources to query — not a fixed pipeline.
- The retrieval system pulls real-time data specific to the query.
- The LLM generates a context-aware answer by combining pre-trained knowledge + fresh data.
- Agentic RAG can also interact with tools and services, not just knowledge bases.
- The customer support example: "Why is my internet slow?" → agent fetches service history + network reports + knowledge base → synthesized answer.

## Vibe-coding challenge

**Customer support agent simulation.** Build a script that simulates the 7-step Agentic RAG flow from the course example:

1. Hardcode 3 data sources:
   - `service_history` — a dict of past complaints by neighborhood
   - `network_reports` — a dict of congestion data by time-of-day
   - `knowledge_base` — a list of articles about common issues
2. The agent receives a query (start with "Why is my internet slow in the evenings?").
3. Implement the agent logic:
   - Step 2: Analyze the query and identify which sources are relevant
   - Step 3: Decide which sources to query (based on keywords/topic)
   - Step 4: Fetch data from each selected source
   - Step 5: Assemble a response combining the retrieved data
4. Print each step with what the agent decided and what it retrieved.
5. Add 2 more test queries and show the agent adapting its retrieval strategy.

> Bonus: add a "confidence score" — if the agent can't find enough relevant data, it says "I'm not sure, let me check more sources" instead of hallucinating.

### How to start

Tell me one of:
- *"Scaffold the 3 data sources and agent loop"*
- *"I want to simulate the full 7-step flow"*
- *"Show me the data structure first"*
- *"Make it interactive — I type queries"*
