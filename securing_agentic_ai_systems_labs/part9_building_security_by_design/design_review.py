"""
Part 9 -- Building Security by Design: Design Review

Conducts a security-by-design review of 2 agent system proposals.
Evaluates each across 6 dimensions (0-5 score), generates findings,
compares proposals, and provides go/no-go recommendation.

Run:  python design_review.py
"""

import json
import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

REVIEW_DIMENSIONS = {
    "security_profile": "Agent Security Profile",
    "threat_modeling": "Threat Modeling",
    "least_privilege": "Least Privilege",
    "secure_defaults": "Secure Defaults",
    "existing_infra": "Existing Infrastructure Integration",
    "compliance": "Compliance",
}

DIMENSION_CRITERIA = {
    "security_profile": "Purpose, resources, actions, prohibited ops, auth requirements documented",
    "threat_modeling": "OWASP/ATLAS applied, top threats identified, attack vectors mapped",
    "least_privilege": "Permissions minimal, default deny, progressive expansion strategy",
    "secure_defaults": "Logging enabled, strictest permissions, guardrails on, shortest credential lifespans",
    "existing_infra": "Using existing IAM/SIEM/IR, not building custom solutions",
    "compliance": "GDPR/HIPAA/SOX/ISO 42001 requirements identified and addressed",
}

SCORE_MEANING = {
    0: "Not addressed",
    1: "Minimal consideration",
    2: "Partial documentation",
    3: "Adequate coverage",
    4: "Strong implementation",
    5: "Best-in-class",
}


# ---------- Agent System Proposals ----------

