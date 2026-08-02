# Part 1 — Introduction to LLM Agents

## Concept in 10 lines

- An **LLM agent** is a model plus a harness — the model reasons, the harness acts.
- The **model** is the reasoning core (the brain).
- The **harness** is everything around it: tools, memory, and a decision loop.
- A plain LLM can only answer. An agent can **try, observe, and retry**.
- The vacation planning example: simple question = single call. Complex request = planning + budgeting + looking things up across many sources.
- The model is the brain; the harness is what lets it get the job done.
- Agents are **engineering wrappers** around models — the intelligence still comes from the model.
- The big question is the **autonomy vs. control** tradeoff.

## Vibe-coding challenge

**Build an agent loop demo.** Create a Python script that simulates the agent sense-decide-act-observe loop for a vacation planner — no LLM calls needed:

1. Define a user goal: *"Plan a 3-day trip to Tokyo under $1500."*
2. Implement a simple loop that:
   - **Senses** the current state (remaining budget, days planned, activities booked).
   - **Decides** what to do next (search flights, find hotels, pick activities).
   - **Acts** by calling mock tool functions that return hardcoded results.
   - **Observes** the result and updates state.
3. The loop runs until the plan is complete or budget runs out.
4. Print a step-by-step transcript showing each loop iteration.

> Bonus: add a second goal (*"Plan a 5-day hiking trip in Patagonia under $2000"*) and show the agent adapting its strategy to a different budget and style.

### How to start

Tell me one of:
- *"Scaffold this in Python"*
- *"I want to use a class-based approach"*
- *"Show me the loop structure first, no code"*
- *"Make it data-driven with a list of goals"*
