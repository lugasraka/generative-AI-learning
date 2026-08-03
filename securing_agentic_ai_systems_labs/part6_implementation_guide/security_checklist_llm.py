"""
Part 6 -- Implementation Guide: LLM-Powered Security Checklist Generator

Uses opencode LLM to auto-fill a pre-deployment security checklist for
a given agent system description. Simulates a realistic security review
workflow where an LLM suggests which controls apply and their status.

Run:  python security_checklist_llm.py
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
    "identity": "Identity & Authentication",
    "permissions": "Authorization & Access Control",
    "containment": "Containment Controls",
    "logging": "Tamper-Resistant Logging",
    "testing": "Vulnerability Testing",
}

ALL_CONTROLS = [
    {"id": "ID-01", "name": "Unique Agent Identity", "category": "identity", "priority": "must-have"},
    {"id": "ID-02", "name": "Short-Lived Certificates", "category": "identity", "priority": "must-have"},
    {"id": "ID-03", "name": "Hardware Security Module (HSM)", "category": "identity", "priority": "should-have"},
    {"id": "ID-04", "name": "Workload Identity Federation", "category": "identity", "priority": "should-have"},
    {"id": "ID-05", "name": "Identity Audit Trail", "category": "identity", "priority": "must-have"},
    {"id": "PM-01", "name": "Role-Based Access Control (RBAC)", "category": "permissions", "priority": "must-have"},
    {"id": "PM-02", "name": "Attribute-Based Access Control (ABAC)", "category": "permissions", "priority": "should-have"},
    {"id": "PM-03", "name": "On-Behalf-Of (OBO) Flow", "category": "permissions", "priority": "must-have"},
    {"id": "PM-04", "name": "Least Privilege Enforcement", "category": "permissions", "priority": "must-have"},
    {"id": "PM-05", "name": "Tool Scope Validation", "category": "permissions", "priority": "must-have"},
    {"id": "CT-01", "name": "Purpose Binding", "category": "containment", "priority": "must-have"},
    {"id": "CT-02", "name": "Kill-Switch Capability", "category": "containment", "priority": "must-have"},
    {"id": "CT-03", "name": "Resource Usage Caps", "category": "containment", "priority": "must-have"},
    {"id": "CT-04", "name": "Circuit Breakers", "category": "containment", "priority": "should-have"},
    {"id": "CT-05", "name": "Sandboxed Execution", "category": "containment", "priority": "should-have"},
    {"id": "LG-01", "name": "Structured Log Format", "category": "logging", "priority": "must-have"},
    {"id": "LG-02", "name": "Comprehensive Log Coverage", "category": "logging", "priority": "must-have"},
    {"id": "LG-03", "name": "Cryptographic Log Signing", "category": "logging", "priority": "should-have"},
    {"id": "LG-04", "name": "Immutable Log Storage", "category": "logging", "priority": "should-have"},
    {"id": "LG-05", "name": "Real-Time Log Replication", "category": "logging", "priority": "nice-to-have"},
    {"id": "TS-01", "name": "Red Team Exercises", "category": "testing", "priority": "must-have"},
    {"id": "TS-02", "name": "Automated Vulnerability Scanning", "category": "testing", "priority": "must-have"},
    {"id": "TS-03", "name": "Adversarial Prompt Library", "category": "testing", "priority": "should-have"},
    {"id": "TS-04", "name": "Quarterly Security Validation", "category": "testing", "priority": "should-have"},
    {"id": "TS-05", "name": "CI/CD Security Gates", "category": "testing", "priority": "must-have"},
]

SAMPLE_DESCRIPTION = (
    "A customer support chatbot that handles user inquiries, looks up order "
    "status, processes refunds up to $500, and sends emails. It has access to "
    "the order database, CRM system, email API, and knowledge base. It retains "
    "conversation history across sessions and can chain multiple tools in a "
    "single interaction."
)

PROMPT_TEMPLATE = """You are a security engineer reviewing an agentic AI system for pre-deployment readiness.

System description:
{description}

For each of the 25 security controls below, assess whether it applies to this system and suggest an estimated implementation status.

Controls to assess:
{controls_list}

Return a JSON array of objects, each with:
- id: the control ID (e.g., "ID-01")
- applicable: true/false (does this control apply to this system?)
- status: one of "not-started", "in-progress", "done", "verified"
- rationale: brief reason for the suggested status

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


def parse_suggestions(raw: str) -> list[dict] | None:
    """Parse LLM response into suggestions list."""
    text = raw.strip()
    if text.startswith("[") and "opencode error" in text:
        print(f"    [ERROR] LLM call failed: {text[:80]}")
        return None

    try:
        suggestions = json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip("`").removeprefix("json").strip()
        try:
            suggestions = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"    [ERROR] Could not parse JSON: {text[:80]}")
            return None

    if not isinstance(suggestions, list):
        print(f"    [ERROR] Expected array, got {type(suggestions).__name__}")
        return None

    return suggestions


