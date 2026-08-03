"""
Part 8 -- What to Watch For: Monitoring Dashboard Spec

Builds a monitoring dashboard specification for a sample agent system.
Defines baselines, thresholds, and alert rules across 6 anomaly categories,
simulates 5 anomalous events, and calculates monitoring coverage.

Run:  python monitoring_dashboard.py
"""

import json
import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

CATEGORIES = {
    "authorization": "Authorization Anomalies",
    "tool_usage": "Tool Usage Anomalies",
    "data_access": "Data Access Anomalies",
    "reasoning": "Reasoning Pattern Changes",
    "output": "Output Characteristic Changes",
    "memory": "Memory Access Patterns",
}

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


# ---------- Agent Baseline ----------

AGENT_SYSTEM = {
    "name": "Customer Support Agent",
    "baseline": {
        "tool_calls_per_hour": 15,
        "denial_rate_per_hour": 2,
        "data_export_kb_per_hour": 50,
        "response_length_avg": 320,
        "memory_reads_per_hour": 8,
        "memory_writes_per_hour": 1,
    },
}


# ---------- Dashboard Specification ----------

DASHBOARD_SPEC: dict[str, list[dict]] = {
    "authorization": [
        {
            "metric": "denial_rate_per_hour",
            "description": "Number of denied authorization requests per hour",
            "baseline": 2,
            "threshold_warning": 8,
            "threshold_critical": 20,
            "action": "Investigate source of denied requests; may indicate reconnaissance or probing",
        },
        {
            "metric": "purpose_inconsistency_score",
            "description": "Frequency of requests outside agent's stated purpose (0-100)",
            "baseline": 5,
            "threshold_warning": 25,
            "threshold_critical": 50,
            "action": "Review request patterns; check for prompt injection or goal hijacking",
        },
        {
            "metric": "permission_escalation_attempts",
            "description": "Attempts to modify permissions or access restricted resources per hour",
            "baseline": 0,
            "threshold_warning": 1,
            "threshold_critical": 3,
            "action": "IMMEDIATE: Block agent, activate kill-switch, investigate compromise",
        },
    ],
    "tool_usage": [
        {
            "metric": "tool_calls_per_hour",
            "description": "Total tool invocations per hour",
            "baseline": 15,
            "threshold_warning": 30,
            "threshold_critical": 50,
            "action": "Check for exfiltration pattern (read+encode+send); verify tool call context",
        },
        {
            "metric": "unusual_combination_score",
            "description": "Frequency of tool combinations not seen in baseline (0-100)",
            "baseline": 3,
            "threshold_warning": 20,
            "threshold_critical": 40,
            "action": "Analyze tool chain sequences; look for cross-domain exfiltration patterns",
        },
        {
            "metric": "parameter_anomaly_score",
            "description": "Tool parameters deviating from expected patterns (0-100)",
            "baseline": 5,
            "threshold_warning": 25,
            "threshold_critical": 50,
            "action": "Review tool call parameters; check for injection or unauthorized access",
        },
    ],
    "data_access": [
        {
            "metric": "data_volume_kb_per_hour",
            "description": "Data accessed or exported per hour in KB",
            "baseline": 50,
            "threshold_warning": 150,
            "threshold_critical": 300,
            "action": "Investigate bulk data access; check for exfiltration or unauthorized queries",
        },
        {
            "metric": "unusual_timing_score",
            "description": "Data access during off-hours or unusual patterns (0-100)",
            "baseline": 2,
            "threshold_warning": 20,
            "threshold_critical": 40,
            "action": "Review access logs for after-hours activity; verify legitimate use case",
        },
        {
            "metric": "scope_violation_count",
            "description": "Access attempts outside agent's data scope per hour",
            "baseline": 0,
            "threshold_warning": 2,
            "threshold_critical": 5,
            "action": "Block access, review scope boundaries, check for privilege escalation",
        },
    ],
    "reasoning": [
        {
            "metric": "reasoning_depth_score",
            "description": "Average reasoning depth of agent responses (0-100)",
            "baseline": 65,
            "threshold_warning_low": 40,
            "threshold_critical_low": 25,
            "action": "Check for prompt override or simplified behavior indicating compromise",
        },
        {
            "metric": "goal_alignment_score",
            "description": "Alignment of agent actions with stated goals (0-100)",
            "baseline": 90,
            "threshold_warning_low": 70,
            "threshold_critical_low": 50,
            "action": "Investigate goal drift; review recent interactions for hijacking attempts",
        },
        {
            "metric": "phantom_instruction_count",
            "description": "References to instructions not in actual user input per hour",
            "baseline": 0,
            "threshold_warning": 1,
            "threshold_critical": 3,
            "action": "IMMEDIATE: Check for injection; review system prompt integrity",
        },
    ],
    "output": [
        {
            "metric": "style_consistency_score",
            "description": "Consistency of output style/tone with baseline (0-100)",
            "baseline": 92,
            "threshold_warning_low": 75,
            "threshold_critical_low": 60,
            "action": "Review recent outputs for style shifts indicating behavioral change",
        },
        {
            "metric": "quality_score",
            "description": "Output quality metrics (accuracy, coherence, relevance) (0-100)",
            "baseline": 88,
            "threshold_warning_low": 70,
            "threshold_critical_low": 55,
            "action": "Check for degraded performance; may indicate memory poisoning or context manipulation",
        },
        {
            "metric": "info_leak_count",
            "description": "Output containing information agent shouldn't have access to per hour",
            "baseline": 0,
            "threshold_warning": 1,
            "threshold_critical": 2,
            "action": "IMMEDIATE: Block output, investigate data access, check for exfiltration",
        },
    ],
    "memory": [
        {
            "metric": "unrelated_retrieval_score",
            "description": "Memory retrievals unrelated to current task (0-100)",
            "baseline": 4,
            "threshold_warning": 20,
            "threshold_critical": 40,
            "action": "Check for memory poisoning; verify retrieval relevance filtering",
        },
        {
            "metric": "memory_write_rate",
            "description": "Memory writes per hour",
            "baseline": 1,
            "threshold_warning": 5,
            "threshold_critical": 15,
            "action": "Investigate write patterns; may indicate poisoning or injection",
        },
        {
            "metric": "repeated_retrieval_count",
            "description": "Same memory entry retrieved repeatedly in short window",
            "baseline": 2,
            "threshold_warning": 8,
            "threshold_critical": 20,
            "action": "Check for manipulation of retrieval mechanism or poisoned entry dominance",
        },
    ],
}


