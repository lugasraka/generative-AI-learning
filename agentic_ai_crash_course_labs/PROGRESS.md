# Progress

Track your journey through the 10 parts. Check off as you go.

- [x] **Part 1** — What Are AI Agents Anyway? — `thinking_vs_doing.py` (with bonus)
- [x] **Part 2** — The 4 Types of Agentic Systems — `which_agent_type.html`
- [x] **Part 3** — What Are Tools in AI? — `tools_agent.py` (3-tool agent, loop-bug fixed)
- [x] **Part 4** — What Is RAG, and What Does It Mean to Make It Agentic? — `mini_rag.py` (LLM) + `mini_rag_no_llm.py` (World Cup theme, min_overlap=2)
- [x] **Part 5** — What Is MCP and Why Should You Care? — `mcp_assembler.py` (assembler + validator)
- [x] **Part 6** — Planning in Agents + Reasoning Models — `planner.py` (rule-based + LLM side-by-side)
- [x] **Part 7** — Memory in Agents — `memory_agent.py` (short-term + 3-flavor long-term + forget)
- [x] **Part 8** — Multi-Agent Systems — `multi_agent.py` (writer + critic flat + hierarchical manager) + `eval_part8.py`
- [x] **Part 9** — Real-World Agentic Systems — `CHECKLIST.md` (reverse-engineer template)
- [x] **Part 10** — AI Agent Lessons and What's Ahead — `eval_part3.py` (4/5 pass) + `reflection.md` + `eval_results.json`

## Personal notes

### Key takeaways
- **Stop-after-answer prompting is essential** — the LLM doesn't know when to stop on its own; one paragraph in the system prompt fixed Part 3's loop.
- **Keyword RAG is fast but noisy** — `min_overlap=2` cleanly rejects 1-token false matches; real fix is embeddings.
- **Rule-based vs LLM planners is the central Part 6 tradeoff** — fast/free/dumb vs slow/cost/smart. Start simple.
- **Long-term memory survives across sessions, short-term doesn't** — procedural prefs flow back into new sessions via recall.
- **Evals catch infra issues, not just model issues** — Part 10's `weather_london` fail was a Bun crash, not a logic bug.

### Open items / things to revisit
- Part 8 multi-agent harness (timeout aborted in CLI; re-test in TUI if needed)
- Part 4 agentic-RAG bonus (Bun segfault on long reflection prompt — could shorten prompt)
- Part 9 — actually run a real system and fill in CHECKLIST.md
- Add a Part 8 eval case to the Part 10 harness
