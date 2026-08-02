# Part 1 — Understanding Agentic AI Security

> Source: [../securing_agentic_ai_systems/part1_understanding_agentic_ai_security.md](../../securing_agentic_ai_systems/part1_understanding_agentic_ai_security.md)

## Concept in 10 lines

- **Agentic AI** = systems that plan, decide, and act — not just generate text.
- Traditional LLM security (input/output filtering) fails because agents **take actions**.
- 94.4% of LLM agents are vulnerable to prompt injection; 100% to inter-agent trust exploits.
- **Four security challenges:** agents act on environment, chain tools dynamically, retain memory, improvise and adapt.
- Prompt injection against a chatbot = bad output. Against an agent = unauthorized actions.
- Memory poisoning persists across sessions — 95%+ success rates in research.
- The attack surface expands from text generation to everything the agent can do.
- Authentication and access control, not just AI safety features, are the actual battleground.

## Vibe-coding challenge

**Threat model sketch for a sample agent system.** Given a system description, identify which security challenges apply and write a structured threat summary:

1. Hardcode 3 sample agent system descriptions (e.g., customer support bot, code review assistant, financial analysis agent).
2. For each system, identify:
   - Which of the 4 security challenges are most relevant and why
   - What tools/APIs the agent has access to
   - What data it can read/write
   - What actions it can take autonomously
3. Output a structured threat summary for each system with:
   - System name and purpose
   - Top 3 risks (ranked by severity)
   - Recommended security controls for each risk
4. Print a comparison table showing which challenges apply to which systems.

> Bonus: add a "blast radius" estimate — if this agent is compromised, what's the worst that could happen?

### How to start

Tell me one of:
- *"Scaffold the 3 system descriptions and threat model structure"*
- *"I want to add my own agent system description"*
- *"Show me the threat model format first"*
- *"Make it a reusable template I can fill in"*
