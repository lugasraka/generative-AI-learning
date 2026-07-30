# Part 6 — Planning in Agents + Reasoning Models

## Concept in 10 lines

- For multi-step tasks, the agent must **plan**: interpret, sequence, choose tools, handle exceptions, know when it's done.
- Plain LLMs are next-token predictors — they don't naturally plan.
- **Chain-of-thought prompting** ("think step by step") helps with puzzles, but falls apart for real agents.
- **Reasoning models (LRMs)** are trained to plan *by design*. Examples: OpenAI o-series, DeepSeek-R1, Claude 3.7 reasoning mode, Gemini thinking.
- LLM: input → output. LRM: input → plan + output.
- Tradeoffs: longer outputs, more latency/cost, can overthink simple tasks, can hallucinate plans.
- Rule of thumb: start with a mid-size base model, only switch to a reasoning model if you see planning failures.

## Vibe-coding challenge

**Build a "planner" that breaks a task into steps.**

1. Take a complex prompt like: *"Find all our Q1 healthcare clients who are overdue on payments, and draft personalized emails with new payment links."*
2. Build a planner (LLM or rule-based) that returns a structured plan:
   ```json
   [
     {"step": 1, "action": "query_db", "details": "filter: Q1, sector=healthcare, status=overdue"},
     {"step": 2, "action": "for each client", "details": "..."},
     {"step": 3, "action": "generate_payment_link", "details": "..."},
     {"step": 4, "action": "draft_email", "details": "personalize with client name + link"},
     {"step": 5, "action": "send_email", "details": "via send_email tool"}
   ]
   ```
3. Print the plan in a readable way. Don't execute it — just plan.
4. Try a second, simpler prompt ("What's 13 × 47?") and show the planner correctly identifies it as a 1-step task.

> Bonus: have the planner also flag which steps need a human-in-the-loop checkpoint.

### How to start

Tell me one of:
- *"Scaffold a rule-based planner in Python"*
- *"Use the opencode CLI as the planner"*
- *"Show me what a reasoning model adds over a plain LLM"*
- *"Just walk me through the planning concept"*