def generate_suggestions(description: str) -> list[dict]:
    """Generate security checklist suggestions via LLM."""
    controls_list = "\n".join(
        f"- {c['id']}: {c['name']} (category: {c['category']}, priority: {c['priority']})"
        for c in ALL_CONTROLS
    )

    prompt = PROMPT_TEMPLATE.format(
        description=description,
        controls_list=controls_list,
    )

    print("  Calling LLM for security assessment...")
    raw = ask_llm(prompt)
    suggestions = parse_suggestions(raw)

    if not suggestions:
        return []

    # Merge with control definitions
    results = []
    sug_map = {s.get("id", ""): s for s in suggestions if isinstance(s, dict)}

    for control in ALL_CONTROLS:
        sug = sug_map.get(control["id"], {})
        results.append({
            **control,
            "applicable": sug.get("applicable", True),
            "status": sug.get("status", "not-started"),
            "rationale": sug.get("rationale", "No rationale provided"),
        })

    return results


def calculate_readiness(results: list[dict]) -> dict:
    """Calculate readiness score from suggestions."""
    applicable = [r for r in results if r.get("applicable", True)]
    if not applicable:
        return {"score": 0, "verdict": "NO-GO", "applicable": 0, "done": 0}

    weight_map = {"must-have": 3, "should-have": 1, "nice-to-have": 0.5}
    total_w = sum(weight_map.get(r["priority"], 1) for r in applicable)
    done_w = sum(
        weight_map.get(r["priority"], 1)
        for r in applicable
        if r.get("status") in ("done", "verified")
    )
    score = (done_w / total_w * 100) if total_w > 0 else 0

    if score >= 90:
        verdict = "GO"
    elif score >= 70:
        verdict = "CONDITIONAL"
    else:
        verdict = "NO-GO"

    return {
        "score": score,
        "verdict": verdict,
        "applicable": len(applicable),
        "done": sum(1 for r in applicable if r.get("status") in ("done", "verified")),
    }


# ---------- Display Functions ----------


def progress_bar(pct: float, width: int = 20) -> str:
    """Generate ASCII progress bar."""
    filled = int(pct / 100 * width)
    empty = width - filled
    return f"[{'#' * filled}{'.' * empty}] {pct:.0f}%"


def print_suggestions(results: list[dict]) -> None:
    """Print all suggested controls."""
    print("=" * 70)
    print("  LLM-GENERATED SECURITY CHECKLIST")
    print("=" * 70)

    for cat_id, cat_label in CATEGORIES.items():
        items = [r for r in results if r["category"] == cat_id]
        applicable = [r for r in items if r.get("applicable", True)]
        print(f"\n  {cat_label} ({len(applicable)}/{len(items)} applicable)")
        print("  " + "-" * 55)

        for r in items:
            if not r.get("applicable", True):
                print(f"    [--] [{r['id']}] {r['name']:<35} NOT APPLICABLE")
                continue

            status = r.get("status", "not-started")
            marker = {"not-started": "[ ]", "in-progress": "[~]", "done": "[x]", "verified": "[V]"}.get(status, "[ ]")
            pri = r["priority"][:4].upper()
            print(f"    {marker} [{r['id']}] {r['name']:<35} [{pri}]")
            rationale = textwrap.fill(r.get("rationale", ""), width=55, initial_indent="         ", subsequent_indent="         ")
            print(rationale)

    print()


def print_readiness(results: list[dict]) -> None:
    """Print readiness assessment."""
    print("=" * 70)
    print("  READINESS ASSESSMENT")
    print("=" * 70)

    readiness = calculate_readiness(results)
    print(f"\n  Score: {readiness['score']:.1f}/100")
    print(f"  Verdict: {readiness['verdict']}")
    print(f"  Applicable Controls: {readiness['applicable']}")
    print(f"  Completed: {readiness['done']}/{readiness['applicable']}")

    # Per-category breakdown
    print("\n  Category Breakdown:")
    for cat_id, cat_label in CATEGORIES.items():
        items = [r for r in results if r["category"] == cat_id and r.get("applicable", True)]
        if not items:
            continue
        done = sum(1 for r in items if r.get("status") in ("done", "verified"))
        pct = (done / len(items) * 100) if items else 0
        print(f"    {cat_label:<35} {progress_bar(pct, 15)}  {done}/{len(items)}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 6 -- Implementation Guide")
    print("  LLM-Powered Security Checklist Generator")
    print("=" * 70)
    print(f"  Model:   {MODEL}")
    print(f"  Timeout: {LLM_TIMEOUT}s per call")
    print("=" * 70 + "\n")

    print("  System Description:")
    desc_lines = textwrap.wrap(SAMPLE_DESCRIPTION, width=60)
    for line in desc_lines:
        print(f"    {line}")
    print()

    results = generate_suggestions(SAMPLE_DESCRIPTION)

    if results:
        print_suggestions(results)
        print_readiness(results)
    else:
        print("  No suggestions generated.\n")

    json_output = {
        "model": MODEL,
        "system_description": SAMPLE_DESCRIPTION,
        "suggestions": results,
        "readiness": calculate_readiness(results) if results else None,
    }
    json_path = "security_checklist_llm.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON checklist written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "LLM-generated checklists provide a fast starting point for security reviews, "
        "but require human validation. The LLM can suggest applicable controls and "
        "estimate status, but the actual implementation status must be verified by "
        "the engineering team with hands-on knowledge of the system.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
