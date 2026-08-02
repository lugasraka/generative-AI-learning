"""
Part 6 — Challenges and Future Directions: Risk audit tool

Evaluates 3 Agentic RAG systems across 4 challenge dimensions
(coordination, scalability, data quality, transparency), recommends
future directions, and generates a risk report.

Run:  python risk_audit.py
"""

import datetime
import os
import sys
from pathlib import Path
from typing import Any

# ---------- UTF-8 fix for Windows ----------

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Configuration ----------

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/mimo-v2.5")

# ---------- System profiles ----------

SYSTEMS: list[dict[str, Any]] = [
    {
        "name": "Customer Support Bot",
        "description": (
            "Handles customer inquiries via chat and email. Routes queries to "
            "knowledge base, ticket system, or live agent based on complexity."
        ),
        "agents": 2,
        "sources": 4,
        "concurrent_users": 500,
        "data_reliability": "high",
        "has_verification": True,
        "has_logging": True,
        "traceable": True,
        "handles_repetitive": True,
        "high_stakes": False,
        "sensitive_data": False,
    },
    {
        "name": "Medical Research Assistant",
        "description": (
            "Assists researchers by querying PubMed, clinical trials, drug "
            "databases, and patient records to synthesize literature reviews "
            "and treatment recommendations."
        ),
        "agents": 3,
        "sources": 6,
        "concurrent_users": 50,
        "data_reliability": "mixed",
        "has_verification": True,
        "has_logging": True,
        "traceable": True,
        "handles_repetitive": False,
        "high_stakes": True,
        "sensitive_data": True,
    },
    {
        "name": "Financial Analysis Tool",
        "description": (
            "Aggregates market data, SEC filings, news feeds, internal reports, "
            "and social sentiment to generate investment insights and risk "
            "assessments for portfolio managers."
        ),
        "agents": 4,
        "sources": 5,
        "concurrent_users": 200,
        "data_reliability": "medium",
        "has_verification": True,
        "has_logging": True,
        "traceable": True,
        "handles_repetitive": True,
        "high_stakes": True,
        "sensitive_data": True,
    },
]

# ---------- Scoring rubric ----------


def score_coordination(system: dict[str, Any]) -> int:
    """Score coordination complexity (1-5, higher = more risk)."""
    agents = system["agents"]
    if agents <= 1:
        return 1
    if agents == 2:
        return 2
    if agents == 3:
        return 3
    if agents == 4:
        return 4
    return 5


def score_scalability(system: dict[str, Any]) -> int:
    """Score scalability concerns (1-5, higher = more risk)."""
    users = system["concurrent_users"]
    sources = system["sources"]
    user_score = 1 if users < 100 else (3 if users < 500 else 5)
    source_score = 1 if sources <= 2 else (3 if sources <= 4 else 5)
    return round((user_score + source_score) / 2)


def score_data_quality(system: dict[str, Any]) -> int:
    """Score data quality risk (1-5, higher = more risk)."""
    reliability_map = {"high": 1, "medium": 3, "low": 5, "mixed": 4}
    base = reliability_map.get(system["data_reliability"], 3)
    if system["has_verification"]:
        base = max(1, base - 1)
    return base


def score_transparency(system: dict[str, Any]) -> int:
    """Score transparency risk (1-5, higher = more risk)."""
    score = 3
    if system["has_logging"]:
        score -= 1
    if system["traceable"]:
        score -= 1
    return max(1, score)


# ---------- Future direction recommendations ----------


def recommend_directions(system: dict[str, Any]) -> list[dict[str, str]]:
    """Recommend future directions based on system characteristics."""
    recs: list[dict[str, str]] = []

    if system["handles_repetitive"]:
        recs.append(
            {
                "direction": "Learning Agents",
                "reason": "System handles repetitive queries — agents could learn from past interactions to improve over time.",
            }
        )

    if system["high_stakes"]:
        recs.append(
            {
                "direction": "Human-in-the-Loop",
                "reason": "High-stakes decisions require human oversight for critical or irreversible actions.",
            }
        )

    if system["sensitive_data"]:
        recs.append(
            {
                "direction": "Ethical Agents",
                "reason": "Sensitive data (medical, financial) requires fairness auditing and bias mitigation.",
            }
        )

    if system["agents"] >= 3:
        recs.append(
            {
                "direction": "Better Orchestration",
                "reason": f"System uses {system['agents']} agents — smarter workflow routing would reduce coordination overhead.",
            }
        )

    return recs


# ---------- Overall risk level ----------


def overall_risk(scores: dict[str, int]) -> str:
    """Calculate overall risk level from dimension scores."""
    total = sum(scores.values())
    if total <= 8:
        return "low"
    if total <= 14:
        return "medium"
    return "high"


def risk_color(level: str) -> str:
    """Return color for risk level."""
    return {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}[level]


# ---------- Display ----------