# ---------- Simulated Anomalous Events ----------

SIMULATED_EVENTS = [
    {
        "name": "Prompt Injection Attempt",
        "description": "Attacker sends 47 crafted prompts in 10 minutes to probe agent defenses",
        "values": {
            "authorization": {"denial_rate_per_hour": 47, "purpose_inconsistency_score": 65, "permission_escalation_attempts": 0},
            "tool_usage": {"tool_calls_per_hour": 12, "unusual_combination_score": 10, "parameter_anomaly_score": 15},
            "data_access": {"data_volume_kb_per_hour": 40, "unusual_timing_score": 5, "scope_violation_count": 0},
            "reasoning": {"reasoning_depth_score": 60, "goal_alignment_score": 85, "phantom_instruction_count": 2},
            "output": {"style_consistency_score": 88, "quality_score": 85, "info_leak_count": 0},
            "memory": {"unrelated_retrieval_score": 6, "memory_write_rate": 1, "repeated_retrieval_count": 3},
        },
    },
    {
        "name": "Data Exfiltration via Tool Chain",
        "description": "Agent chains database query -> encode -> email to external address",
        "values": {
            "authorization": {"denial_rate_per_hour": 1, "purpose_inconsistency_score": 15, "permission_escalation_attempts": 0},
            "tool_usage": {"tool_calls_per_hour": 45, "unusual_combination_score": 55, "parameter_anomaly_score": 40},
            "data_access": {"data_volume_kb_per_hour": 280, "unusual_timing_score": 10, "scope_violation_count": 3},
            "reasoning": {"reasoning_depth_score": 62, "goal_alignment_score": 78, "phantom_instruction_count": 0},
            "output": {"style_consistency_score": 82, "quality_score": 80, "info_leak_count": 1},
            "memory": {"unrelated_retrieval_score": 8, "memory_write_rate": 2, "repeated_retrieval_count": 5},
        },
    },
    {
        "name": "Memory Poisoning Attack",
        "description": "Attacker injects 15 poisoned memory entries over multiple sessions",
        "values": {
            "authorization": {"denial_rate_per_hour": 3, "purpose_inconsistency_score": 10, "permission_escalation_attempts": 0},
            "tool_usage": {"tool_calls_per_hour": 18, "unusual_combination_score": 12, "parameter_anomaly_score": 8},
            "data_access": {"data_volume_kb_per_hour": 60, "unusual_timing_score": 5, "scope_violation_count": 0},
            "reasoning": {"reasoning_depth_score": 55, "goal_alignment_score": 75, "phantom_instruction_count": 1},
            "output": {"style_consistency_score": 78, "quality_score": 72, "info_leak_count": 0},
            "memory": {"unrelated_retrieval_score": 45, "memory_write_rate": 15, "repeated_retrieval_count": 18},
        },
    },
    {
        "name": "Goal Hijacking via Gradual Drift",
        "description": "Multi-turn conversation gradually shifts agent objectives",
        "values": {
            "authorization": {"denial_rate_per_hour": 4, "purpose_inconsistency_score": 30, "permission_escalation_attempts": 0},
            "tool_usage": {"tool_calls_per_hour": 20, "unusual_combination_score": 18, "parameter_anomaly_score": 12},
            "data_access": {"data_volume_kb_per_hour": 70, "unusual_timing_score": 8, "scope_violation_count": 1},
            "reasoning": {"reasoning_depth_score": 35, "goal_alignment_score": 45, "phantom_instruction_count": 0},
            "output": {"style_consistency_score": 65, "quality_score": 68, "info_leak_count": 0},
            "memory": {"unrelated_retrieval_score": 12, "memory_write_rate": 2, "repeated_retrieval_count": 6},
        },
    },
    {
        "name": "Normal Operation (Baseline)",
        "description": "Agent operating normally within expected parameters",
        "values": {
            "authorization": {"denial_rate_per_hour": 2, "purpose_inconsistency_score": 5, "permission_escalation_attempts": 0},
            "tool_usage": {"tool_calls_per_hour": 15, "unusual_combination_score": 3, "parameter_anomaly_score": 5},
            "data_access": {"data_volume_kb_per_hour": 50, "unusual_timing_score": 2, "scope_violation_count": 0},
            "reasoning": {"reasoning_depth_score": 65, "goal_alignment_score": 90, "phantom_instruction_count": 0},
            "output": {"style_consistency_score": 92, "quality_score": 88, "info_leak_count": 0},
            "memory": {"unrelated_retrieval_score": 4, "memory_write_rate": 1, "repeated_retrieval_count": 2},
        },
    },
]


