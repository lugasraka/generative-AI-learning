# Part 7: Addressing Specific Vulnerabilities

Targeted defenses against the five major attack vectors identified in Part 2.

---

## 7.1 Preventing Prompt Injection

### Input Validation and Segregation

- **Separate System Instructions from User Input:** Never concatenate directly. Use platform-level message roles when available.
- **Mark External Content:** Wrap untrusted content in clear markers. Instruct agent to treat as data, not instructions.
- **Input Sanitization:** Scan for injection patterns — instruction overrides, role-playing, prompt extraction, encoding tricks, nested instructions.

### Instruction Hierarchy

- Include explicit priority statements: system instructions override conflicting content.
- Periodically re-inject system prompts for long-running agents.

### Human-in-the-Loop

Require approval for: deleting/modifying data, external communications, fund transfers, access grants, code execution.

### Signed Instructions

Cryptographically sign valid instruction sets. Agent only accepts verifiable instructions from authorized sources.

## 7.2 Protecting Agent Memory

### Memory Access Controls

- **Write Protection:** Restricted to authenticated, verified operations. Unauthorized attempts trigger alerts.
- **Read Validation:** Check provenance, creation time, source legitimacy, modification status, relevance.

### Memory Sanitization

Scan retrieved memories for embedded instructions, suspicious patterns, structural anomalies, out-of-scope references.

### Memory Isolation

- **Per-Agent:** Each instance has its own store.
- **Per-User:** Separate contexts per user.
- **Per-Task:** Segregate memories by task type.

### Periodic Memory Validation

- Anomaly detection for unusual patterns
- Automated validation of structure, provenance, timestamps
- Manual review sampling for high-security agents

## 7.3 Securing the Supply Chain

### Dependency Management

- **Pin versions** with lock files. Test updates in non-production first.
- **Vulnerability scanning** against CVE databases (Dependabot, Snyk, Grype).
- **SBOM** — inventory of all components with versions and sources.

### Package Integrity

- **Checksum verification** before installation.
- **Signature verification** for packages from maintainers.
- **Private package mirrors** for critical dependencies.

### Model Provenance

- **Model signing** verification from claimed providers.
- **Model scanning** for backdoors or anomalies.
- **Trusted sources** with established security practices.

### Configuration Validation

- **Configuration as Code** in version control with PR reviews.
- **Configuration signing** with cryptographic verification.
- **Schema validation** — reject excessive permissions, unauthorized tools, missing logging.

## 7.4 Controlling Tool Access

### Principle of Least Privilege

- **Tool Allowlisting:** Explicit lists of invocable tools per agent.
- **Parameter Validation:** File paths, database queries, email recipients, API scopes.

### Runtime Tool Validation

- Authorization checks before every invocation
- Parameter range validation
- Resource quota verification
- Intent alignment checks

### Tool Chaining Prevention

- **Sequence Analysis:** Monitor for exfiltration, privilege escalation, persistence patterns.
- **Contextual Authorization:** Permissions change based on previous actions.

### Sandboxed Execution

- **Containerization:** Restricted network, file system, resources.
- **API Gateways:** Mediate all access with security policies, rate limiting, monitoring.

## 7.5 Preventing Goal Hijacking

### Goal Specification

- Formal, machine-readable goal definitions with success metrics and constraints.
- Continuous alignment checks against stated objectives.

### Input Trust Levels

- System config: highest trust
- Direct user: high trust
- Internal docs: medium trust
- External docs: low trust
- Web content: lowest trust

### Behavioral Drift Detection

- Baselines for tool call patterns, decision patterns, resource usage, output characteristics.
- Statistical tests and ML models for anomaly detection.
- Multi-agent consensus for critical decisions — compromised agents produce different recommendations.

---

**Previous:** [Part 6: Implementation Guide](part6_implementation_guide.md)
**Next:** [Part 8: What to Watch For](part8_what_to_watch_for.md)
