# Part 4 — Detection, Prevention, and Mitigation

> Source: [../securing_agentic_ai_systems/part4_detection_prevention_mitigation.md](../../securing_agentic_ai_systems/part4_detection_prevention_mitigation.md)

## Concept in 10 lines

- **Detection** identifies attacks (visibility layer). **Prevention** stops them (first defense). **Mitigation** limits damage (safety net).
- Detection accuracy: 84.9% for explicit attacks, 77.1% for indirect, 74.6% for stealth.
- Prevention: input validation, privilege control, intent-based defense, adversarial testing.
- Mitigation: sandboxing, network segmentation, rate limiting, circuit breakers, graceful degradation.
- Layered defense: prevention stops most, detection catches bypasses, mitigation bounds remaining damage.
- Proactive measures reduce incident response costs by 60-70% vs reactive approaches.
- Guardrails primarily implement prevention. Permissions implement prevention + mitigation. Auditability enables detection.
- No single approach provides complete protection — layered defenses are necessary.

## Vibe-coding challenge

**Detection rule builder.** Define detection rules for 5 different attack patterns:

1. Define 5 attack scenarios (prompt injection, data exfiltration, privilege escalation, memory poisoning, tool chaining abuse).
2. For each scenario, create a detection rule with:
   - **Rule name** and description
   - **Trigger:** What event or pattern triggers the rule?
   - **Condition:** What criteria must be met?
   - **Severity:** Critical / High / Medium / Low
   - **Action:** What happens when the rule fires? (alert, block, escalate, log)
   - **False positive rate estimate:** How likely is this a false positive?
3. Output all rules as structured JSON.
4. Print a summary table showing coverage across the 3 defense categories (detection/prevention/mitigation).
5. Identify any gaps — which attack patterns don't have good detection rules?

> Bonus: add a "layered defense map" showing how detection, prevention, and mitigation overlap for each attack.

### How to start

Tell me one of:
- *"Scaffold the 5 attack scenarios and rule structure"*
- *"Use MITRE ATLAS technique IDs"*
- *"Show me the JSON schema first"*
- *"I want to define rules for my own system"*
