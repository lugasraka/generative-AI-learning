"""
Part 8 -- What to Watch For: LLM Monitoring Dashboard Generator

Uses opencode LLM to generate a monitoring dashboard specification
for a custom agent system description. Produces baselines, thresholds,
and alert rules tailored to the described system.

Run:  python monitoring_dashboard_llm.py
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

# ---------- Constants ----------

CATEGORIES = {
    "authorization": "Authorization Anomalies",
    "tool_usage": "Tool Usage Anomalies",
    "data_access": "Data Access Anomalies",
    "reasoning": "Reasoning Pattern Changes",
    "output": "Output Characteristic Changes",
    "memory": "Memory Access Patterns",
}

SAMPLE_DESCRIPTION = (
    "A financial trading agent that executes trades within predefined limits, "
    "generates analysis reports, accesses market data feeds and portfolio data. "
    "It can chain multiple tools (data fetch -> analysis -> trade execution) "
    "and retains trading strategy preferences across sessions."
)

PROMPT_TEMPLATE = """You are a security engineer defining monitoring rules for an agentic AI system.

System description:
{description}

For each of the 6 anomaly categories below, define 3 monitoring metrics with baselines and thresholds.

Categories:
1. Authorization Anomalies (denial rates, purpose inconsistency, escalation attempts)
2. Tool Usage Anomalies (call frequency, unusual combinations, parameter patterns)
3. Data Access Anomalies (volume, timing, scope violations)
4. Reasoning Pattern Changes (depth, goal alignment, phantom instructions)
5. Output Characteristic Changes (style, quality, information leaks)
6. Memory Access Patterns (unrelated retrievals, write rates, repeated access)

For each metric provide:
- metric: short snake_case name
- description: what it measures
- baseline: normal value for this system
- threshold_warning: when to alert (warning level)
- threshold_critical: when to alert (critical level)
- action: what the operator should do

Return ONLY valid JSON as an object with keys for each category, each containing an array of 3 metric objects. No markdown fences, no explanation.