PROPOSALS: list[dict] = [
    {
        "name": "Secure Banking Assistant",
        "type": "Well-Designed",
        "purpose": "Processes internal bank transfers, provides account balance inquiries, generates regulatory reports. Accesses account database, payment processing system, and reporting tools.",
        "resources": ["account_database", "payment_processing_api", "reporting_tools", "audit_logs"],
        "actions": ["read_balance", "process_transfer", "generate_report", "log_transaction"],
        "prohibited": ["modify_schema", "access_other_accounts", "delete_records", "external_communications"],
        "review_scores": {
            "security_profile": {
                "score": 5,
                "evidence": "Full security profile documented: purpose, resources, actions, prohibited ops, auth requirements, monitoring needs. Reviewed by security team before development.",
            },
            "threat_modeling": {
                "score": 4,
                "evidence": "OWASP Top 10 and MITRE ATLAS applied. 8 threats identified with mitigations. Missing: multi-agent coordination scenario (not applicable to current design).",
            },
            "least_privilege": {
                "score": 5,
                "evidence": "Default deny. Each permission explicitly granted and justified. RBAC with 3 roles (read-only, standard, admin). No shared accounts. Progressive expansion documented.",
            },
            "secure_defaults": {
                "score": 4,
                "evidence": "All logging enabled by default. Strictest permission set. Guardrails on all tool calls. 1-hour credential lifetime. Missing: automated config validation in CI.",
            },
            "existing_infra": {
                "score": 5,
                "evidence": "Uses existing Azure Entra ID for auth. Logs to existing Sentinel SIEM. Incident response through existing SOC team. Agent-specific runbook added to IR procedures.",
            },
            "compliance": {
                "score": 4,
                "evidence": "GDPR data handling documented. SOX audit trail requirements met. ISO 42001 checklist 80% complete. Missing: formal DPIA for automated decision-making.",
            },
        },
        "findings": [
            {"severity": "low", "finding": "Multi-agent coordination threat not modeled", "recommendation": "Add note that multi-agent scenarios are out of scope for current design"},
            {"severity": "low", "finding": "Automated config validation not in CI pipeline", "recommendation": "Add schema validation to CI/CD for agent config files"},
            {"severity": "info", "finding": "DPIA for automated decisions pending", "recommendation": "Complete DPIA before processing customer data in production"},
        ],
    },
    {
        "name": "Quick Customer Bot",
        "type": "Security Gaps",
        "purpose": "Handles customer inquiries, processes refunds, sends emails. Accesses customer database, email system, and payment processing. Built quickly to meet Q3 deadline.",
        "resources": ["customer_database", "email_system", "payment_processing", "knowledge_base", "crm_system"],
        "actions": ["read_customer_data", "send_email", "process_refund", "update_records", "search_knowledge_base"],
        "prohibited": [],
        "review_scores": {
            "security_profile": {
                "score": 2,
                "evidence": "Basic purpose documented. Resources and actions listed but not formally approved. Prohibited operations not defined. No monitoring requirements specified.",
            },
            "threat_modeling": {
                "score": 1,
                "evidence": "Informal discussion of risks. No structured threat model. OWASP/ATLAS not applied. Attack vectors not mapped. Consequences not documented.",
            },
            "least_privilege": {
                "score": 2,
                "evidence": "Some permission scoping exists (refund cap). But email access unrestricted. CRM access broad. No formal RBAC model. Default allow for most operations.",
            },
            "secure_defaults": {
                "score": 1,
                "evidence": "Basic logging enabled. Permissions not restricted by default. Guardrails minimal. 30-day credential lifetime. No config validation.",
            },
            "existing_infra": {
                "score": 3,
                "evidence": "Uses existing email system and CRM. Logs go to application logging (not SIEM). Incident response not integrated with SOC. Custom logging solution built.",
            },
            "compliance": {
                "score": 2,
                "evidence": "GDPR mentioned but not detailed. PII handling informal. No formal data retention policy. No compliance review conducted.",
            },
        },
        "findings": [
            {"severity": "critical", "finding": "No threat model conducted", "recommendation": "Conduct formal threat modeling using OWASP/ATLAS before deployment"},
            {"severity": "critical", "finding": "Prohibited operations not defined", "recommendation": "Document all prohibited operations and implement enforcement"},
            {"severity": "high", "finding": "Default allow permissions", "recommendation": "Switch to default deny with explicit grants for each capability"},
            {"severity": "high", "finding": "Email access unrestricted", "recommendation": "Implement recipient allowlisting and rate limits"},
            {"severity": "high", "finding": "Logging not integrated with SIEM", "recommendation": "Send agent logs to existing SIEM for correlation"},
            {"severity": "medium", "finding": "30-day credential lifetime", "recommendation": "Reduce to 1-hour with automatic rotation"},
            {"severity": "medium", "finding": "No compliance review", "recommendation": "Conduct GDPR/HIPAA assessment before processing customer data"},
            {"severity": "low", "finding": "Custom logging solution", "recommendation": "Replace with existing logging infrastructure to reduce maintenance"},
        ],
    },
]


# ---------- Analysis Functions ----------


def calculate_readiness(proposal: dict) -> dict:
    """Calculate overall readiness score and verdict."""
    scores = proposal["review_scores"]
    total = sum(s["score"] for s in scores.values())
    count = len(scores)
    overall = total / count if count > 0 else 0

    if overall >= 4.0:
        verdict = "GO"
        verdict_desc = "Ready for secure development and deployment"
    elif overall >= 3.0:
        verdict = "CONDITIONAL"
        verdict_desc = "Proceed with mandatory security improvements"
    else:
        verdict = "NO-GO"
        verdict_desc = "Not ready -- critical security gaps must be addressed first"

    return {"overall": overall, "verdict": verdict, "verdict_desc": verdict_desc}


