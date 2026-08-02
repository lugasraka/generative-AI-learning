# Part 2 — What's Inside an Agent: The Harness

## Concept in 10 lines

- The harness has **4 components**: Agent Core, Memory, Tools, Planning.
- **Agent Core** — the central decision loop. Holds the goal, decides which tool to use, pulls in memory.
- **Memory** — short-term (current task context) and long-term (facts across sessions, retrieved by similarity + recency + importance).
- **Tools** — actions the agent can take: web search, code execution, RAG, APIs. MCP is the emerging standard for wiring tools.
- **Planning** — task decomposition and self-reflection. Reasoning models made this dramatically more capable.
- **Context engineering** — managing what goes into the context window and what stays out.
- The brain/perception/action framework is another lens on the same structure.
- A good harness makes a mediocre model useful; a bad harness makes a great model useless.

## Vibe-coding challenge

**Build a minimal agent harness from scratch.** Create a Python script with all 4 components wired together:

1. **Agent Core:** a `while` loop that holds the current goal, picks the next action, and stops when the goal is met.
2. **Memory:** a `dict` for short-term (current task state) and a `list` for long-term (past task summaries appended after each run).
3. **Tools:** implement at least 2 mock tools — e.g. `get_weather(city)` and `search_flights(origin, dest, date)` — that return hardcoded data.
4. **Planning:** given a complex goal like *"Plan a weekend in Paris under $800"*, decompose it into subtasks (find flights, find hotel, pick activities), then execute each in order.
5. Wire them together: the core reads memory, decomposes via planning, calls tools, updates memory, and repeats until done.
6. Print a summary of the final state (memory contents, tools called, steps taken).

> Bonus: add a `reflect()` step after each tool call — the agent evaluates whether the result is good enough or needs a retry with different parameters.

### How to start

Tell me one of:
- *"Scaffold the 4 components in Python"*
- *"I want a class-based harness"*
- *"Show me the data flow diagram first"*
- *"Start with just memory and tools, add planning later"*