def banner(title: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_risk_bar(label: str, score: int, max_score: int = 5) -> None:
    """Print a visual risk bar."""
    filled = "#" * score
    empty = "." * (max_score - score)
    print(f"  {label:<15} [{filled}{empty}] {score}/5")


# ---------- Markdown output ----------

RESULTS_PATH = Path(__file__).parent / "results.md"


def write_results(audits: list[dict[str, Any]], comparison: str) -> None:
    """Write full risk audit report to markdown."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# Part 6 — Agentic RAG Risk Audit Report",
        "",
        f"- **Generated:** {now}",
        "",
    ]

    for audit in audits:
        sys_info = audit["system"]
        scores = audit["scores"]
        risk = audit["risk_level"]
        recs = audit["recommendations"]

        lines.append(f"## {sys_info['name']}")
        lines.append("")
        lines.append(f"> {sys_info['description']}")
        lines.append("")
        lines.append("### System Profile")
        lines.append("")
        lines.append(f"- **Agents:** {sys_info['agents']}")
        lines.append(f"- **Data sources:** {sys_info['sources']}")
        lines.append(f"- **Concurrent users:** {sys_info['concurrent_users']}")
        lines.append(f"- **Data reliability:** {sys_info['data_reliability']}")
        lines.append(
            f"- **Verification:** {'Yes' if sys_info['has_verification'] else 'No'}"
        )
        lines.append(f"- **Logging:** {'Yes' if sys_info['has_logging'] else 'No'}")
        lines.append(f"- **Traceable:** {'Yes' if sys_info['traceable'] else 'No'}")
        lines.append("")
        lines.append("### Risk Scores")
        lines.append("")
        lines.append("| Dimension | Score | Risk |")
        lines.append("|-----------|-------|------|")
        for dim, score in scores.items():
            level = "High" if score >= 4 else ("Medium" if score >= 3 else "Low")
            lines.append(f"| {dim.title()} | {score}/5 | {level} |")
        lines.append("")
        total = sum(scores.values())
        lines.append(f"**Overall risk: {risk.upper()}** ({total}/20)")
        lines.append("")

        if recs:
            lines.append("### Recommended Future Directions")
            lines.append("")
            for r in recs:
                lines.append(f"- **{r['direction']}**: {r['reason']}")
            lines.append("")

    lines.append("## Cross-System Comparison")
    lines.append("")
    lines.append(
        "| System | Coordination | Scalability | Data Quality | Transparency | Total | Risk |"
    )
    lines.append(
        "|--------|-------------|-------------|--------------|--------------|-------|------|"
    )
    for audit in audits:
        s = audit["scores"]
        total = sum(s.values())
        lines.append(
            f"| {audit['system']['name']} "
            f"| {s['Coordination']} | {s['Scalability']} "
            f"| {s['Data Quality']} | {s['Transparency']} "
            f"| {total}/20 | {audit['risk_level'].upper()} |"
        )
    lines.append("")
    lines.append(comparison)

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main ----------


def main() -> None:
    """Run risk audit on all systems."""
    banner("Part 6 — Agentic RAG Risk Audit Tool")
    print(f"Evaluating {len(SYSTEMS)} systems across 4 challenge dimensions.\n")

    audits: list[dict[str, Any]] = []

    for system in SYSTEMS:
        scores = {
            "Coordination": score_coordination(system),
            "Scalability": score_scalability(system),
            "Data Quality": score_data_quality(system),
            "Transparency": score_transparency(system),
        }
        risk = overall_risk(scores)
        recs = recommend_directions(system)

        audits.append(
            {
                "system": system,
                "scores": scores,
                "risk_level": risk,
                "total": sum(scores.values()),
                "recommendations": recs,
            }
        )

        banner(system["name"])
        print(f"  {system['description']}\n")
        print(
            f"  Agents: {system['agents']}  |  Sources: {system['sources']}  "
            f"|  Users: {system['concurrent_users']}  "
            f"|  Reliability: {system['data_reliability']}\n"
        )

        print("  Risk Scores:")
        for dim, score in scores.items():
            print_risk_bar(dim, score)

        total = sum(scores.values())
        print(f"\n  Overall: {risk.upper()} ({total}/20)")

        if recs:
            print("\n  Recommended Future Directions:")
            for r in recs:
                print(f"    - {r['direction']}: {r['reason'][:80]}...")
        print()

    # Cross-system comparison
    banner("Cross-System Comparison")
    print(
        f"  {'System':<30} {'Coord':<6} {'Scale':<6} {'Data':<6} {'Trans':<6} {'Total':<6} Risk"
    )
    print(f"  {'-' * 30} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6}")
    for a in sorted(audits, key=lambda x: x["total"], reverse=True):
        s = a["scores"]
        print(
            f"  {a['system']['name']:<30} {s['Coordination']:<6} "
            f"{s['Scalability']:<6} {s['Data Quality']:<6} "
            f"{s['Transparency']:<6} {a['total']:<6} {a['risk_level'].upper()}"
        )

    riskiest = max(audits, key=lambda x: x["total"])
    safest = min(audits, key=lambda x: x["total"])

    comparison = (
        f"**Riskiest system:** {riskiest['system']['name']} ({riskiest['total']}/20) — "
        f"high coordination overhead ({riskiest['scores']['Coordination']}/5) and "
        f"scalability pressure ({riskiest['scores']['Scalability']}/5) from managing "
        f"{riskiest['system']['agents']} agents across {riskiest['system']['sources']} sources.\n\n"
        f"**Safest system:** {safest['system']['name']} ({safest['total']}/20) — "
        f"simple coordination ({safest['scores']['Coordination']}/5) and "
        f"high data reliability reduce overall risk."
    )
    print(
        f"\n  {riskiest['system']['name']} is riskiest due to "
        f"multi-agent coordination and many data sources."
    )
    print(f"  {safest['system']['name']} is safest with fewer agents and curated data.")

    write_results(audits, comparison)
    banner("DONE — Part 6 complete. Course finished!")


if __name__ == "__main__":
    main()