def compare_proposals(a: dict, b: dict) -> dict:
    """Compare two proposals side by side."""
    readiness_a = calculate_readiness(a)
    readiness_b = calculate_readiness(b)

    dimension_comparison = {}
    for dim in REVIEW_DIMENSIONS:
        score_a = a["review_scores"].get(dim, {}).get("score", 0)
        score_b = b["review_scores"].get(dim, {}).get("score", 0)
        dimension_comparison[dim] = {
            "a": score_a,
            "b": score_b,
            "winner": a["name"] if score_a > score_b else (b["name"] if score_b > score_a else "Tie"),
        }

    critical_a = sum(1 for f in a["findings"] if f["severity"] == "critical")
    critical_b = sum(1 for f in b["findings"] if f["severity"] == "critical")
    high_a = sum(1 for f in a["findings"] if f["severity"] == "high")
    high_b = sum(1 for f in b["findings"] if f["severity"] == "high")

    return {
        "readiness_a": readiness_a,
        "readiness_b": readiness_b,
        "dimension_comparison": dimension_comparison,
        "critical_gaps": {"a": critical_a, "b": critical_b},
        "high_risks": {"a": high_a, "b": high_b},
    }


# ---------- Display Functions ----------


def progress_bar(pct: float, width: int = 15) -> str:
    """Generate ASCII progress bar."""
    filled = int(pct / 100 * width)
    empty = width - filled
    return f"[{'#' * filled}{'.' * empty}] {pct:.0f}%"


def print_proposal_profile(proposal: dict) -> None:
    """Print proposal overview."""
    print("=" * 70)
    print(f"  PROPOSAL: {proposal['name'].upper()}")
    print(f"  Type: {proposal['type']}")
    print("=" * 70)

    print(f"\n  Purpose: {proposal['purpose']}")
    print(f"\n  Resources: {', '.join(proposal['resources'])}")
    print(f"  Actions:   {', '.join(proposal['actions'])}")
    print(f"  Prohibited: {', '.join(proposal['prohibited']) if proposal['prohibited'] else '(not defined)'}")
    print()


def print_dimension_scores(proposal: dict) -> None:
    """Print 6-dimension scores."""
    print("  Design Review Scores:")
    print("  " + "-" * 55)

    for dim_id, dim_label in REVIEW_DIMENSIONS.items():
        data = proposal["review_scores"].get(dim_id, {"score": 0, "evidence": ""})
        score = data["score"]
        pct = score / 5 * 100
        meaning = SCORE_MEANING.get(score, "?")
        print(f"    {dim_label:<35} {progress_bar(pct, 10)} {score}/5  {meaning}")

    readiness = calculate_readiness(proposal)
    print(f"\n    {'Overall Readiness':<35} {progress_bar(readiness['overall'] / 5 * 100, 10)} {readiness['overall']:.1f}/5")
    print(f"    {'Verdict':<35} {readiness['verdict']} -- {readiness['verdict_desc']}")
    print()


def print_findings(proposal: dict) -> None:
    """Print findings with severity."""
    print("  Findings:")
    print("  " + "-" * 55)

    if not proposal["findings"]:
        print("    No findings -- clean design.")
        print()
        return

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(proposal["findings"], key=lambda f: severity_order.get(f["severity"], 99))

    for f in sorted_findings:
        sev = f["severity"].upper()
        marker = "!!!" if f["severity"] == "critical" else ("!  " if f["severity"] == "high" else "   ")
        print(f"    {marker} [{sev:<8}] {f['finding']}")
        rec = textwrap.fill(f["recommendation"], width=55, initial_indent="             Recommendation: ", subsequent_indent="                           ")
        print(rec)

    counts = {}
    for f in proposal["findings"]:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print(f"\n    Summary: {counts.get('critical', 0)} critical, {counts.get('high', 0)} high, {counts.get('medium', 0)} medium, {counts.get('low', 0)} low, {counts.get('info', 0)} info")
    print()


