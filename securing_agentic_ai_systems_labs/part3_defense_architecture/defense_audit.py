"""
Part 3 — Defense Architecture: Three-Pillar Audit

Audits 2 agent systems against the three-pillar defense framework
(Guardrails, Permissions, Auditability). Scores each sub-item 1-5,
identifies weakest pillars, generates prioritized remediation lists,
and analyzes the governance-containment gap.

Run:  python defense_audit.py
"""

import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

PILLARS = {
    "guardrails": {
        "label": "Guardrails",
        "description": "Preventing harmful behavior",
        "sub_items": [
            ("input_validation", "Input Validation & Sanitization"),
            ("output_filtering", "Output Filtering & Redaction"),
            ("sandboxing", "Sandboxed Execution"),
            ("tool_validation", "Tool/Function Call Validation"),
            ("content_filters", "Content Safety Filters"),
        ],
    },
    "permissions": {
        "label": "Permissions",
        "description": "Defining authority boundaries",
        "sub_items": [
            ("unique_identity", "Unique Agent Identity"),
            ("short_lived_credentials", "Short-Lived Credentials"),
            ("least_privilege", "Least Privilege Enforcement"),
            ("obo_flow", "On-Behalf-Of (OBO) Flow"),
        ],
    },
    "auditability": {
        "label": "Auditability",
        "description": "Ensuring traceability",
        "sub_items": [
            ("comprehensive_logging", "Comprehensive Logging"),
            ("tamper_resistant", "Tamper-Resistant Logs"),
            ("immutable_storage", "Immutable Storage"),
            ("real_time_alerts", "Real-Time Alerting"),
        ],
    },
}

SCORE_MEANING = {
    1: "Not implemented",
    2: "Partial / ad-hoc",
    3: "Basic",
    4: "Comprehensive",
    5: "Best-in-class",
}

CONTAINMENT_ITEMS = [
    ("purpose_binding", "Purpose Binding", "Agent cryptographically bound to specific use cases"),
    ("kill_switch", "Kill-Switch Capability", "Immediate termination of agent operations"),
    ("resource_caps", "Resource Usage Caps", "Defined resource boundaries with auto-enforcement"),
    ("circuit_breakers", "Circuit Breakers", "Automated suspension on anomalous patterns"),
]


# ---------- Agent System Definitions ----------

AGENT_SYSTEMS: list[dict] = [
    {
        "name": "Healthcare Triage Agent",
        "risk_profile": "HIGH -- handles PHI, influences medical decisions",
        "purpose": (
            "Triages patient symptoms via chat, recommends urgency levels, "
            "schedules appointments, and flags critical cases to human staff. "
            "Accesses electronic health records (EHR) and scheduling systems."
        ),
        "audit_scores": {
            "guardrails": {
                "input_validation": 4,
                "output_filtering": 5,
                "sandboxing": 3,
                "tool_validation": 4,
                "content_filters": 4,
            },
            "permissions": {
                "unique_identity": 5,
                "short_lived_credentials": 4,
                "least_privilege": 3,
                "obo_flow": 2,
            },
            "auditability": {
                "comprehensive_logging": 5,
                "tamper_resistant": 4,
                "immutable_storage": 3,
                "real_time_alerts": 4,
            },
        },
        "containment": {
            "purpose_binding": True,
            "kill_switch": True,
            "resource_caps": True,
            "circuit_breakers": False,
        },
    },
    {
        "name": "Internal Wiki Search Agent",
        "risk_profile": "LOW -- read-only access, no PII, internal use only",
        "purpose": (
            "Searches internal company wiki, generates summaries, and answers "
            "employee questions about policies and procedures. Read-only access "
            "to documentation; no write or external API permissions."
        ),
        "audit_scores": {
            "guardrails": {
                "input_validation": 3,
                "output_filtering": 2,
                "sandboxing": 2,
                "tool_validation": 3,
                "content_filters": 2,
            },
            "permissions": {
                "unique_identity": 2,
                "short_lived_credentials": 1,
                "least_privilege": 4,
                "obo_flow": 1,
            },
            "auditability": {
                "comprehensive_logging": 2,
                "tamper_resistant": 1,
                "immutable_storage": 1,
                "real_time_alerts": 2,
            },
        },
        "containment": {
            "purpose_binding": False,
            "kill_switch": False,
            "resource_caps": True,
            "circuit_breakers": False,
        },
    },
]


# ---------- Analysis Functions ----------


