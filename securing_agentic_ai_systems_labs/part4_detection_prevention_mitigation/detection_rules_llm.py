"""
Part 4 -- Detection, Prevention, and Mitigation: LLM-Powered Rule Generator

Uses opencode LLM to dynamically generate detection rules for 5 attack
scenarios. Simulates a realistic detection engineering workflow where
an LLM helps write security rules.

Run:  python detection_rules_llm.py
"""

import json
import os
import subprocess
import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Configuration ----------

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/mimo-v2.5")
LLM_TIMEOUT = int(os.environ.get("OPENCODE_TIMEOUT", "30"))
RULE_LIMIT = int(os.environ.get("OPENCODE_RULE_LIMIT", "5"))

# ---------- Constants ----------

DEFENSE_CATEGORIES = ["detection", "prevention", "mitigation"]

ATTACK_SCENARIOS = [
    {
        "id": "prompt_injection",
        "name": "Prompt Injection",
        "context": (
            "An attacker sends crafted inputs to manipulate an AI agent's behavior. "
            "The agent processes user messages, system prompts, and external content. "
            "Injection may be direct (user input) or indirect (embedded in documents)."
        ),
    },
    {
        "id": "data_exfiltration",
        "name": "Data Exfiltration",
        "context": (
            "An agent with access to sensitive data (customer records, financial data, "
            "source code) may be tricked into exporting that data through legitimate "
            "tool chains — writing to files, calling external APIs, or composing emails."
        ),
    },
    {
        "id": "privilege_escalation",
        "name": "Privilege Escalation",
        "context": (
            "An agent with limited permissions is manipulated into invoking tools or "
            "APIs beyond its authorized scope. The agent chains its legitimate permissions "
            "to create higher-level capabilities it should not have."
        ),
    },
    {
        "id": "memory_poisoning",
        "name": "Memory Poisoning",
        "context": (
            "An attacker injects malicious entries into an agent's long-term memory. "
            "These poisoned entries persist across sessions and influence future behavior. "
            "Research shows 95%+ success rates with poisoned memories comprising only 10% "
            "of total entries but dominating retrieval results."
        ),
    },
    {
        "id": "tool_chaining_abuse",
        "name": "Tool Chaining Abuse",
        "context": (
            "An agent chains multiple tools in unexpected sequences to achieve goals "
            "outside its intended purpose. Each individual tool call may be authorized, "
            "but the combined chain enables data exfiltration or unauthorized actions."
        ),
    },
]

PROMPT_TEMPLATE = """You are a security engineer writing detection rules for agentic AI systems.

Attack scenario: {name}

Context: {context}

Write a detection rule for this attack. Return a JSON object with these fields ONLY:
- rule_name: short descriptive name (string)
- description: what this rule detects (string)
- trigger: what event fires the rule (string)
- condition: criteria that must be met (string)
- severity: one of critical/high/medium/low (string)
- action: one of alert/block/escalate/log (string)
- false_positive_rate: estimated rate 0.0-1.0 (number)
- defense_category: one of detection/prevention/mitigation (string)

Return ONLY valid JSON, no markdown fences, no explanation."""


# ---------- LLM Functions ----------


