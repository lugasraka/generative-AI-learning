# Part 3 — Defense Architecture: Three-Pillar Approach

> Source: [../securing_agentic_ai_systems/part3_defense_architecture.md](../../securing_agentic_ai_systems/part3_defense_architecture.md)

## Concept in 10 lines

- **Three pillars:** Guardrails (prevent harmful behavior), Permissions (gate actions), Auditability (traceability).
- No single pillar provides complete protection — they work synergistically.
- **Guardrails:** input validation, output filtering, sandboxing, content filters, tool validation.
- **Permissions:** unique identities, short-lived credentials, RBAC/ABAC/IBAC, least privilege, OBO flow.
- **Auditability:** log everything (prompts, reasoning, tool calls, permissions, safety events), tamper-resistant storage.
- **Governance-containment gap:** 58% have monitoring, only 37% have containment (kill-switch, purpose binding).
- Monitoring without containment is insufficient — you can see what agents do but can't stop them.
- True containment: purpose binding, kill-switch, resource caps, circuit breakers.

## Vibe-coding challenge

**Three-pillar audit checklist.** Create a structured audit for a sample agent system:

1. Define 2 agent system descriptions with different risk profiles.
2. For each system, evaluate all 3 pillars:
   - **Guardrails:** input validation? output filtering? sandboxing? tool validation? (score 1-5 per sub-item)
   - **Permissions:** unique identity? short-lived creds? least privilege? OBO flow? (score 1-5 per sub-item)
   - **Auditability:** comprehensive logging? tamper-resistant? immutable storage? real-time alerts? (score 1-5 per sub-item)
3. Calculate pillar scores and identify the weakest pillar for each system.
4. Output a prioritized remediation list: fix the weakest areas first.
5. Print a formatted audit report.

> Bonus: add a "governance-containment gap" analysis — does the system have monitoring but no containment?

### How to start

Tell me one of:
- *"Scaffold the 2 system profiles and scoring rubric"*
- *"I want to audit my own system"*
- *"Show me the scoring criteria first"*
- *"Make it a reusable audit template"*
