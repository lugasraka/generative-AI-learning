# Part 4: Detection, Prevention, and Mitigation Strategies

Security controls fall into three categories based on when they operate: detection identifies attacks, prevention stops them, and mitigation limits damage. Effective security requires all three working together.

---

## 4.1 Detection Mechanisms

Detection doesn't stop attacks directly; it surfaces signals that something is wrong so you can investigate and respond.

### What to Monitor

**Input Monitoring:**
- Injection patterns, suspicious instructions, malicious content
- Source and provenance of input data
- Unusual request patterns and format anomalies

**Behavioral Monitoring:**
- Tool invocation frequency and patterns
- Resource usage (API calls, computation, data access)
- Unexpected action sequences and workflow deviations

**Output Monitoring:**
- Sensitive data exposure in generated content
- Hallucinations or fabricated information
- Patterns consistent with data exfiltration

### Detection Accuracy Limitations

Studies found detection systems performed best against explicit attacks (84.9% accuracy) but decreased for indirect (77.1%) and stealth (74.6%) styles. Detection alone is insufficient.

## 4.2 Prevention Controls

### Input Validation and Sanitization
- **Content Filtering:** Scan and block/sanitize inputs before they reach the agent.
- **Format Enforcement:** Require inputs to match specific structures.
- **Source Verification:** Validate authorized sources with proper authentication.
- **Segregate External Content:** Clearly mark untrusted sources.

### Privilege Control
- **Minimum Necessary Permissions:** Restrict to exactly what's needed.
- **Code-Based Function Handling:** Mediate function calls through validation code.
- **Human-in-the-Loop:** Require approval for high-risk operations.
- **Tool Authorization Checks:** Verify permissions before every tool invocation.

### Intent-Based Defense
Validate that requested actions align with the agent's stated purpose. If a customer support agent suddenly tries to query financial databases, those actions don't match its verified intent.

### Adversarial Testing
- **Red Team Exercises:** Actively attempt to compromise agents using known techniques.
- **Automated Security Testing:** Integrate into CI/CD to catch vulnerabilities before production.

## 4.3 Mitigation Approaches

### Limiting Blast Radius
- **Sandboxed Execution:** Isolated environments limiting access to sensitive resources.
- **Network Segmentation:** Separate network segments with restricted connectivity.
- **Data Access Boundaries:** Limit what data agents can access.
- **Rate Limiting and Quotas:** Cap API calls, data access, computation, tool invocations.

### Context Filters and Sanitization
- **Memory Sanitization:** Validate provenance and content before use.
- **Retrieved Content Filtering:** Remove embedded instructions from fetched documents.
- **Output Sanitization:** Redact PII, remove embedded commands, block unsafe outputs.

### Workflow Monitoring and Validation
- **Multi-Step Pattern Detection:** Monitor sequences for harmful patterns.
- **Anomaly Detection:** Baselines for normal behavior; investigate deviations.
- **Circuit Breakers:** Automatic suspension on anomalies; hold for human review.

### Graceful Degradation
- **Reduced Permission Modes:** Auto-revoke high-risk permissions on suspicious behavior.
- **Increased Human Oversight:** Escalate more decisions when confidence is low.
- **Read-Only Fallback:** Restrict to read-only mode if write operations seem problematic.

## Layered Defense in Practice

- **Prevention** stops most attacks before they succeed.
- **Detection** identifies attacks that bypass prevention.
- **Mitigation** limits damage from attacks that evade both.

Proactive security measures reduce incident response costs by 60-70% compared to reactive approaches.

---

**Previous:** [Part 3: Defense Architecture](part3_defense_architecture.md)
**Next:** [Part 5: Security Frameworks](part5_security_frameworks.md)
