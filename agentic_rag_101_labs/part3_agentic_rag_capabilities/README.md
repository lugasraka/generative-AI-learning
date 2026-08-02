# Part 3 — Agentic RAG Capabilities

> Source: [../agentic_rag_101/part3_agentic_rag_capabilities.md](../../agentic_rag_101/part3_agentic_rag_capabilities.md)

## Concept in 10 lines

- **Dynamic Data Retrieval** — fetch real-time info based on queries, not a fixed index.
- **Autonomous Decision-Making** — agents decide what to retrieve, when, and how, without human intervention.
- **Context-Aware Responses** — agents assess query context and adjust retrieval accordingly.
- **Scalability** — handle more complex queries across domains by leveraging multiple data sources.
- **Reduced Hallucination Risk** — real-time data + intelligent integration = fewer fabricated answers.
- **Customizable Workflows** — fine-tune retrieval strategies per task or domain.
- **Multi-Step Reasoning** — break queries into sub-queries, retrieve progressively, build a layered answer.
- Not all capabilities are needed for every task — pick what fits your use case.
- The power is in the combination: dynamic + autonomous + context-aware = smart retrieval.

## Vibe-coding challenge

**Capability demo harness.** Build a script that demonstrates at least 3 of the 7 capabilities using a simulated document store:

1. **Dynamic Data Retrieval** — given a query, the agent selects which of 3 different data sources to query (e.g., news, finance, sports) based on the query topic. Print which source was chosen and why.
2. **Context-Aware Responses** — given two similar queries with different contexts (e.g., "What's the weather?" vs "What's the weather for my flight?"), the agent adjusts its retrieval to include different data. Show the difference.
3. **Multi-Step Reasoning** — given a complex query like "Compare the stock performance of Apple and Google over the last month", the agent breaks it into sub-queries, retrieves data for each, then synthesizes a comparison.
4. For each capability, print: what the agent did, why it chose that approach, and what the output looked like.
5. Run all demos and print a summary showing which capabilities were demonstrated.

> Bonus: add **Reduced Hallucination Risk** — give the agent a query about something NOT in the data store and verify it says "I don't have data on that" instead of making something up.

### How to start

Tell me one of:
- *"Scaffold 3 capabilities with mock data"*
- *"Start with Dynamic Retrieval only"*
- *"I want the multi-step reasoning one"*
- *"Show me the data sources first"*
