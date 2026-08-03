"""
Part 6 -- Implementation Guide: Pre-Deployment Security Checklist

Tracks 25 security controls across 5 categories (identity, permissions,
containment, logging, testing). Calculates completion percentages,
identifies overdue items, and generates a readiness score for production.

Run:  python security_checklist.py
"""

import json
import sys
import textwrap
from datetime import datetime, timedelta

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

CATEGORIES = {
    "identity": "Identity & Authentication",
    "permissions": "Authorization & Access Control",
    "containment": "Containment Controls",
    "logging": "Tamper-Resistant Logging",
    "testing": "Vulnerability Testing",
}

PRIORITIES = {
    "must-have": {"weight": 3, "label": "Must-Have"},
    "should-have": {"weight": 1, "label": "Should-Have"},
    "nice-to-have": {"weight": 0.5, "label": "Nice-to-Have"},
}

STATUSES = {
    "not-started": {"label": "Not Started", "marker": "[ ]"},
    "in-progress": {"label": "In Progress", "label_short": "[~]", "marker": "[~]"},
    "done": {"label": "Done", "marker": "[x]"},
    "verified": {"label": "Verified", "marker": "[V]"},
}

TODAY = datetime.now().strftime("%Y-%m-%d")


# ---------- Security Controls Checklist ----------

