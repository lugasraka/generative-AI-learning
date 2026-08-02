# Part 8: What to Watch For in Your Systems

Security monitoring for agentic systems requires understanding what normal behavior looks like so you can identify deviations that might indicate compromise.

---

## Warning Signs of Compromise

### Authorization Anomalies

- **High Frequency Denials:** Repeated denied actions may indicate reconnaissance or probing.
- **Purpose-Inconsistent Requests:** Data analysis agent requesting email permissions, read-only agents requesting writes.
- **Permission Escalation:** Agents attempting to modify their own permissions or create accounts.

### Tool Usage Anomalies

- **Frequency Changes:** Sudden spikes (possible exfiltration) or drops (possible evasion).
- **Unusual Combinations:** Read data + encode + external communication = exfiltration pattern.
- **Parameter Patterns:** Unexpected file paths, database tables, API endpoints, large data volumes.

### Data Access Anomalies

- **Volume:** Significantly more data than typical, sequential scanning, bulk downloads.
- **Timing:** Operations during unusual hours, rapid-fire operations.
- **Scope:** Cross-user access, geographic violations, organizational boundary crossings.

## Behavioral Anomalies

### Reasoning Pattern Changes

- Sudden changes in reasoning depth (simple outputs might indicate prompt override).
- Goal statement changes that don't match documented purpose.
- References to instructions not in actual user input.

### Output Characteristic Changes

- Different tones, formats, or styles.
- Verbosity changes.
- Increased errors or hallucinations.
- Information the agent shouldn't have access to.

### Memory Access Patterns

- Retrieving memories unrelated to current tasks.
- Unusual memory creation rates or content.
- Repeated retrieval of the same memories.

## Log Patterns Indicating Attacks

### Prompt Injection Indicators

- Instructions to ignore previous directions
- Role-playing prompts
- Requests to repeat system prompts
- Unusual encoding (base64, unicode tricks)
- Clustered guardrail violations from same source

### Memory Poisoning Indicators

- Memories containing embedded instructions
- Fabricated or obviously false information
- Memories without clear attribution
- Timestamps inconsistent with task execution

### Supply Chain Indicators

- Unexpected dependency updates
- Checksum verification failures
- Unsigned configuration changes
- Permission expansions without approval

## When to Escalate

### Immediate Escalation Triggers

- **Multiple anomaly categories** occurring together
- **High-impact operations** (data deletion, permission changes, external comms, financial transactions)
- **Known attack pattern matches** (MITRE ATLAS techniques)
- **Security control modifications** (disabling logging, bypassing guardrails)

### Investigation Workflow

1. **Automated Triage:** Severity, confidence, context assessment.
2. **Human Review:** Full logs, correlated agents, user context, recent changes.
3. **Decision:** False positive / Benign anomaly / Possible attack / Confirmed attack.

### Incident Response

- **Immediate:** Activate kill-switch, preserve logs, identify scope, assess damage.
- **Containment:** Revoke credentials, isolate systems, stop lateral movement.
- **Remediation:** Fix vulnerability, restore from clean backups, deploy updated controls.
- **Post-Incident:** Root cause analysis, update controls, review procedures.

## Continuous Monitoring Improvement

- **False Positive Reduction:** Tune detection rules based on patterns.
- **Attack Pattern Updates:** Update monitoring for new techniques.
- **Baseline Refreshes:** Periodically update normal behavior baselines.
- **Feedback Loops:** Each incident informs detection improvements.

---

**Previous:** [Part 7: Addressing Vulnerabilities](part7_addressing_vulnerabilities.md)
**Next:** [Part 9: Building Security by Design](part9_building_security_by_design.md)
