# Part 6 — Build Your Own Agent (Capstone)

## Concept in 10 lines

- This part ties together everything from Parts 1-5 into one working agent.
- You need: agent core (loop), memory (short + long), tools (2+), planning (decomposition), and evaluation.
- The capstone agent should solve a real task end-to-end.
- Start simple: pick a narrow domain (trip planner, task tracker, recipe finder).
- Wire the harness: goal -> decompose -> execute tools -> update memory -> reflect -> repeat.
- Add evaluation: run test cases and score utility, reliability, safety.
- The goal is not perfection — it's demonstrating you understand how all the pieces fit.
- A 50-line agent that runs is worth more than a 500-line agent that doesn't.
- Ship it, then iterate. That's the agent loop applied to building agents.

## Vibe-coding challenge

**Build a complete mini-agent from scratch.** Combine all prior concepts into one script:

1. **Agent Core:** a `while` loop that holds the goal, picks the next action, and stops when done or budget is exhausted.
2. **Memory:** short-term dict for current task state + long-term list that persists across runs (append to a JSON file).
3. **Tools:** at least 2 mock tools relevant to your chosen domain (e.g., search, calculate, fetch, classify).
4. **Planning:** decompose the goal into subtasks, execute them in order, track progress.
5. **Reflection:** after each tool call, evaluate whether the result is good enough or needs a retry.
6. **Evaluation:** run 3+ test cases through your agent and print a pass/fail summary.
7. Print a final summary: goal, steps taken, tools used, cost/time estimate, and whether the goal was achieved.

> Bonus: make the agent handle **interruption and recovery** — save state to disk mid-run, and resume from where it left off.

### How to start

Tell me one of:
- *"I'll pick a domain, scaffold the harness for me"*
- *"Use a trip planner domain"*
- *"Use a task tracker domain"*
- *"Show me the architecture before we code"*
