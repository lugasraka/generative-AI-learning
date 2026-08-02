# Part 5 — Security Frameworks for Agentic AI

> Source: [../securing_agentic_ai_systems/part5_security_frameworks.md](../../securing_agentic_ai_systems/part5_security_frameworks.md)

## Concept in 10 lines

- **OWASP Top 10 for Agentic Applications 2026:** 10 critical risk categories specific to autonomous agents.
- **NIST AI RMF:** Four functions — GOVERN, MAP, MEASURE, MANAGE — for risk management throughout AI lifecycle.
- **MITRE ATLAS:** 15 tactics, 66+ techniques, 14 new agent-specific techniques added October 2025.
- OWASP answers: "What are the biggest threats?" NIST answers: "How should we organize?" ATLAS answers: "How will attackers try?"
- Use all three frameworks together — each serves a different purpose.
- OWASP for threat modeling and security requirements. NIST for governance. ATLAS for specific attack techniques.
- Frameworks give you a foundation but don't solve security problems by themselves.
- You must still design controls specific to your agent's context and test them against real attacks.

## Vibe-coding challenge

**Framework mapping exercise.** Map a sample agent system against all three frameworks:

1. Define 2 agent system descriptions (e.g., customer support agent, financial analysis agent).
2. For each system, map against:
   - **OWASP Top 10:** Which of the 10 risk categories apply? Rate each as High/Medium/Low/None.
   - **NIST AI RMF:** For each of the 4 functions (GOVERN, MAP, MEASURE, MANAGE), what specific actions has the organization taken? Score 0-5.
   - **MITRE ATLAS:** Which of the 14 agent-specific techniques apply? What mitigations exist?
3. Output a structured mapping report for each system.
4. Print a summary showing: system, OWASP risks (count by severity), NIST function scores, ATLAS technique coverage.
5. Identify the biggest gap — which framework reveals the most risk for each system?

> Bonus: create a "framework integration" view showing how controls map across all three frameworks simultaneously.

### How to start

Tell me one of:
- *"Scaffold the system profiles and mapping structure"*
- *"I want to map my own system"*
- *"Show me the OWASP Top 10 categories first"*
- *"Make it a reusable mapping template"*
