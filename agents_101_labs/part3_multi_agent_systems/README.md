# Part 3 — Multi-Agent Systems

## Concept in 10 lines

- A multi-agent system splits a task across **specialized agents** with their own roles.
- Two coordination patterns: **cooperative** (share info, build on each other) and **adversarial** (debate to sharpen answers).
- **Hierarchical:** orchestrator delegates to sub-agents. More control.
- **Flat:** agents chat as peers. More dynamic.
- Multi-agent buys you: parallelization, specialization, tooling independence.
- But it costs you: non-determinism, state complexity, latency, cost, weird failure modes.
- **Don't start with multi-agent.** Start with one agent, let it fail empirically, then scale.
- ~70% of enterprise use cases work fine with a single well-designed agent.
- Multi-agent shines when: big parallel tasks, clear specialization, or creative debate.

## Vibe-coding challenge

**Build a 2-agent "writer + critic" loop.** Create a Python script that:

1. Two agents:
   - **Writer** — takes a topic, generates a short draft (2-3 sentences). Use template-based generation (no LLM).
   - **Critic** — reads the draft, checks for specific quality criteria (clarity, specificity, no filler words), and gives 1-2 concrete suggestions.
2. Loop: Writer drafts -> Critic critiques -> Writer revises -> repeat up to 3 rounds or until Critic says "looks good."
3. Print the full conversation transcript at the end showing each round.
4. Track metrics: number of rounds, words changed per round, final quality score.

> Bonus: add a **Manager** agent (hierarchical pattern) that decides when to stop the loop and which agent speaks next.

### How to start

Tell me one of:
- *"Python with template-based generation"*
- *"I want to use opencode CLI as both agents"*
- *"Add a third agent (Editor) for a 3-agent pipeline"*
- *"Walk me through the coordination patterns first"*
