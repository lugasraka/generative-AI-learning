# Part 4 — Agents in the Real World

## Concept in 10 lines

- The 2023 wave of task-loop demos (BabyAGI) proved the idea. What shipped in 2025-2026 is built on strong harnesses.
- **Coding agents:** Claude Code, Codex, Cursor — plan, edit files, run code, verify.
- **Computer-use and browser agents:** operate screens or browsers across apps.
- **Deep research agents:** plan a question, search the web, synthesize a cited report.
- **Enterprise workflow agents:** customer support, operations, analysis in production with observability.
- The common pattern: capable model + well-designed harness + loop that survives long tasks.
- Each category has different tool requirements, memory needs, and failure modes.
- Coding agents need file system access and code execution. Research agents need web search and synthesis.
- Enterprise agents need guardrails, logging, and human-in-the-loop checkpoints.

## Vibe-coding challenge

**Build an agent archetype classifier.** Create a Python script that:

1. Define 10 task descriptions (a mix of coding, research, browser, and enterprise tasks).
2. For each task, classify it into the right agent archetype (coding, computer-use, deep research, enterprise workflow).
3. For each classified task, output the required harness components:
   - Which tools are needed (file access, web search, browser control, API calls, etc.)
   - What memory type is appropriate (short-term only, session memory, persistent)
   - What planning style fits (single-pass, iterative, multi-step with reflection)
   - What safety constraints apply (sandbox, read-only, human approval)
4. Print a formatted table showing task -> archetype -> harness requirements.
5. Calculate statistics: how many tasks fall into each archetype, most common tool needs.

> Bonus: add a "hybrid" archetype for tasks that span multiple categories, and output a recommended multi-agent architecture for those.

### How to start

Tell me one of:
- *"Python with a dictionary of tasks"*
- *"Make it interactive — I input tasks"*
- *"Add a confidence score to each classification"*
- *"Show me the taxonomy first, then code"*
