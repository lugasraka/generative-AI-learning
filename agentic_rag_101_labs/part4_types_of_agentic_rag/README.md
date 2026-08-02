# Part 4 — Types of Agentic RAG

> Source: [../agentic_rag_101/part4_types_of_agentic_rag.md](../../agentic_rag_101/part4_types_of_agentic_rag.md)

## Concept in 10 lines

- **Single-Agent RAG** — one agent manages the entire retrieval and generation process. Simple, efficient, good for straightforward queries.
- **Multi-Agent RAG** — multiple agents collaborate, each handling different retrieval aspects. Good for complex, multi-source tasks.
- **Hierarchical Agentic RAG** — agents organized in a hierarchy. Higher-level agents supervise; lower-level agents execute queries.
- Single-agent = fast and simple. Multi-agent = parallel and specialized. Hierarchical = strategic and controlled.
- Choose single-agent when the task is routine. Choose multi-agent when you need specialization. Choose hierarchical when you need strategic oversight.
- Multi-agent adds coordination overhead — don't use it by default.
- Hierarchical is useful when data sources have different priorities or reliability levels.
- All three architectures share the same core components: agent, retriever, generator.

## Vibe-coding challenge

**Architecture selector.** Build a script that recommends which Agentic RAG architecture to use based on a task description:

1. Define 10 task descriptions (mix of simple lookups, multi-source research, and complex strategic queries).
2. For each task, classify it into the right architecture using keyword signals:
   - Single-agent: "find", "lookup", "what is", "simple"
   - Multi-agent: "compare", "multiple sources", "research", "comprehensive"
   - Hierarchical: "prioritize", "critical", "enterprise", "audit", "compliance"
3. For each classified task, output:
   - Recommended architecture
   - Why (which signals matched)
   - Estimated complexity (low/medium/high)
   - Number of agents needed
4. Print a formatted table with all results.
5. Calculate statistics: how many tasks per architecture, average complexity.

> Bonus: add a "hybrid" recommendation for tasks that could use 2 architectures (e.g., single-agent for simple queries + multi-agent for complex follow-ups).

### How to start

Tell me one of:
- *"Python with a task list and decision tree"*
- *"Make it interactive — I describe tasks"*
- *"Add confidence scores to each classification"*
- *"Show me the decision logic first"*
