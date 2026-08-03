"""
Part 4 -- Detection, Prevention, and Mitigation: Detection Rule Builder

Builds detection rules for 5 attack scenarios, maps each to the three
defense categories (detection/prevention/mitigation), prints coverage
tables, identifies gaps, and visualizes layered defense.

Run:  python detection_rules.py
"""

import json
import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

DEFENSE_CATEGORIES = ["detection", "prevention", "mitigation"]

ATTACK_TYPES = {
    "prompt_injection": "Prompt Injection",
    "data_exfiltration": "Data Exfiltration",
    "privilege_escalation": "Privilege Escalation",
    "memory_poisoning": "Memory Poisoning",
    "tool_chaining_abuse": "Tool Chaining Abuse",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# ---------- Detection Rule Definitions ----------

RULES: list[dict] = [
    # --- Prompt Injection ---
    {
        "rule_id": "R001",
        "rule_name": "Direct Prompt Injection Signatures",
        "description": "Detects known prompt injection patterns in user inputs such as instruction overrides, role manipulation, and delimiter escapes.",
        "attack_type": "prompt_injection",
        "trigger": "User input received by agent",
        "condition": "Input matches regex patterns: 'ignore previous', 'you are now', 'system:', '--- END ---', or base64-encoded instructions",
        "severity": "critical",
        "action": "block",
        "false_positive_rate": 0.05,
        "defense_category": "detection",
    },
    {
        "rule_id": "R002",
        "rule_name": "Intent Validation on Agent Actions",
        "description": "Validates that agent actions align with its stated purpose. Flags actions outside the agent's verified intent scope.",
        "attack_type": "prompt_injection",
        "trigger": "Agent attempts a tool call or action",
        "condition": "Action does not match any action in the agent's purpose-bound allowlist",
        "severity": "critical",
        "action": "block",
        "false_positive_rate": 0.08,
        "defense_category": "prevention",
    },
    # --- Data Exfiltration ---
    {
        "rule_id": "R003",
        "rule_name": "PII Exposure in Agent Output",
        "description": "Scans agent-generated output for patterns matching PII: SSN, credit card numbers, email addresses, phone numbers.",
        "attack_type": "data_exfiltration",
        "trigger": "Agent generates output (response, file, API call body)",
        "condition": "Output contains regex matches for PII patterns (SSN: xxx-xx-xxxx, CC: 16-digit sequences, email: xxx@xxx.xxx)",
        "severity": "high",
        "action": "alert",
        "false_positive_rate": 0.10,
        "defense_category": "detection",
    },
    {
        "rule_id": "R004",
        "rule_name": "Data Export Volume Rate Limit",
        "description": "Limits the volume of data an agent can export within a time window to prevent bulk exfiltration.",
        "attack_type": "data_exfiltration",
        "trigger": "Agent writes data to external destination (file, API, email)",
        "condition": "Data volume exceeds threshold (e.g., >100KB/min or >1MB/hour) or exceeds row count limit",
        "severity": "high",
        "action": "block",
        "false_positive_rate": 0.03,
        "defense_category": "mitigation",
    },
    # --- Privilege Escalation ---
    {
        "rule_id": "R005",
        "rule_name": "Tool Scope Violation Detection",
        "description": "Monitors tool invocations for scope violations -- agent calling tools outside its assigned permission boundary.",
        "attack_type": "privilege_escalation",
        "trigger": "Agent invokes a tool or API endpoint",
        "condition": "Tool ID is not in the agent's authorized tool list, or requires a permission level higher than the agent's current role",
        "severity": "critical",
        "action": "block",
        "false_positive_rate": 0.02,
        "defense_category": "detection",
    },
    {
        "rule_id": "R006",
        "rule_name": "Unauthorized API Call Kill-Switch",
        "description": "Immediately terminates agent execution when it attempts an API call that exceeds its permission boundary.",
        "attack_type": "privilege_escalation",
        "trigger": "Agent attempts API call to a protected endpoint",
        "condition": "API endpoint requires higher privilege than agent's current token, or endpoint is on the deny-list",
        "severity": "critical",
        "action": "block",
        "false_positive_rate": 0.01,
        "defense_category": "prevention",
    },
    # --- Memory Poisoning ---
    {
        "rule_id": "R007",
        "rule_name": "Anomalous Memory Write Detection",
        "description": "Detects memory writes that deviate from the agent's normal write patterns -- unusual provenance, frequency, or content characteristics.",
        "attack_type": "memory_poisoning",
        "trigger": "Agent writes to long-term memory store",
        "condition": "Write source is external (not agent-initiated), OR write frequency exceeds baseline by 3x, OR content contains instruction-like patterns",
        "severity": "high",
        "action": "alert",
        "false_positive_rate": 0.12,
        "defense_category": "detection",
    },
    {
        "rule_id": "R008",
        "rule_name": "Memory Entry TTL Expiration",
        "description": "Automatically expires memory entries after a configurable TTL to limit persistence of poisoned data.",
        "attack_type": "memory_poisoning",
        "trigger": "Memory entry is accessed for retrieval",
        "condition": "Entry age exceeds configured TTL (e.g., 30 days for preferences, 7 days for learned patterns)",
        "severity": "medium",
        "action": "log",
        "false_positive_rate": 0.0,
        "defense_category": "mitigation",
    },
    # --- Tool Chaining Abuse ---
    {
        "rule_id": "R009",
        "rule_name": "Tool Chain Depth Monitor",
        "description": "Tracks the depth of tool call chains and flags when the agent chains more tools than its normal workflow requires.",
        "attack_type": "tool_chaining_abuse",
        "trigger": "Agent initiates a new tool call within an active chain",
        "condition": "Chain depth exceeds threshold (e.g., >5 sequential tool calls without user input), OR chain includes tools from unrelated domains",
        "severity": "high",
        "action": "alert",
        "false_positive_rate": 0.08,
        "defense_category": "detection",
    },
    {
        "rule_id": "R010",
        "rule_name": "Sandboxed Tool Chain Execution",
        "description": "Enforces sandboxed execution for multi-step tool chains, isolating chained operations from sensitive resources.",
        "attack_type": "tool_chaining_abuse",
        "trigger": "Agent begins a multi-tool chain (2+ tools in sequence)",
        "condition": "Chain includes any write operation or external API call; sandbox restricts network and file system access",
        "severity": "medium",
        "action": "block",
        "false_positive_rate": 0.04,
        "defense_category": "mitigation",
    },
]


# ---------- Analysis Functions ----------


def build_rules_by_attack(rules: list[dict]) -> dict[str, list[dict]]:
    """Group rules by attack type."""
    grouped: dict[str, list[dict]] = {k: [] for k in ATTACK_TYPES}
    for rule in rules:
        at = rule["attack_type"]
        if at in grouped:
            grouped[at].append(rule)
    return grouped


def build_rules_by_category(rules: list[dict]) -> dict[str, list[dict]]:
    """Group rules by defense category."""
    grouped: dict[str, list[dict]] = {c: [] for c in DEFENSE_CATEGORIES}
    for rule in rules:
        cat = rule["defense_category"]
        if cat in grouped:
            grouped[cat].append(rule)
    return grouped


def calculate_coverage(rules: list[dict]) -> dict[str, dict[str, int]]:
    """Calculate rule count per attack type per defense category."""
    coverage: dict[str, dict[str, int]] = {
        at: {c: 0 for c in DEFENSE_CATEGORIES} for at in ATTACK_TYPES
    }
    for rule in rules:
        at = rule["attack_type"]
        cat = rule["defense_category"]
        if at in coverage and cat in coverage[at]:
            coverage[at][cat] += 1
    return coverage


def find_gaps(rules: list[dict]) -> list[dict]:
    """Find attack types with missing defense coverage."""
    coverage = calculate_coverage(rules)
    gaps = []
    for at, cats in coverage.items():
        for cat, count in cats.items():
            if count == 0:
                risk_msg = {
                    "detection": "Attacks may go unnoticed.",
                    "prevention": "No first-line defense to block attacks.",
                    "mitigation": "Damage from successful attacks is unbounded.",
                }[cat]
                gaps.append({
                    "attack_type": at,
                    "attack_label": ATTACK_TYPES[at],
                    "missing_category": cat,
                    "risk": f"No {cat} rule for {ATTACK_TYPES[at]}. {risk_msg}",
                })
    return gaps


def build_layered_defense_map(rules: list[dict]) -> dict[str, dict[str, list[str]]]:
    """Build a layered defense map: attack type -> category -> rule names."""
    dmap: dict[str, dict[str, list[str]]] = {
        at: {c: [] for c in DEFENSE_CATEGORIES} for at in ATTACK_TYPES
    }
    for rule in rules:
        at = rule["attack_type"]
        cat = rule["defense_category"]
        if at in dmap and cat in dmap[at]:
            dmap[at][cat].append(rule["rule_name"])
    return dmap


# ---------- Display Functions ----------


def print_rule_detail(rule: dict) -> None:
    """Print a single rule formatted."""
    sev = rule["severity"].upper()
    fpr = f"{rule['false_positive_rate'] * 100:.0f}%"
    print(f"  [{rule['rule_id']}] {rule['rule_name']}")
    print(f"    Attack:     {ATTACK_TYPES.get(rule['attack_type'], rule['attack_type'])}")
    print(f"    Category:   {rule['defense_category'].title()}")
    print(f"    Severity:   {sev}")
    print(f"    Action:     {rule['action'].title()}")
    print(f"    FP Rate:    {fpr}")
    print(f"    Trigger:    {rule['trigger']}")
    print(f"    Condition:  ", end="")
    cond = textwrap.fill(rule["condition"], width=55, initial_indent="", subsequent_indent="              ")
    print(cond)
    print(f"    Description:", end=" ")
    desc = textwrap.fill(rule["description"], width=55, initial_indent="", subsequent_indent="              ")
    print(desc)
    print()


def print_rules_by_attack(grouped: dict[str, list[dict]]) -> None:
    """Print all rules grouped by attack type."""
    print("=" * 70)
    print("  DETECTION RULES BY ATTACK TYPE")
    print("=" * 70)

    for at, label in ATTACK_TYPES.items():
        rules = grouped.get(at, [])
        print(f"\n  --- {label} ({len(rules)} rules) ---\n")
        for rule in sorted(rules, key=lambda r: SEVERITY_ORDER.get(r["severity"], 99)):
            print_rule_detail(rule)


def print_coverage_table(coverage: dict[str, dict[str, int]]) -> None:
    """Print ASCII coverage table: attack types vs defense categories."""
    print("=" * 70)
    print("  DEFENSE COVERAGE TABLE")
    print("=" * 70)

    col_w = 16
    header = f"  {'Attack Type':<25}"
    for cat in DEFENSE_CATEGORIES:
        header += f" {cat.title():^{col_w}}"
    header += f" {'Total':^8}"
    print(header)
    print("  " + "-" * (25 + col_w * len(DEFENSE_CATEGORIES) + 8))

    for at, label in ATTACK_TYPES.items():
        row = f"  {label:<25}"
        total = 0
        for cat in DEFENSE_CATEGORIES:
            count = coverage[at][cat]
            total += count
            cell = str(count) if count > 0 else "-"
            row += f" {cell:^{col_w}}"
        row += f" {total:^8}"
        print(row)

    row = f"  {'TOTAL':<25}"
    grand = 0
    for cat in DEFENSE_CATEGORIES:
        cat_total = sum(coverage[at][cat] for at in ATTACK_TYPES)
        grand += cat_total
        row += f" {cat_total:^{col_w}}"
    row += f" {grand:^8}"
    print(row)
    print()


def print_gaps(gaps: list[dict]) -> None:
    """Print gap analysis."""
    print("=" * 70)
    print("  GAP ANALYSIS")
    print("=" * 70)

    if not gaps:
        print("\n  No gaps found -- all attack types have rules in every defense category.\n")
        return

    for gap in gaps:
        print(f"\n  [{gap['missing_category'].upper()}] {gap['attack_label']}")
        print(f"    {gap['risk']}")

    print(f"\n  Total gaps: {len(gaps)}")
    print()


def print_layered_defense_map(dmap: dict[str, dict[str, list[str]]]) -> None:
    """Print layered defense visualization."""
    print("=" * 70)
    print("  LAYERED DEFENSE MAP")
    print("=" * 70)

    for at, label in ATTACK_TYPES.items():
        print(f"\n  {label}:")
        for cat in DEFENSE_CATEGORIES:
            rules = dmap[at][cat]
            marker = "+" if rules else "-"
            rule_names = "; ".join(rules) if rules else "(none)"
            print(f"    [{marker}] {cat.title():<15} {rule_names}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 4 -- Detection, Prevention, and Mitigation")
    print("  Detection Rule Builder (Pure Python)")
    print("=" * 70 + "\n")

    by_attack = build_rules_by_attack(RULES)
    coverage = calculate_coverage(RULES)
    gaps = find_gaps(RULES)
    dmap = build_layered_defense_map(RULES)

    print_rules_by_attack(by_attack)
    print_coverage_table(coverage)
    print_gaps(gaps)
    print_layered_defense_map(dmap)

    json_output = {
        "rules": RULES,
        "coverage": coverage,
        "gaps": gaps,
    }
    json_path = "detection_rules.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON rules written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "Layered defense means prevention stops most attacks, detection catches "
        "bypasses, and mitigation bounds remaining damage. Every attack type needs "
        "rules in all three categories. Proactive measures reduce incident response "
        "costs by 60-70% vs reactive approaches.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
