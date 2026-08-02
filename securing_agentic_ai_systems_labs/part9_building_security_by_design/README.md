# Part 9 — Building Security by Design

> Source: [../securing_agentic_ai_systems/part9_building_security_by_design.md](../../securing_agentic_ai_systems/part9_building_security_by_design.md)

## Concept in 10 lines

- **Security requirements before development:** agent security profile, threat modeling, tradeoff documentation.
- **Least privilege by default:** no permissions by default; every capability explicitly granted and justified.
- **Security in the workflow:** review gates, automated CI/CD testing, security test coverage metrics.
- **Secure defaults:** enable all logging, strictest permissions, all guardrails, shortest credential lifespans.
- **Configuration validation:** reject unsafe configs automatically; disabled security requires override + approval.
- **Immutable infrastructure:** bake security into containers/IaC to prevent runtime tampering.
- **Integration with existing security:** use existing IAM, SIEM, incident response — don't build custom.
- **Compliance:** GDPR, HIPAA, SOX, ISO 42001 all apply to agent systems.
- **Culture:** shared responsibility, security as enabler not blocker, continuous learning.

## Vibe-coding challenge

**Security-by-design review.** Conduct a design review of a new agent system before it's built:

1. Define 2 new agent system proposals (one well-designed, one with security gaps).
2. For each proposal, evaluate using the design review checklist:
   - **Agent security profile:** Is it documented? Purpose, resources, actions, prohibited ops, monitoring?
   - **Threat modeling:** Has OWASP/ATLAS been applied? Top threats identified?
   - **Least privilege:** Are permissions minimal? Default deny?
   - **Secure defaults:** Is the default config secure by default?
   - **Existing infrastructure:** Is it using existing IAM/SIEM/IR or building custom?
   - **Compliance:** Are regulatory requirements identified and addressed?
3. Score each dimension (0-5) and calculate an overall readiness score.
4. Output a design review report with findings, risks, and recommended changes.
5. Compare the two proposals and explain why one is more secure.

> Bonus: generate a "go/no-go" recommendation based on the readiness score.

### How to start

Tell me one of:
- *"Scaffold the 2 system proposals and review checklist"*
- *"I want to review my own system design"*
- *"Show me the scoring criteria first"*
- *"Make it a reusable design review template"*