# ---------- Analysis Functions ----------


def check_metric(metric_spec: dict, value: float) -> str | None:
    """Check if a metric value triggers an alert."""
    name = metric_spec["metric"]

    # Handle "low is bad" metrics (reasoning_depth, goal_alignment, style, quality)
    if "threshold_critical_low" in metric_spec:
        if value <= metric_spec["threshold_critical_low"]:
            return "critical"
        if value <= metric_spec.get("threshold_warning_low", 999):
            return "warning"
        return None

    # Handle "high is bad" metrics
    if value >= metric_spec.get("threshold_critical", 999):
        return "critical"
    if value >= metric_spec.get("threshold_warning", 999):
        return "warning"
    return None


def simulate_event(event: dict) -> list[dict]:
    """Simulate an anomalous event and return triggered alerts."""
    alerts = []
    for category, values in event["values"].items():
        specs = DASHBOARD_SPEC.get(category, [])
        for spec in specs:
            metric_name = spec["metric"]
            if metric_name in values:
                severity = check_metric(spec, values[metric_name])
                if severity:
                    alerts.append({
                        "category": CATEGORIES[category],
                        "metric": metric_name,
                        "value": values[metric_name],
                        "severity": severity,
                        "action": spec["action"],
                    })
    alerts.sort(key=lambda a: SEVERITY_ORDER.get(a["severity"], 99))
    return alerts


def calculate_coverage() -> dict:
    """Calculate monitoring coverage score."""
    total_attack_patterns = 15  # known attack patterns from course
    detected = sum(
        len(metrics) for metrics in DASHBOARD_SPEC.values()
    )
    return {
        "total_metrics": detected,
        "total_categories": len(DASHBOARD_SPEC),
        "coverage_pct": min(100, (detected / total_attack_patterns) * 100),
    }


# ---------- Display Functions ----------


def print_baseline_profile() -> None:
    """Print agent baseline behavior."""
    print("=" * 70)
    print("  AGENT BASELINE PROFILE")
    print("=" * 70)
    print(f"\n  System: {AGENT_SYSTEM['name']}")
    print("\n  Normal Behavior:")
    for metric, value in AGENT_SYSTEM["baseline"].items():
        label = metric.replace("_", " ").title()
        print(f"    {label:<35} {value}")
    print()


