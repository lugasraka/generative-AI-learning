# Part 6 — Tools for LLM Apps

> Source: [week5_tools_for_LLM_apps.md](../../Applied_LLMs_Mastery_2024/week5_tools_for_LLM_apps.md)

## Concept in 10 lines

- **Tools** are external capabilities an LLM can call — APIs, databases, calculators, search engines. They turn an LLM from "talks" into "acts."
- A tool is defined by: **name**, **description** (when to use it), **input parameters** (with types), and **output structure**.
- The LLM doesn't execute tools directly — it outputs a structured decision (e.g., JSON), a runtime executes the tool, and the result ("observation") is fed back.
- This loop — **reason → call tool → observe → reason** — is the core of agentic systems.
- The **tool ecosystem** for LLM apps includes: data pipelines (Airflow, LangChain), vector databases (Pinecone, Chroma, FAISS), orchestration (LangChain, LlamaIndex), hosting (Replicate, Vercel), monitoring (LangKit, Helicone), and evaluation (Humanloop, PromptLayer).
- **LangChain** provides tool integration, prompt management, memory, and agent orchestration. **LlamaIndex** focuses on data indexing and retrieval (RAG-first).
- Choosing tools depends on your use case: if you need RAG, start with LlamaIndex. If you need agents with tools, start with LangChain. If you need both, they work together.
- The key is to **start simple**: one LLM call + one tool, then add complexity only when needed.

## Vibe-coding challenge

**Build a tool-augmented agent from scratch.** Create a Python script called `tool_ecosystem.py` that:

1. Defines 5 mock tools with JSON schemas:
   - `calculator(expression)` — evaluates a math expression (use Python's `eval` with safety checks or parse manually)
   - `search(query)` — returns a hardcoded result from a small knowledge dict (5+ entries)
   - `summarize(text)` — truncates text to the first N sentences (mock summarization)
   - `lookup_dictionary(word)` — returns a definition from a hardcoded dict
   - `convert_unit(value, from_unit, to_unit)` — converts between a few units (km/miles, kg/lbs, C/F)

2. Registers tools in a registry dict:
   ```python
   TOOLS = {
       "calculator": {"fn": calculator, "schema": {...}},
       "search": {"fn": search, "schema": {...}},
       ...
   }
   ```

3. Implements an **agent loop** (max 5 steps):
   - Sends the user query + tool schemas to `opencode run -m <model>` with a system prompt that says: "You have access to tools. If a tool can help, respond with JSON: {\"action\": \"call_tool\", \"tool\": \"name\", \"args\": {...}}. If no tool is needed, respond with: {\"action\": \"answer\", \"text\": \"...\"}"
   - Parses the LLM's JSON response
   - If `call_tool`: executes the tool, feeds the observation back to the LLM, loops
   - If `answer`: returns the final answer

4. Tests with these queries:
   - "What's 15 * 23 + 7?" → should call `calculator`
   - "What's the capital of France?" → should call `search`
   - "Convert 100 miles to km" → should call `convert_unit`
   - "Define 'algorithm'" → should call `lookup_dictionary`
   - "Summarize: [paste a 3-sentence paragraph]" → should call `summarize`

5. Prints a **full transcript** for each query: each LLM decision, tool call, observation, and final answer.

> Bonus: implement a **multi-tool chain** — a query that requires 2+ tool calls in sequence. Example: "What's 50 miles in km, and what's 10% of that number?" (convert_unit → calculator → answer).

### How to start

Tell me one of:
- *"Scaffold tool_ecosystem.py in Python"*
- *"Start with 2 tools (calculator + search), add more later"*
- *"Use opencode CLI for the LLM"*
- *"Show me the tool schema format first"*
