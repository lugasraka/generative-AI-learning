# Part 7 — Memory in Agents

## Concept in 10 lines

- LLMs are **stateless** — they have no built-in memory.
- **Short-term memory**: the current session. Conversation, tools used, docs retrieved.
- **Long-term memory**: across sessions. User prefs, past actions, important context.
- Long-term flavors (from cognitive science):
  - **Semantic** — facts ("user prefers Excel")
  - **Episodic** — past actions ("I already sent that email yesterday")
  - **Procedural** — preferences ("avoid passive voice")
- Memory looks a lot like RAG, but the goal is **continuity** over time, not answering questions.
- More data ≠ better. The hard part is *what* to store and *what* to retrieve.
- **Problem first:** not every agent needs memory. Decide *why* before you architect.

## Vibe-coding challenge

**Build a tiny agent with both memory types.**

1. Two storage backends (in-memory dicts are fine):
   - `short_term: list[{role, content}]` — cleared each session
   - `long_term: dict[user_id, {semantic, episodic, procedural}]` — persists
2. Functions:
   - `remember(user_id, memory_type, content)` — writes to long-term
   - `recall(user_id, query)` — pulls from both, returns merged context
   - `add_turn(user_id, role, content)` — appends to short-term
   - `get_context(user_id, query)` — returns short-term + recalled long-term
3. Simulate 2 "sessions" for a fake user:
   - Session 1: user says *"I prefer bullet points"* → stored as procedural
   - Session 2 (new session, short-term empty): user asks *"Summarize this article"* → agent should recall the preference and use bullet points
4. Print the context the agent sees at each step.

> Bonus: add a `forget(user_id, memory_type, key)` to demonstrate that not all memory should be forever.

### How to start

Tell me one of:
- *"Python with in-memory dicts"*
- *"Python with a JSON file as the long-term store"*
- *"TypeScript"*
- *"Walk me through the design first, no code"*
