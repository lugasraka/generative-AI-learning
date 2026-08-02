# Part 9: Building Security by Design

Security works best when built into systems from the beginning rather than added as an afterthought.

---

## Security Requirements Before Development

### Agent Security Profile

Before writing code, document:
- Purpose and goals
- Resources needed (data, APIs, tools)
- Actions it can take (read, write, execute, communicate)
- Prohibited operations
- Authentication and authorization requirements
- Monitoring requirements for compromise detection

### Threat Modeling

Use MITRE ATLAS and OWASP to systematically identify:
- What attacks could target this agent?
- What would attackers gain?
- What are the attack vectors?
- What are the consequences if attacks succeed?

### Security vs. Functionality Tradeoffs

Document deliberate decisions: where reduced functionality was accepted for security, where risk was accepted for necessary functionality, and what compensating controls exist.

## Secure Development Practices

### Principle of Least Privilege by Default

**Default Deny:** No permissions by default. Every capability explicitly granted and justified.

**Progressive Expansion:** As agents prove reliable, carefully expand with same rigor as initial grants.

### Security in the Development Workflow

- **Security Review Gates:** Code changes affecting capabilities, permissions, or controls require security review.
- **Automated Testing in CI/CD:** Static analysis, dependency scanning, security unit tests, integration tests. Failures block deployment.
- **Test Coverage Metrics:** Track percentage of MITRE ATLAS techniques and OWASP risks with test coverage.

## Secure Defaults and Safe Configuration

- **Safe Defaults:** Enable all logging, strictest permissions, all guardrails, all authentication, shortest credential lifespans.
- **Configuration Validation:** Reject unsafe configurations automatically. Disabled security controls require override flags and approval.
- **Immutable Infrastructure:** Bake security into container images and IaC. Prevent runtime tampering.

## Integration with Existing Security

- **IAM:** Use existing systems (Azure Entra ID, AWS IAM, Okta). Agents as first-class citizens.
- **SIEM:** Send agent logs to existing platforms for unified view and correlation.
- **Incident Response:** Flow through existing processes. Train teams on agent-specific concerns.

### Compliance

- **Data Protection (GDPR, CCPA):** PII handling, automated decision-making, data subject requests, retention policies.
- **Industry Regulations:** HIPAA, SOX, GLBA, FedRAMP as applicable.
- **ISO 42001:** AI Management System framework for governance.

## Security Maintenance

### Regular Assessments

- **Quarterly:** Re-run threat modeling, review access controls, audit permissions, check logging, validate testing coverage.
- **Annual:** External penetration testing.

### Vulnerability Management

- Severity assessment and patching priority
- Rapid response for critical vulnerabilities
- Stakeholder communication and regulatory disclosure

### Staying Current

- Monitor OWASP GenAI, NIST AI RMF, MITRE ATLAS updates
- Follow security research and vendor advisories
- Subscribe to AI security threat intelligence
- Engage with the AI security community

## Cultural Aspects

- **Security Ownership:** Shared responsibility — developers implement, specialists review, leadership prioritizes.
- **Security as Enabler:** Enables safe, confident deployment rather than blocking it.
- **Continuous Learning:** Invest in AI-specific security training for teams.

---

**Previous:** [Part 8: What to Watch For](part8_what_to_watch_for.md)
