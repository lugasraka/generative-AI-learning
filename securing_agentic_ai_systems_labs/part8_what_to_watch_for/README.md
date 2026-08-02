# Part 8 — What to Watch For

> Source: [../securing_agentic_ai_systems/part8_what_to_watch_for.md](../../securing_agentic_ai_systems/part8_what_to_watch_for.md)

## Concept in 10 lines

- **Authorization anomalies:** high-frequency denials, purpose-inconsistent requests, permission escalation attempts.
- **Tool usage anomalies:** frequency spikes/drops, unusual combinations, parameter pattern changes.
- **Data access anomalies:** volume spikes, unusual timing, scope violations.
- **Reasoning changes:** depth changes, goal statement changes, references to non-existent instructions.
- **Output changes:** style/tone shifts, quality degradation, information the agent shouldn't have.
- **Memory anomalies:** unrelated retrievals, unusual creation rates, repeated retrieval patterns.
- **Immediate escalation:** multiple anomaly categories together, high-impact operations, known attack patterns, security control modifications.
- Detection accuracy varies: explicit (84.9%), indirect (77.1%), stealth (74.6%).
- False positive reduction is critical — tune rules based on patterns.

## Vibe-coding challenge

**Monitoring dashboard spec.** Define metrics, thresholds, and alert rules for an agent monitoring dashboard:

1. Define a sample agent system with baseline behavior (typical tool calls, data access patterns, response characteristics).
2. For each anomaly category (authorization, tool usage, data access, reasoning, output, memory), define:
   - **Metrics:** What specific values to track (e.g., tool_calls_per_hour, data_access_bytes, response_length)
   - **Baselines:** What's normal for this agent?
   - **Thresholds:** When should alerts fire? (e.g., 2-3 standard deviations from mean)
   - **Alert severity:** Critical / Warning / Info
   - **Recommended action:** What should the operator do?
3. Output a dashboard spec as structured JSON with all metrics and thresholds.
4. Print a summary showing: category, metric, baseline, threshold, alert action.
5. Simulate 5 anomalous events and show which alerts would fire.

> Bonus: add a "monitoring coverage score" — what percentage of attack patterns have detection rules?

### How to start

Tell me one of:
- *"Scaffold the baseline behavior and metric definitions"*
- *"I want to monitor my own agent system"*
- *"Show me the threshold calculation logic first"*
- *"Make it a reusable monitoring spec template"*
