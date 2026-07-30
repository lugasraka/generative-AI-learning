# Part 5 — What Is MCP and Why Should You Care?

## Concept in 10 lines

- **MCP = Model Context Protocol.** A standardized way to package *everything* an LLM needs into one structured payload.
- It's not a product, library, or tool — it's a **protocol**, like HTTP or SMTP.
- What gets packaged: the task, available tools, retrieved documents, memory, prior messages, instructions.
- Why it matters: as agents get more complex (tools + RAG + memory + planning), coordinating all that gets messy. MCP standardizes it.
- Released by Anthropic in late 2024; exploded in 2025; OpenAI and others now support it.
- Common misunderstanding: MCP doesn't make the model smarter — it gives it **better, more structured context**.
- It works best for **enterprise-grade, multi-tool, multi-context** systems — overkill for toy demos.

## Vibe-coding challenge

**Build a tiny "MCP-style" request assembler.**

1. Define a `Context` data structure (in any language) with fields:
   - `task: string`
   - `tools: list[{name, description, params}]`
   - `retrieved_docs: list[string]`
   - `memory: list[{role, content}]`
   - `instructions: string`
2. Build a function `assemble_mcp_request(context)` that serializes it into a single JSON object — pretty-printed.
3. Build a function `simulate_llm_call(request)` that just prints the assembled JSON and returns a hardcoded response (no real LLM needed).
4. Test by calling it with:
   - 2 tools
   - 1 retrieved doc
   - 3 memory turns
   - a task: *"Summarize the doc and email it to john@example.com using send_email."*

> Bonus: add a second helper `validate_request(request)` that checks for missing fields and returns a list of warnings — like "no tools registered" or "memory empty."

### How to start

Tell me one of:
- *"Python"*
- *"TypeScript"*
- *"Just a JSON schema, no code"*
- *"Walk me through the protocol flow first"*
