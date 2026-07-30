# Part 8 — Multi-Agent Systems

## Concept in 10 lines

- A multi-agent system splits a task across **specialized agents** with their own tools and memory.
- Two coordination patterns:
  - **Hierarchical** — an orchestrator delegates to sub-agents. More control. Good for enterprise workflows.
  - **Flat** — agents chat as peers. More dynamic. Good for debate, brainstorming, ranking.
- Multi-agent buys you: **parallelization**, **specialization**, **tooling independence**.
- But it costs you: more **non-determinism**, **state complexity**, **latency**, **cost**, and weird failure modes (agents agreeing when they shouldn't).
- The author's rule: **don't start with multi-agent.** Start with one, let it fail empirically, then scale.
- ~70% of enterprise use cases work fine with a single well-designed agent.
- Multi-agent shines when: big parallel tasks, clear specialization, or creative debate.

## Vibe-coding challenge

**Build a 2-agent "writer + critic" loop (flat pattern).**

1. Two agents:
   - **Writer** — takes a topic, generates a short draft (a paragraph).
   - **Critic** — reads the draft, gives 1-2 specific suggestions.
2. Loop:
   - Writer drafts → Critic critiques → Writer revises → repeat up to 3 rounds or until Critic says "looks good."
3. Print the full conversation transcript at the end.
4. Use the opencode CLI as both agents, or mock with templates.

> Bonus: try the hierarchical version — add a **Manager** that decides which agent speaks next and when the loop ends.

### How to start

Tell me one of:
- *"Python with opencode CLI as both agents"*
- *"Python with mocked LLM calls"*
- *"TypeScript"*
- *"Just walk me through the patterns, no code"*
