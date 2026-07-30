# Part 10 — AI Agent Lessons and What's Ahead

## Concept in 10 lines

- Two non-negotiables for any real agent: **observability** and **evaluation**.
- **Observability** = logs of every tool call, decision, retry. Step-wise traceability. Build it from day one.
- **Evaluation** = continuous, not one-off. Track: task completion, tool-call success, RAG quality, hallucinations, latency, token cost.
- "Vibe checks" don't scale. Real evals do.
- Trends to watch:
  - **Protocols > prompts** (MCP, A2A)
  - **Hybrid reasoning models** (think only when needed)
  - **Better memory** (task-scoped, persona-aware)
  - **Tool ecosystem maturity** (trusted, plug-and-play)
- The throughline of all 10 parts: **start with the problem, not the architecture.**

## Vibe-coding challenge

**Build a "vibe-check" eval for one of your earlier labs.**

Pick any lab you completed (Part 1-8) and add a small eval to it:

1. Define 3-5 test cases — each with:
   - An input prompt
   - Expected behavior (e.g., "should call tool X", "should mention Y", "should NOT call any tool")
2. Run each test case and capture: did it match expected behavior? how long did it take? how many tokens?
3. Print a simple results table:
   ```
   test 1: PASS  (0.8s, 120 tokens)
   test 2: FAIL  (1.2s, 240 tokens)  -- expected tool X, got tool Y
   ...
   ```
4. (Optional) Save the results to a JSON file so you can compare runs over time.

> Bonus: write 1 short reflection (3-5 lines) in `reflection.md` — what's hard to eval in agents that you've now seen first-hand?

### How to start

Tell me one of:
- *"Add it to my Part 3 lab"*
- *"Add it to my Part 4 lab (RAG)"*
- *"Show me an eval template in Python first"*
- *"Just give me the rubric, no code"*