def print_dashboard_spec() -> None:
    """Print full dashboard specification."""
    print("=" * 70)
    print("  MONITORING DASHBOARD SPECIFICATION")
    print("=" * 70)

    for cat_id, cat_label in CATEGORIES.items():
        metrics = DASHBOARD_SPEC.get(cat_id, [])
        print(f"\n  {cat_label}")
        print("  " + "-" * 55)

        for m in metrics:
            print(f"    {m['metric']}")
            print(f"      Baseline:    {m['baseline']}")
            if "threshold_critical_low" in m:
                print(f"      Warning:     < {m.get('threshold_warning_low', '?')}")
                print(f"      Critical:    < {m['threshold_critical_low']}")
            else:
                print(f"      Warning:     >= {m.get('threshold_warning', '?')}")
                print(f"      Critical:    >= {m.get('threshold_critical', '?')}")
            action = textwrap.fill(m["action"], width=50, initial_indent="      Action:      ", subsequent_indent="                   ")
            print(action)
            print()


def print_simulation_results() -> None:
    """Print simulation results for all events."""
    print("=" * 70)
    print("  ANOMALY SIMULATION RESULTS")
    print("=" * 70)

    for event in SIMULATED_EVENTS:
        alerts = simulate_event(event)
        print(f"\n  Event: {event['name']}")
        print(f"  Description: {event['description']}")

        if not alerts:
            print("  Result: No alerts fired (normal operation)")
        else:
            print(f"  Result: {len(alerts)} alert(s) fired")
            for a in alerts:
                marker = "!!!" if a["severity"] == "critical" else ("!  " if a["severity"] == "warning" else "   ")
                print(f"    {marker} [{a['severity'].upper():<8}] {a['category']}: {a['metric']} = {a['value']}")

    print()


def print_coverage() -> None:
    """Print monitoring coverage score."""
    print("=" * 70)
    print("  MONITORING COVERAGE")
    print("=" * 70)

    cov = calculate_coverage()
    bar_len = int(cov["coverage_pct"] / 100 * 20)
    bar = "#" * bar_len + "." * (20 - bar_len)

    print(f"\n  Metrics Defined:  {cov['total_metrics']}")
    print(f"  Categories:       {cov['total_categories']}")
    print(f"  Coverage:         [{bar}] {cov['coverage_pct']:.0f}%")
    print(f"\n  Note: Coverage measures metric definition breadth, not detection accuracy.")
    print(f"  Detection accuracy varies: explicit (84.9%), indirect (77.1%), stealth (74.6%).")
    print()


def print_summary_table() -> None:
    """Print compact summary table."""
    print("=" * 70)
    print("  SUMMARY TABLE")
    print("=" * 70)

    print(f"\n  {'Category':<25} {'Metric':<30} {'Baseline':<10} {'Warn':<8} {'Crit':<8}")
    print("  " + "-" * 81)

    for cat_id, cat_label in CATEGORIES.items():
        for m in DASHBOARD_SPEC.get(cat_id, []):
            if "threshold_critical_low" in m:
                warn = f"<{m.get('threshold_warning_low', '?')}"
                crit = f"<{m['threshold_critical_low']}"
            else:
                warn = f">={m.get('threshold_warning', '?')}"
                crit = f">={m.get('threshold_critical', '?')}"
            print(f"  {cat_label:<25} {m['metric']:<30} {str(m['baseline']):<10} {warn:<8} {crit:<8}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 8 -- What to Watch For")
    print("  Monitoring Dashboard Specification")
    print(f"  System: {AGENT_SYSTEM['name']}")
    print("=" * 70 + "\n")

    print_baseline_profile()
    print_dashboard_spec()
    print_simulation_results()
    print_coverage()
    print_summary_table()

    # JSON export
    json_output = {
        "agent_system": AGENT_SYSTEM,
        "dashboard_spec": DASHBOARD_SPEC,
        "simulated_events": [
            {"name": e["name"], "alerts": simulate_event(e)}
            for e in SIMULATED_EVENTS
        ],
        "coverage": calculate_coverage(),
    }
    json_path = "monitoring_dashboard.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON dashboard spec written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "False positive reduction is critical -- tune rules based on patterns. "
        "Detection accuracy varies: explicit attacks (84.9%), indirect (77.1%), "
        "stealth (74.6%). When multiple anomaly categories trigger together, "
        "escalate immediately. Continuous monitoring improvement is essential.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