def ask_llm(prompt: str) -> str:
    """Call opencode LLM via subprocess."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=LLM_TIMEOUT,
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


def parse_rule(raw: str, scenario: dict) -> dict | None:
    """Parse LLM response into a rule dict, with validation."""
    text = raw.strip()
    if text.startswith("["):
        print(f"    [ERROR] LLM call failed: {text[:80]}")
        return None

    try:
        rule = json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip("`").removeprefix("json").strip()
        try:
            rule = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"    [ERROR] Could not parse JSON: {text[:80]}")
            return None

    required = ["rule_name", "description", "trigger", "condition",
                 "severity", "action", "false_positive_rate", "defense_category"]
    for field in required:
        if field not in rule:
            rule[field] = "unknown" if isinstance(rule.get(field), str) else 0

    rule["attack_type"] = scenario["id"]
    rule["rule_id"] = f"LLM-{scenario['id'][:3].upper()}"
    return rule


def generate_rules() -> list[dict]:
    """Generate detection rules for each scenario via LLM."""
    rules = []
    limit = min(RULE_LIMIT, len(ATTACK_SCENARIOS))

    for i, scenario in enumerate(ATTACK_SCENARIOS[:limit]):
        print(f"  [{i + 1}/{limit}] Generating rule for: {scenario['name']}...")

        prompt = PROMPT_TEMPLATE.format(
            name=scenario["name"],
            context=scenario["context"],
        )
        raw = ask_llm(prompt)
        rule = parse_rule(raw, scenario)

        if rule:
            rules.append(rule)
            sev = rule.get("severity", "?").upper()
            cat = rule.get("defense_category", "?")
            print(f"           -> {rule['rule_name']} [{sev}] ({cat})")
        else:
            print(f"           -> SKIPPED (parse failed)")

    return rules


# ---------- Display Functions ----------


def print_generated_rule(rule: dict, index: int) -> None:
    """Print a single generated rule."""
    sev = rule.get("severity", "?").upper()
    fpr = rule.get("false_positive_rate", 0)
    if isinstance(fpr, (int, float)):
        fpr_str = f"{fpr * 100:.0f}%"
    else:
        fpr_str = str(fpr)

    print(f"  [{rule.get('rule_id', '?')}] {rule.get('rule_name', '?')}")
    print(f"    Attack:     {rule.get('attack_type', '?')}")
    print(f"    Category:   {rule.get('defense_category', '?').title()}")
    print(f"    Severity:   {sev}")
    print(f"    Action:     {rule.get('action', '?').title()}")
    print(f"    FP Rate:    {fpr_str}")
    print(f"    Trigger:    {rule.get('trigger', '?')}")
    cond = textwrap.fill(str(rule.get("condition", "?")), width=55,
                         initial_indent="", subsequent_indent="              ")
    print(f"    Condition:  {cond}")
    desc = textwrap.fill(str(rule.get("description", "?")), width=55,
                         initial_indent="", subsequent_indent="              ")
    print(f"    Description: {desc}")
    print()


def print_rules_summary(rules: list[dict]) -> None:
    """Print summary of all generated rules."""
    print("=" * 70)
    print("  GENERATED RULES SUMMARY")
    print("=" * 70)

    if not rules:
        print("\n  No rules were generated.\n")
        return

    for i, rule in enumerate(rules, 1):
        print_generated_rule(rule, i)


def print_coverage_table(rules: list[dict]) -> None:
    """Print coverage table."""
    print("=" * 70)
    print("  DEFENSE COVERAGE TABLE (LLM-Generated)")
    print("=" * 70)

    coverage: dict[str, dict[str, int]] = {
        at: {c: 0 for c in DEFENSE_CATEGORIES} for at in [s["id"] for s in ATTACK_SCENARIOS]
    }
    for rule in rules:
        at = rule.get("attack_type", "")
        cat = rule.get("defense_category", "")
        if at in coverage and cat in coverage[at]:
            coverage[at][cat] += 1

    col_w = 16
    header = f"  {'Attack Type':<25}"
    for cat in DEFENSE_CATEGORIES:
        header += f" {cat.title():^{col_w}}"
    print(header)
    print("  " + "-" * (25 + col_w * len(DEFENSE_CATEGORIES)))

    for scenario in ATTACK_SCENARIOS:
        at = scenario["id"]
        row = f"  {scenario['name']:<25}"
        for cat in DEFENSE_CATEGORIES:
            count = coverage[at][cat]
            cell = str(count) if count > 0 else "-"
            row += f" {cell:^{col_w}}"
        print(row)

    print()


def print_validation_report(rules: list[dict]) -> None:
    """Print validation report for generated rules."""
    print("=" * 70)
    print("  RULE VALIDATION REPORT")
    print("=" * 70)

    valid = 0
    issues = []
    for rule in rules:
        rule_issues = []
        if rule.get("severity") not in ("critical", "high", "medium", "low"):
            rule_issues.append(f"invalid severity: {rule.get('severity')}")
        if rule.get("action") not in ("alert", "block", "escalate", "log"):
            rule_issues.append(f"invalid action: {rule.get('action')}")
        if rule.get("defense_category") not in DEFENSE_CATEGORIES:
            rule_issues.append(f"invalid category: {rule.get('defense_category')}")
        fpr = rule.get("false_positive_rate", -1)
        if not isinstance(fpr, (int, float)) or fpr < 0 or fpr > 1:
            rule_issues.append(f"invalid FP rate: {fpr}")

        if rule_issues:
            issues.append((rule.get("rule_id", "?"), rule_issues))
        else:
            valid += 1

    print(f"\n  Valid rules:   {valid}/{len(rules)}")
    print(f"  Invalid rules: {len(issues)}/{len(rules)}")

    if issues:
        print("\n  Issues:")
        for rule_id, rule_issues in issues:
            print(f"    [{rule_id}] {'; '.join(rule_issues)}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 4 -- Detection, Prevention, and Mitigation")
    print("  LLM-Powered Detection Rule Generator")
    print("=" * 70)
    print(f"  Model:       {MODEL}")
    print(f"  Timeout:     {LLM_TIMEOUT}s per call")
    print(f"  Rule Limit:  {RULE_LIMIT}")
    print("=" * 70 + "\n")

    rules = generate_rules()

    print()
    print_rules_summary(rules)
    print_coverage_table(rules)
    print_validation_report(rules)

    json_output = {
        "model": MODEL,
        "rules": rules,
        "total_generated": len(rules),
    }
    json_path = "detection_rules_llm.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON rules written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "LLM-generated detection rules provide a fast starting point for security "
        "engineering, but require human review for accuracy, false positive tuning, "
        "and integration with existing monitoring infrastructure. The LLM excels at "
        "pattern recognition but needs validation against real-world attack data.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