CHECKLIST: list[dict] = [
    # --- Identity (5) ---
    {
        "id": "ID-01",
        "name": "Unique Agent Identity",
        "description": "Every agent has its own unique identity. No shared accounts or reused identities.",
        "category": "identity",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-01",
    },
    {
        "id": "ID-02",
        "name": "Short-Lived Certificates",
        "description": "Agent authentication uses certificates with limited lifespans (hours to days, not months).",
        "category": "identity",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-05",
    },
    {
        "id": "ID-03",
        "name": "Hardware Security Module (HSM)",
        "description": "Critical key material stored in tamper-resistant hardware. Private keys never exist outside HSM.",
        "category": "identity",
        "priority": "should-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-15",
    },
    {
        "id": "ID-04",
        "name": "Workload Identity Federation",
        "description": "Just-in-time credentials instead of long-lived secrets. Cross-cloud support.",
        "category": "identity",
        "priority": "should-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-08-20",
    },
    {
        "id": "ID-05",
        "name": "Identity Audit Trail",
        "description": "All agent identity operations logged: creation, rotation, revocation, authentication events.",
        "category": "identity",
        "priority": "must-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-10",
    },
    # --- Permissions (5) ---
    {
        "id": "PM-01",
        "name": "Role-Based Access Control (RBAC)",
        "description": "Agents assigned roles mapped to purposes with minimum necessary permissions.",
        "category": "permissions",
        "priority": "must-have",
        "status": "done",
        "owner": "Security Team",
        "due_date": "2026-08-01",
    },
    {
        "id": "PM-02",
        "name": "Attribute-Based Access Control (ABAC)",
        "description": "Multi-attribute decisions: identity, resource properties, environment, action context.",
        "category": "permissions",
        "priority": "should-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-18",
    },
    {
        "id": "PM-03",
        "name": "On-Behalf-Of (OBO) Flow",
        "description": "Delegated permissions: agent operates with intersection of its capabilities and user's access rights.",
        "category": "permissions",
        "priority": "must-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-08-22",
    },
    {
        "id": "PM-04",
        "name": "Least Privilege Enforcement",
        "description": "API-level, data-level, and tool-level permissions scoped to minimum required.",
        "category": "permissions",
        "priority": "must-have",
        "status": "done",
        "owner": "Security Team",
        "due_date": "2026-08-01",
    },
    {
        "id": "PM-05",
        "name": "Tool Scope Validation",
        "description": "Every tool invocation validated against agent's authorized tool list before execution.",
        "category": "permissions",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-03",
    },
    # --- Containment (5) ---
    {
        "id": "CT-01",
        "name": "Purpose Binding",
        "description": "Agents cryptographically bound to specific purposes via signed configuration files.",
        "category": "containment",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-01",
    },
    {
        "id": "CT-02",
        "name": "Kill-Switch Capability",
        "description": "Immediate termination of agent operations. Separate from agent infrastructure.",
        "category": "containment",
        "priority": "must-have",
        "status": "done",
        "owner": "Security Team",
        "due_date": "2026-08-05",
    },
    {
        "id": "CT-03",
        "name": "Resource Usage Caps",
        "description": "API call limits, data access volume caps, computation budgets, tool invocation frequency limits.",
        "category": "containment",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-03",
    },
    {
        "id": "CT-04",
        "name": "Circuit Breakers",
        "description": "Three-state system: Closed (normal), Open (suspended), Half-Open (gradual restoration).",
        "category": "containment",
        "priority": "should-have",
        "status": "in-progress",
        "owner": "Platform Team",
        "due_date": "2026-08-12",
    },
    {
        "id": "CT-05",
        "name": "Sandboxed Execution",
        "description": "Agent operations run in isolated environments with restricted access to sensitive resources.",
        "category": "containment",
        "priority": "should-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-08-25",
    },
    # --- Logging (5) ---
    {
        "id": "LG-01",
        "name": "Structured Log Format",
        "description": "All logs in structured format (JSON). Each entry: event type, timestamp, agent ID, trace ID, severity.",
        "category": "logging",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-01",
    },
    {
        "id": "LG-02",
        "name": "Comprehensive Log Coverage",
        "description": "Log inputs, reasoning chains, tool calls, permission decisions, safety events, and outputs.",
        "category": "logging",
        "priority": "must-have",
        "status": "done",
        "owner": "Platform Team",
        "due_date": "2026-08-05",
    },
    {
        "id": "LG-03",
        "name": "Cryptographic Log Signing",
        "description": "Hash chain where modifying one entry invalidates all subsequent entries.",
        "category": "logging",
        "priority": "should-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-20",
    },
    {
        "id": "LG-04",
        "name": "Immutable Log Storage",
        "description": "Append-only storage (S3 Object Lock, Azure Immutable Blob, GCP Retention Policies).",
        "category": "logging",
        "priority": "should-have",
        "status": "not-started",
        "owner": "Security Team",
        "due_date": "2026-08-25",
    },
    {
        "id": "LG-05",
        "name": "Real-Time Log Replication",
        "description": "Logs replicated to multiple destinations concurrently for redundancy.",
        "category": "logging",
        "priority": "nice-to-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-09-01",
    },
    # --- Testing (5) ---
    {
        "id": "TS-01",
        "name": "Red Team Exercises",
        "description": "Regular adversarial testing: prompt injection, memory poisoning, tool exploitation, goal hijacking.",
        "category": "testing",
        "priority": "must-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-15",
    },
    {
        "id": "TS-02",
        "name": "Automated Vulnerability Scanning",
        "description": "CI/CD integration: AI security testing platforms, adversarial prompt libraries.",
        "category": "testing",
        "priority": "must-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-08-20",
    },
    {
        "id": "TS-03",
        "name": "Adversarial Prompt Library",
        "description": "Maintained library of attack prompts for regular testing against all known vectors.",
        "category": "testing",
        "priority": "should-have",
        "status": "in-progress",
        "owner": "Security Team",
        "due_date": "2026-08-18",
    },
    {
        "id": "TS-04",
        "name": "Quarterly Security Validation",
        "description": "Repeat red team exercises, update libraries, review controls, test containment quarterly.",
        "category": "testing",
        "priority": "should-have",
        "status": "not-started",
        "owner": "Security Team",
        "due_date": "2026-08-25",
    },
    {
        "id": "TS-05",
        "name": "CI/CD Security Gates",
        "description": "Security checks block deployment on failure. Integration with pipeline.",
        "category": "testing",
        "priority": "must-have",
        "status": "not-started",
        "owner": "Platform Team",
        "due_date": "2026-08-22",
    },
]


# ---------- Core Functions ----------