def print_comparison(a: dict, b: dict) -> None:
    """Print side-by-side comparison."""
    print("=" * 70)
    print("  PROPOSAL COMPARISON")
    print("=" * 70)

    comp = compare_proposals(a, b)

    print(f"\n  {'Dimension':<35} {a['name']:<20} {b['name']:<20}")
    print("  " + "-" * 75)

    for dim_id, dim_label in REVIEW_DIMENSIONS.items():
        dc = comp["dimension_comparison"][dim_id]
        score_a = f"{dc['a']}/5"
        score_b = f"{dc['b']}/5"
        winner = " <<" if dc["winner"] == a["name"] else (" <<" if dc["winner"] == b["name"] else "")
        print(f"  {dim_label:<35} {score_a:<20} {score_b:<20}{winner}")

    print()
    print(f"  {'Overall Readiness':<35} {comp['readiness_a']['overall']:.1f}/5{'':>14} {comp['readiness_b']['overall']:.1f}/5")
    print(f"  {'Verdict':<35} {comp['readiness_a']['verdict']:<20} {comp['readiness_b']['verdict']:<20}")
    print(f"  {'Critical Gaps':<35} {comp['critical_gaps']['a']:<20} {comp['critical_gaps']['b']:<20}")
    print(f"  {'High Risks':<35} {comp['high_risks']['a']:<20} {comp['high_risks']['b']:<20}")

    print()
    print("  Why one is more secure:")
    print("  " + "-" * 55)
    print(f"  {a['name']} is more secure because:")
    print("    - Full security profile documented before development")
    print("    - Formal threat modeling using OWASP and ATLAS frameworks")
    print("    - Default deny with explicit permission grants")
    print("    - Integrated with existing IAM/SIEM/IR infrastructure")
    print("    - Comprehensive compliance documentation")
    print()
    print(f"  {b['name']} has critical gaps:")
    print("    - No structured threat model")
    print("    - Default allow permissions")
    print("    - Custom logging not integrated with security operations")
    print("    - Prohibited operations not defined")
    print("    - No compliance review conducted")
    print()


def print_recommendation(proposal: dict) -> None:
    """Print go/no-go recommendation."""
    print("=" * 70)
    print(f"  RECOMMENDATION: {proposal['name'].upper()}")
    print("=" * 70)

    readiness = calculate_readiness(proposal)

    print(f"\n  Readiness Score: {readiness['overall']:.1f}/5.0")
    print(f"  Verdict: {readiness['verdict']}")
    print(f"  Assessment: {readiness['verdict_desc']}")

    if readiness["verdict"] == "GO":
        print("\n  Proceed with development. Security design is strong.")
        print("  Complete pending items (DPIA, config validation) before production.")
    elif readiness["verdict"] == "CONDITIONAL":
        print("\n  Address the following before proceeding:")
        critical = [f for f in proposal["findings"] if f["severity"] == "critical"]
        high = [f for f in proposal["findings"] if f["severity"] == "high"]
        for f in critical:
            print(f"    CRITICAL: {f['finding']}")
        for f in high:
            print(f"    HIGH: {f['finding']}")
    else:
        print("\n  DO NOT PROCEED with current design.")
        print("  Required before re-review:")
        critical = [f for f in proposal["findings"] if f["severity"] == "critical"]
        for f in critical:
            print(f"    1. {f['finding']}: {f['recommendation']}")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 9 -- Building Security by Design")
    print("  Security-by-Design Review")
    print("=" * 70 + "\n")

    for proposal in PROPOSALS:
        print_proposal_profile(proposal)
        print_dimension_scores(proposal)
        print_findings(proposal)
        print_recommendation(proposal)

    print_comparison(PROPOSALS[0], PROPOSALS[1])

    # JSON export
    json_output = {
        "proposals": [
            {
                "name": p["name"],
                "type": p["type"],
                "readiness": calculate_readiness(p),
                "review_scores": p["review_scores"],
                "findings": p["findings"],
            }
            for p in PROPOSALS
        ],
        "comparison": compare_proposals(PROPOSALS[0], PROPOSALS[1]),
    }
    json_path = "design_review.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON review written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "Security works best when built into systems from the beginning. "
        "Document your agent security profile before development. Apply "
        "threat modeling frameworks systematically. Default to deny. Use "
        "existing security infrastructure. Compliance is not optional.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
