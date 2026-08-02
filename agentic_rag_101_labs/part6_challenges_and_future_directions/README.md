# Part 6 — Agentic RAG Challenges and Future Directions

> Source: [../agentic_rag_101/part6_challenges_and_future_directions.md](../../agentic_rag_101/part6_challenges_and_future_directions.md)

## Concept in 10 lines

- **Coordination complexity** — more agents = more potential for conflicts and bottlenecks.
- **Scalability concerns** — managing many agents and data sources is resource-intensive; real-time performance degrades.
- **Data quality** — garbage in, garbage out. Unreliable sources → misinformation.
- **Transparency** — "black box" agent decisions make debugging and trust hard.
- Future: **better orchestration** — agents that collaborate more efficiently with smarter workflows.
- Future: **hybrid human-agent** — agents handle routine, humans handle exceptions and high-stakes decisions.
- Future: **learning agents** — adapt from past interactions instead of following static rules.
- Future: **ethical agents** — fairness, bias mitigation, responsible AI in sensitive domains.
- The challenges are real but solvable — the field is moving fast.

## Vibe-coding challenge

**Agentic RAG risk audit tool.** Build a script that takes a description of an Agentic RAG system and outputs a risk assessment:

1. Define a system description input (hardcode 3 example systems: a customer support bot, a medical research assistant, a financial analysis tool).
2. For each system, evaluate the 4 challenges:
   - **Coordination** — how many agents? How complex is the routing? (score 1-5)
   - **Scalability** — how many data sources? How many concurrent users? (score 1-5)
   - **Data quality** — are sources reliable? Is there a verification step? (score 1-5)
   - **Transparency** — is there logging? Can you trace decisions? (score 1-5)
3. For each system, recommend which future directions are most relevant:
   - Learning agents (if the system handles repetitive queries)
   - Human-in-the-loop (if high-stakes decisions)
   - Ethical agents (if sensitive data)
   - Better orchestration (if multi-agent)
4. Print a risk report for each system with scores, recommendations, and an overall risk level (low/medium/high).
5. Compare the three systems and explain which is riskiest and why.

> Bonus: generate a markdown risk report file that could be shared with a team.

### How to start

Tell me one of:
- *"Scaffold the 3 system profiles and scoring logic"*
- *"Make it interactive — I describe my system"*
- *"Show me the scoring rubric first"*
- *"I want the markdown report output"*