def calculate_category_completion(category: str) -> float:
    """Calculate completion percentage for a category."""
    items = [c for c in CHECKLIST if c["category"] == category]
    if not items:
        return 0.0
    done = sum(1 for c in items if c["status"] in ("done", "verified"))
    return (done / len(items)) * 100


def calculate_overall_completion() -> float:
    """Calculate overall completion percentage."""
    if not CHECKLIST:
        return 0.0
    done = sum(1 for c in CHECKLIST if c["status"] in ("done", "verified"))
    return (done / len(CHECKLIST)) * 100


def find_overdue_items() -> list[dict]:
    """Find controls past their due date."""
    today = datetime.strptime(TODAY, "%Y-%m-%d")
    overdue = []
    for c in CHECKLIST:
        due = datetime.strptime(c["due_date"], "%Y-%m-%d")
        if due < today and c["status"] not in ("done", "verified"):
            days = (today - due).days
            overdue.append({**c, "days_overdue": days})
    overdue.sort(key=lambda x: x["days_overdue"], reverse=True)
    return overdue


def calculate_readiness_score() -> dict:
    """Calculate weighted readiness score."""
    total_weight = 0
    completed_weight = 0
    for c in CHECKLIST:
        w = PRIORITIES[c["priority"]]["weight"]
        total_weight += w
        if c["status"] in ("done", "verified"):
            completed_weight += w

    score = (completed_weight / total_weight * 100) if total_weight > 0 else 0

    if score >= 90:
        verdict = "GO"
        verdict_desc = "Ready for production deployment"
    elif score >= 70:
        verdict = "CONDITIONAL"
        verdict_desc = "Proceed with caution, address must-have gaps first"
    else:
        verdict = "NO-GO"
        verdict_desc = "Not ready -- critical controls missing"

    # Per-category breakdown
    cat_scores = {}
    for cat in CATEGORIES:
        items = [c for c in CHECKLIST if c["category"] == cat]
        cat_weight = sum(PRIORITIES[c["priority"]]["weight"] for c in items)
        cat_done = sum(PRIORITIES[c["priority"]]["weight"] for c in items if c["status"] in ("done", "verified"))
        cat_scores[cat] = (cat_done / cat_weight * 100) if cat_weight > 0 else 0

    return {
        "score": score,
        "verdict": verdict,
        "verdict_desc": verdict_desc,
        "total_weight": total_weight,
        "completed_weight": completed_weight,
        "category_scores": cat_scores,
    }


def get_next_actions() -> list[dict]:
    """Get prioritized next actions."""
    actions = []
    for c in CHECKLIST:
        if c["status"] not in ("done", "verified"):
            actions.append(c)

    # Sort: must-have first, then by due date
    actions.sort(key=lambda x: (
        0 if x["priority"] == "must-have" else (1 if x["priority"] == "should-have" else 2),
        x["due_date"],
    ))
    return actions[:5]


# ---------- Display Functions ----------


def progress_bar(pct: float, width: int = 20) -> str:
    """Generate ASCII progress bar."""
    filled = int(pct / 100 * width)
    empty = width - filled
    return f"[{'#' * filled}{'.' * empty}] {pct:.0f}%"


def print_dashboard() -> None:
    """Print overall dashboard."""
    print("=" * 70)
    print("  PRE-DEPLOYMENT SECURITY DASHBOARD")
    print("=" * 70)
    print(f"  Date: {TODAY}")
    print(f"  Total Controls: {len(CHECKLIST)}")
    print()

    overall = calculate_overall_completion()
    print(f"  Overall Progress: {progress_bar(overall, 30)}")
    print()

    print("  Per-Category Breakdown:")
    print("  " + "-" * 55)
    for cat_id, cat_label in CATEGORIES.items():
        pct = calculate_category_completion(cat_id)
        count = sum(1 for c in CHECKLIST if c["category"] == cat_id)
        done = sum(1 for c in CHECKLIST if c["category"] == cat_id and c["status"] in ("done", "verified"))
        print(f"  {cat_label:<35} {progress_bar(pct, 15)}  {done}/{count}")

    print()


