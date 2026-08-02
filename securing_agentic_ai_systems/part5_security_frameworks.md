# Part 5: Security Frameworks for Agentic AI

Three frameworks have emerged as particularly relevant for agent security: OWASP Top 10 for Agentic Applications 2026, NIST AI Risk Management Framework, and MITRE ATLAS.

---

## 5.1 OWASP Top 10 for Agentic Applications 2026

Released December 9, 2025, this is the first comprehensive risk framework specifically for autonomous agents, developed with 100+ industry experts.

### Core Risk Categories

1. **Goal Hijacking** — Manipulating agent objectives over time.
2. **Identity Abuse** — Exploiting agent identity and authentication systems.
3. **Human Trust Manipulation** — Exploiting human trust in agent recommendations.
4. **Rogue Autonomous Behaviors** — Unexpected, unauthorized, or harmful autonomous actions.
5. **Tool Misuse and Privilege Escalation** — Unauthorized tool invocation or chaining.
6. **Memory Poisoning** — Compromising persistent memory through injection.
7. **Supply Chain Vulnerabilities** — Risks from compromised frameworks, models, plugins.
8. **Multi-Agent Coordination Attacks** — Exploiting communication between agents.
9. **Context Manipulation** — Poisoning RAG systems, knowledge bases, data sources.
10. **Insufficient Monitoring and Response** — Lack of visibility or response capability.

### How to Apply

- **Threat Modeling:** Use categories as a checklist during design.
- **Security Requirements:** Map each risk to specific requirements.
- **Testing and Validation:** Verify resilience against each category.
- **Stakeholder Communication:** Common language for discussing risks.

## 5.2 NIST AI Risk Management Framework

Released January 2023, provides voluntary guidance for trustworthiness in AI systems. Microsoft has demonstrated how to map it to agent security.

### Four Core Functions

**GOVERN:** Cultivates a culture of risk management. For agents: who has authority to deploy, approval processes, monitoring, misbehavior handling, alignment with values.

**MAP:** Establishes context. For agents: what systems/data they access, what actions they can take, who is affected, what harms could result, what regulations apply.

**MEASURE:** Analyzes and monitors risk. For agents: vulnerability assessments, behavioral testing, continuous monitoring, goal alignment metrics, security control performance.

**MANAGE:** Ongoing risk management. For agents: implementing three-pillar defense, incident response, updating controls, retiring risky agents.

## 5.3 MITRE ATLAS for AI Agents

A knowledge base of adversary tactics, techniques, and case studies for ML systems. As of October 2025: 15 tactics, 66 techniques, 46 sub-techniques, 26 mitigations, and 33 case studies.

### October 2025 Agentic AI Update

14 new agent-specific techniques added:
- **AI Agent Context Poisoning** — Manipulating agent context to persistently influence behavior.
- **Memory Manipulation** — Altering long-term memory across sessions.
- **Modify AI Agent Configuration** — Changing config files for persistent malicious behavior.
- **Exfiltration via Tool Invocation** — Using legitimate write tools to leak data.
- **RAG Credential Harvesting** — Collecting credentials from ingested documents.
- **Agent Configuration Discovery** — Enumerating agent configs and permissions.
- **Tool Definitions Discovery** — Enumerating available tools.

### Using ATLAS for Threat Modeling

1. Identify relevant tactics from the 15 available.
2. Map applicable techniques to your system.
3. Assess defenses against each technique.
4. Document coverage gaps.
5. Prioritize based on risk (likelihood, impact, detectability).

## Combining the Frameworks

- **OWASP Top 10** answers: "What are the biggest threats?"
- **NIST AI RMF** answers: "How should we organize risk management?"
- **MITRE ATLAS** answers: "Exactly how will attackers try to compromise our agents?"

In practice: use NIST to establish governance, OWASP to identify risks, ATLAS to understand attack techniques and design defenses.

---

**Previous:** [Part 4: Detection, Prevention, and Mitigation](part4_detection_prevention_mitigation.md)
**Next:** [Part 6: Implementation Guide](part6_implementation_guide.md)
