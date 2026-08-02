# Part 6: Implementation Guide

Practical guidance for implementing the security controls described in previous sections — translating principles into concrete actions.

---

## 6.1 Securing Agent Identity and Access

### Establishing Agent Identities

Every agent needs a unique, verifiable identity. Never use shared accounts or reuse identities across multiple agents.

**Identity Attributes:** Purpose, deployment environment, permission tier, owning team.

### Authentication Methods

- **Short-Lived Certificates:** Hours to days, not months. Issued from trusted PKI. Use HashiCorp Vault PKI, AWS Certificate Manager Private CA, or Azure Key Vault.
- **HSMs:** Tamper-resistant hardware for critical key material. Private keys never exist outside the HSM.
- **Workload Identity Federation:** Just-in-time credentials instead of long-lived secrets. Works across cloud providers.

### Authorization and Access Control

- **RBAC:** Roles mapped to agent purposes with minimum necessary permissions.
- **ABAC:** Multiple attributes (identity, resource, environment, action) inform decisions.
- **OBO Flow:** Delegated permissions where agent operates with intersection of its own capabilities and the user's access rights.

## 6.2 Building Containment Controls

### Purpose Binding

Cryptographically associate agents with their intended function. Use signed configuration files or attestation tokens. Validation layer checks signatures before operations.

### Kill-Switch Capability

- Agent processes that can be remotely signaled to shut down
- Monitoring systems that trigger automatically on behavioral anomalies
- Manual trigger mechanisms for security analysts
- Kill-switch system separate from agent infrastructure

### Resource Usage Caps

- API call limits per minute/hour/day
- Data access volume caps
- Computation budgets (CPU, memory, duration)
- Tool invocation frequency limits
- Output volume caps

Enforcement must be external to the agent — don't rely on self-policing.

### Circuit Breakers

Three states: Closed (normal), Open (suspended pending review), Half-Open (gradual restoration after false positive). Use monitoring systems to track metrics and trigger state changes.

## 6.3 Implementing Tamper-Resistant Logging

### What to Log

- **Inputs:** User queries, retrieved context, system prompts, configuration
- **Reasoning:** Internal thought process, tool selection decisions, alternatives
- **Authorization Checks:** Permission requests, decisions, policies applied
- **Actions:** Tool invocations, parameters, results, errors
- **Security Events:** Guardrail violations, blocked content, anomalies

### Log Format

Use structured formats (JSON, protobuf). Each entry: event type, timestamp, agent identity, session/trace ID, event-specific fields, severity level.

### Tamper-Resistance

- **Cryptographic Signing:** Hash chain where modifying one entry invalidates all subsequent.
- **Immutable Storage:** AWS S3 Object Lock, Azure Immutable Blob Storage, GCP Retention Policies.
- **Real-Time Replication:** Write to multiple destinations concurrently.
- **Separate Security Context:** Agent writes to buffer; separate service writes to permanent storage.

## 6.4 Testing for Vulnerabilities

### Red Team Exercises

Test scenarios: prompt injection, memory poisoning, tool exploitation, goal hijacking, supply chain attacks. Document every success and failure.

### Automated Vulnerability Scanning

Integrate into CI/CD: AI security testing platforms, adversarial prompt libraries, permission control validation, log coverage verification. Failures block deployment.

### Continuous Security Validation

Quarterly minimum for production agents: repeat red team exercises, update adversarial prompt libraries, review access controls, verify logging, test containment controls.

---

**Previous:** [Part 5: Security Frameworks](part5_security_frameworks.md)
**Next:** [Part 7: Addressing Specific Vulnerabilities](part7_addressing_vulnerabilities.md)