def print_category_breakdown() -> None:
    """Print detailed per-category view."""
    print("=" * 70)
    print("  CONTROL STATUS BY CATEGORY")
    print("=" * 70)

    for cat_id, cat_label in CATEGORIES.items():
        items = [c for c in CHECKLIST if c["category"] == cat_id]
        pct = calculate_category_completion(cat_id)
        print(f"\n  {cat_label} ({pct:.0f}% complete)")
        print("  " + "-" * 55)

        for c in items:
            marker = STATUSES[c["status"]]["marker"]
            pri = c["priority"][:4].upper()
            due = c["due_date"]
            print(f"    {marker} [{c['id']}] {c['name']:<35} [{pri}] Due: {due}")

    print()


def print_overdue_report() -> None:
    """Print overdue items."""
    print("=" * 70)
    print("  OVERDUE ITEMS")
    print("=" * 70)

    overdue = find_overdue_items()
    if not overdue:
        print("\n  No overdue items.\n")
        return

    for item in overdue:
        print(f"\n  [{item['id']}] {item['name']}")
        print(f"    Category:  {CATEGORIES[item['category']]}")
        print(f"    Priority:  {PRIORITIES[item['priority']]['label']}")
        print(f"    Owner:     {item['owner']}")
        print(f"    Due:       {item['due_date']} ({item['days_overdue']} days overdue)")
        print(f"    Status:    {STATUSES[item['status']]['label']}")

    print(f"\n  Total overdue: {len(overdue)}")
    print()


def print_next_actions() -> None:
    """Print next actions."""
    print("=" * 70)
    print("  NEXT ACTIONS (Top 5)")
    print("=" * 70)

    actions = get_next_actions()
    for i, a in enumerate(actions, 1):
        print(f"\n  {i}. [{a['id']}] {a['name']}")
        print(f"     Priority: {PRIORITIES[a['priority']]['label']}")
        print(f"     Owner:    {a['owner']}")
        print(f"     Due:      {a['due_date']}")
        desc = textwrap.fill(a["description"], width=55, initial_indent="     ", subsequent_indent="     ")
        print(desc)

    print()


def print_readiness_score() -> None:
    """Print readiness score."""
    print("=" * 70)
    print("  READINESS SCORE")
    print("=" * 70)

    result = calculate_readiness_score()
    score = result["score"]

    print(f"\n  Score: {score:.1f}/100")
    print(f"  Verdict: {result['verdict']} -- {result['verdict_desc']}")
    print()

    print("  Category Breakdown:")
    for cat_id, cat_label in CATEGORIES.items():
        cat_pct = result["category_scores"][cat_id]
        print(f"    {cat_label:<35} {progress_bar(cat_pct, 15)}")

    print()
    must_haves = [c for c in CHECKLIST if c["priority"] == "must-have"]
    must_done = sum(1 for c in must_haves if c["status"] in ("done", "verified"))
    print(f"  Must-Have Controls: {must_done}/{len(must_haves)} complete")

    if result["verdict"] == "NO-GO":
        missing = [c for c in must_haves if c["status"] not in ("done", "verified")]
        print("  Critical missing controls:")
        for c in missing:
            print(f"    - [{c['id']}] {c['name']}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 6 -- Implementation Guide")
    print("  Pre-Deployment Security Checklist Tracker")
    print("=" * 70 + "\n")

    print_dashboard()
    print_category_breakdown()
    print_overdue_report()
    print_next_actions()
    print_readiness_score()

    # JSON export
    json_output = {
        "date": TODAY,
        "controls": CHECKLIST,
        "overall_completion": calculate_overall_completion(),
        "category_completion": {cat: calculate_category_completion(cat) for cat in CATEGORIES},
        "overdue": find_overdue_items(),
        "readiness": calculate_readiness_score(),
    }
    json_path = "security_checklist.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON checklist written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "Enforcement must be external to the agent -- don't rely on self-policing. "
        "The kill-switch system must be separate from agent infrastructure. "
        "Quarterly security validation is the minimum for production agents.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