def calculate_pillar_scores(audit_scores: dict) -> dict[str, float]:
    """Calculate average score for each pillar."""
    scores = {}
    for pillar_id, data in PILLARS.items():
        items = audit_scores.get(pillar_id, {})
        values = list(items.values())
        scores[pillar_id] = sum(values) / len(values) if values else 0.0
    return scores


def find_weakest_pillar(pillar_scores: dict[str, float]) -> tuple[str, float]:
    """Find the pillar with the lowest average score."""
    weakest = min(pillar_scores, key=lambda k: pillar_scores[k])
    return weakest, pillar_scores[weakest]


def find_strongest_pillar(pillar_scores: dict[str, float]) -> tuple[str, float]:
    """Find the pillar with the highest average score."""
    strongest = max(pillar_scores, key=lambda k: pillar_scores[k])
    return strongest, pillar_scores[strongest]


def build_remediation_list(audit_scores: dict, pillar_scores: dict[str, float]) -> list[dict]:
    """Build prioritized remediation list: low-scoring sub-items first."""
    items = []
    for pillar_id, data in PILLARS.items():
        for sub_id, sub_label in data["sub_items"]:
            score = audit_scores.get(pillar_id, {}).get(sub_id, 0)
            items.append({
                "pillar": data["label"],
                "sub_item": sub_label,
                "score": score,
                "priority": "CRITICAL" if score <= 2 else ("HIGH" if score == 3 else "MEDIUM"),
            })
    items.sort(key=lambda x: (x["score"], x["priority"] != "CRITICAL"))
    return items


def assess_governance_gap(containment: dict) -> dict:
    """Assess the governance-containment gap."""
    implemented = sum(1 for v in containment.values() if v)
    total = len(containment)
    has_monitoring = implemented > 0
    has_full_containment = implemented == total
    gap_type = "none" if has_full_containment else ("partial" if has_monitoring else "severe")

    return {
        "items": [
            {"name": label, "implemented": containment.get(item_id, False), "description": desc}
            for item_id, label, desc in CONTAINMENT_ITEMS
        ],
        "implemented_count": implemented,
        "total": total,
        "gap_type": gap_type,
        "assessment": (
            "Full containment in place."
            if gap_type == "none"
            else (
                f"Governance-containment gap: {implemented}/{total} controls active. "
                + ("Organization can monitor but may not be able to stop the agent."
                   if gap_type == "partial"
                   else "No containment controls -- agent cannot be stopped if compromised.")
            )
        ),
    }


# ---------- Display Functions ----------


def score_bar(score: int, max_score: int = 5) -> str:
    """Generate ASCII score bar."""
    filled = score
    empty = max_score - score
    return f"[{'#' * filled}{'.' * empty}] {score}/{max_score}"


def print_pillar_breakdown(name: str, audit_scores: dict) -> None:
    """Print detailed sub-item breakdown for each pillar."""
    print("=" * 70)
    print(f"  AUDIT BREAKDOWN: {name.upper()}")
    print("=" * 70)

    for pillar_id, data in PILLARS.items():
        print(f"\n  {data['label']} ({data['description']})")
        print("  " + "-" * 50)
        items = audit_scores.get(pillar_id, {})
        for sub_id, sub_label in data["sub_items"]:
            score = items.get(sub_id, 0)
            meaning = SCORE_MEANING.get(score, "?")
            print(f"    {sub_label:<35} {score_bar(score)}  {meaning}")

    print()


def print_pillar_summary(name: str, pillar_scores: dict[str, float]) -> None:
    """Print 3-pillar comparison chart."""
    print("=" * 70)
    print(f"  PILLAR SCORES: {name.upper()}")
    print("=" * 70)

    max_label = max(len(PILLARS[k]["label"]) for k in PILLARS)
    for pillar_id, data in PILLARS.items():
        avg = pillar_scores[pillar_id]
        bar_len = int(avg * 8)
        bar = "#" * bar_len + "." * (8 - bar_len)
        label = data["label"].ljust(max_label)
        print(f"    {label}  [{bar}] {avg:.1f}/5.0")

    overall = sum(pillar_scores.values()) / len(pillar_scores)
    print(f"\n    {'Overall'.ljust(max_label)}  {'':>9} {overall:.1f}/5.0")
    print()