Structure:
{{"authorization": [{{"metric": "...", "description": "...", "baseline": N, "threshold_warning": N, "threshold_critical": N, "action": "..."}}], "tool_usage": [...], ...}}"""


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


def parse_spec(raw: str) -> dict | None:
    """Parse LLM response into dashboard spec."""
    text = raw.strip()
    if text.startswith("[") and "opencode error" in text:
        print(f"    [ERROR] LLM call failed: {text[:80]}")
        return None

    try:
        spec = json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip("`").removeprefix("json").strip()
        try:
            spec = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"    [ERROR] Could not parse JSON: {text[:80]}")
            return None

    if not isinstance(spec, dict):
        print(f"    [ERROR] Expected object, got {type(spec).__name__}")
        return None

    return spec


def generate_dashboard_spec(description: str) -> dict | None:
    """Generate monitoring dashboard spec via LLM."""
    prompt = PROMPT_TEMPLATE.format(description=description)
    print("  Calling LLM for monitoring spec...")
    raw = ask_llm(prompt)
    return parse_spec(raw)


def validate_spec(spec: dict) -> list[str]:
    """Validate generated spec structure."""
    issues = []
    for cat in CATEGORIES:
        if cat not in spec:
            issues.append(f"missing category: {cat}")
            continue
        metrics = spec[cat]
        if not isinstance(metrics, list):
            issues.append(f"{cat}: expected array, got {type(metrics).__name__}")
            continue
        for m in metrics:
            for field in ["metric", "baseline", "threshold_warning", "threshold_critical"]:
                if field not in m:
                    issues.append(f"{cat}/{m.get('metric', '?')}: missing {field}")
    return issues


# ---------- Display Functions ----------


def progress_bar(pct: float, width: int = 15) -> str:
    """Generate ASCII progress bar."""
    filled = int(pct / 100 * width)
    empty = width - filled
    return f"[{'#' * filled}{'.' * empty}] {pct:.0f}%"


def print_llm_spec(spec: dict) -> None:
    """Print LLM-generated dashboard spec."""
    print("=" * 70)
    print("  LLM-GENERATED MONITORING SPEC")
    print("=" * 70)

    for cat_id, cat_label in CATEGORIES.items():
        metrics = spec.get(cat_id, [])
        print(f"\n  {cat_label} ({len(metrics)} metrics)")
        print("  " + "-" * 55)

        for m in metrics:
            print(f"    {m.get('metric', '?')}")
            print(f"      Baseline:    {m.get('baseline', '?')}")
            print(f"      Warning:     {m.get('threshold_warning', '?')}")
            print(f"      Critical:    {m.get('threshold_critical', '?')}")
            action = textwrap.fill(m.get("action", ""), width=50, initial_indent="      Action:      ", subsequent_indent="                   ")
            print(action)
            print()


def print_validation(issues: list[str]) -> None:
    """Print validation results."""
    print("=" * 70)
    print("  VALIDATION")
    print("=" * 70)

    if not issues:
        print("\n  All checks passed -- spec is valid.\n")
    else:
        print(f"\n  {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"    - {issue}")
        print()


def print_comparison_table(spec: dict) -> None:
    """Print comparison with hardcoded baseline."""
    print("=" * 70)
    print("  LLM vs HARDCODED BASELINE")
    print("=" * 70)

    print(f"\n  {'Category':<30} {'LLM Metrics':<15} {'Baseline':<15}")
    print("  " + "-" * 60)

    for cat_id, cat_label in CATEGORIES.items():
        llm_count = len(spec.get(cat_id, []))
        print(f"  {cat_label:<30} {llm_count:<15} {3:<15}")

    print()


def print_simulation(spec: dict) -> None:
    """Quick simulation using LLM thresholds."""
    print("=" * 70)
    print("  QUICK SIMULATION: Normal Operation")
    print("=" * 70)

    total = 0
    fired = 0
    for cat_id, metrics in spec.items():
        for m in metrics:
            total += 1
            baseline = m.get("baseline", 0)
            warn = m.get("threshold_warning", 999)
            crit = m.get("threshold_critical", 999)
            # Check if baseline is within warning threshold
            if isinstance(baseline, (int, float)) and isinstance(warn, (int, float)):
                if "low" in m.get("metric", ""):
                    # Low-is-bad metric
                    if baseline < warn:
                        fired += 1
                else:
                    if baseline >= warn:
                        fired += 1

    pct = ((total - fired) / total * 100) if total > 0 else 100
    print(f"\n  Metrics at baseline: {total - fired}/{total} ({pct:.0f}% within thresholds)")
    print(f"  Alerts at baseline:  {fired if fired > 0 else 0}")
    print(f"  Health: {progress_bar(pct)}")
    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 8 -- What to Watch For")
    print("  LLM Monitoring Dashboard Generator")
    print("=" * 70)
    print(f"  Model:   {MODEL}")
    print(f"  Timeout: {LLM_TIMEOUT}s per call")
    print("=" * 70 + "\n")

    print("  System Description:")
    desc_lines = textwrap.wrap(SAMPLE_DESCRIPTION, width=60)
    for line in desc_lines:
        print(f"    {line}")
    print()

    spec = generate_dashboard_spec(SAMPLE_DESCRIPTION)

    if spec:
        issues = validate_spec(spec)
        print_validation(issues)
        print_llm_spec(spec)
        print_comparison_table(spec)
        print_simulation(spec)
    else:
        print("  Failed to generate spec.\n")

    # JSON export
    json_output = {
        "model": MODEL,
        "system_description": SAMPLE_DESCRIPTION,
        "spec": spec,
        "validation_issues": validate_spec(spec) if spec else [],
    }
    json_path = "monitoring_dashboard_llm.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON spec written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "LLM-generated monitoring specs provide a fast starting point for security "
        "operations. The LLM can suggest baselines and thresholds based on the "
        "system description, but these must be validated against real operational "
        "data and tuned based on actual false positive rates in production.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
