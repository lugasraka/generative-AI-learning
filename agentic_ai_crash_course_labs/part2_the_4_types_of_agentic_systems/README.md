# Part 2 — The 4 Types of Agentic Systems

## Concept in 10 lines

- Autonomy vs. control is the key axis. The right level depends on the problem.
- **Type 1 — Rule-based:** if/then logic, no LLM. Fast, predictable, brittle. Use when the problem is fully understood.
- **Type 2 — Workflow agents:** LLM *suggests*, human *acts*. Low autonomy, high control. Great first step into GenAI.
- **Type 3 — Semi-autonomous agents:** LLM plans and acts across multiple steps with some guardrails. The "real" agentic sweet spot for enterprise.
- **Type 4 — Autonomous agents:** broad goal in, agent figures it all out. High scale, high risk, infra-heavy.
- These are not mutually exclusive — a single system can mix them.
- **Start with the problem**, not the architecture.

## Vibe-coding challenge

**Build a "which agent type?" decision tool.** Make a small interactive CLI (or web form) that:

1. Asks the user 3-4 questions about their problem:
   - Is it repetitive and structured?
   - Does it need natural language understanding?
   - Is it multi-step?
   - Does it need a human in the loop?
2. Based on the answers, recommends one of the 4 types and explains *why*.
3. Optionally outputs a 1-line "starter architecture" (e.g., "Use a workflow agent wrapping an LLM + a retrieval step").

> Bonus: hardcode 2-3 example use cases and show the recommended agent type for each.

### How to start

Tell me one of:
- *"Make it a Python CLI"*
- *"Make it a single HTML+JS file"*
- *"Skip code, just walk me through the decision tree"*
- *"Show me what each type looks like with a tiny code snippet"*