def print_weakest_pillar(name: str, pillar_scores: dict[str, float]) -> None:
    """Flag the weakest pillar."""
    weakest_id, weakest_score = find_weakest_pillar(pillar_scores)
    strongest_id, strongest_score = find_strongest_pillar(pillar_scores)
    gap = strongest_score - weakest_score

    print("=" * 70)
    print(f"  WEAKEST PILLAR: {name.upper()}")
    print("=" * 70)
    print(f"    Weakest:   {PILLARS[weakest_id]['label']} ({weakest_score:.1f}/5.0)")
    print(f"    Strongest: {PILLARS[strongest_id]['label']} ({strongest_score:.1f}/5.0)")
    print(f"    Gap:       {gap:.1f} points")
    print()
    print(textwrap.fill(
        f"The {PILLARS[weakest_id]['label']} pillar is the primary defense gap. "
        f"Without improving this area, the other pillars cannot compensate -- "
        f"guardrails without permissions allow unauthorized actions, permissions "
        f"without auditability remove accountability, and auditability without "
        f"guardrails provides visibility but no prevention.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print()


def print_remediation_list(name: str, items: list[dict]) -> None:
    """Print prioritized remediation list."""
    print("=" * 70)
    print(f"  PRIORITIZED REMEDIATION: {name.upper()}")
    print("=" * 70)
    print(f"  {'Priority':<10} {'Pillar':<15} {'Sub-Item':<35} {'Score':<8}")
    print("  " + "-" * 66)

    for item in items:
        if item["score"] >= 5:
            continue
        pri = item["priority"]
        marker = "!!!" if pri == "CRITICAL" else ("!  " if pri == "HIGH" else "   ")
        print(
            f"  {marker} {pri:<8} {item['pillar']:<15} "
            f"{item['sub_item']:<35} {score_bar(item['score'])}"
        )

    print()


def print_governance_gap(name: str, gap: dict) -> None:
    """Print governance-containment gap analysis."""
    print("=" * 70)
    print(f"  GOVERNANCE-CONTAINMENT GAP: {name.upper()}")
    print("=" * 70)

    for item in gap["items"]:
        marker = "+" if item["implemented"] else "x"
        status = "YES" if item["implemented"] else "NO "
        print(f"    [{marker}] {item['name']:<30} {status}  -- {item['description']}")

    print(f"\n    Implemented: {gap['implemented_count']}/{gap['total']}")
    print(f"    Assessment:  {gap['assessment']}")
    print()


def print_comparison(systems: list[dict]) -> None:
    """Print side-by-side comparison of both systems."""
    print("=" * 70)
    print("  SYSTEM COMPARISON")
    print("=" * 70)

    col_w = 30
    header = f"  {'Pillar':<20}"
    for s in systems:
        header += f" {s['name']:^{col_w}}"
    print(header)
    print("  " + "-" * (20 + col_w * len(systems)))

    for pillar_id, data in PILLARS.items():
        row = f"  {data['label']:<20}"
        for s in systems:
            scores = calculate_pillar_scores(s["audit_scores"])
            avg = scores[pillar_id]
            cell = f"{avg:.1f}/5.0"
            row += f" {cell:^{col_w}}"
        print(row)

    row = f"  {'Overall':<20}"
    for s in systems:
        scores = calculate_pillar_scores(s["audit_scores"])
        overall = sum(scores.values()) / len(scores)
        cell = f"{overall:.1f}/5.0"
        row += f" {cell:^{col_w}}"
    print(row)

    row = f"  {'Gov. Gap':<20}"
    for s in systems:
        gap = assess_governance_gap(s["containment"])
        cell = f"{gap['implemented_count']}/{gap['total']}"
        row += f" {cell:^{col_w}}"
    print(row)

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 3 -- Defense Architecture: Three-Pillar Audit")
    print("  Guardrails | Permissions | Auditability")
    print("=" * 70 + "\n")

    for system in AGENT_SYSTEMS:
        print(f"\n>>> System: {system['name']} ({system['risk_profile']})\n")

        pillar_scores = calculate_pillar_scores(system["audit_scores"])
        gap = assess_governance_gap(system["containment"])
        remediation = build_remediation_list(system["audit_scores"], pillar_scores)

        print_pillar_breakdown(system["name"], system["audit_scores"])
        print_pillar_summary(system["name"], pillar_scores)
        print_weakest_pillar(system["name"], pillar_scores)
        print_remediation_list(system["name"], remediation)
        print_governance_gap(system["name"], gap)

    print_comparison(AGENT_SYSTEMS)

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "The three pillars work synergistically -- no single pillar provides complete "
        "protection. The governance-containment gap is the industry's blind spot: "
        "58% have monitoring but only 37% have true containment. Defense requires "
        "guardrails to prevent, permissions to gate, and auditability to prove.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
