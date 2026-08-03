"""
Part 1 — Understanding Agentic AI Security: Threat Model Analyzer

Builds structured threat models for 3 sample agent systems, identifies
which of the 4 key security challenges apply, ranks risks, recommends
controls, and estimates blast radius.

Run:  python threat_model.py
"""

import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

CHALLENGES = {
    "env": "Agents Act on Environment",
    "chain": "Agents Chain Tools Dynamically",
    "memory": "Agents Retain Memory Across Sessions",
    "adapt": "Agents Improvise and Adapt",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# ---------- Agent System Definitions ----------

AGENT_SYSTEMS: list[dict] = [
    {
        "name": "Customer Support Bot",
        "purpose": "Handles customer inquiries, looks up orders, issues refunds, and escalates complex cases to human agents.",
        "tools_access": [
            "order_lookup_api",
            "refund_processing_api",
            "knowledge_base_search",
            "email_send",
            "ticketing_system",
        ],
        "data_access": {
            "read": ["customer_profiles", "order_history", "knowledge_base"],
            "write": ["support_tickets", "refund_records", "email_log"],
        },
        "autonomous_actions": [
            "issue_refunds_up_to_500",
            "send_emails_to_customers",
            "create_escalation_tickets",
            "lookup_order_status",
        ],
        "applicable_challenges": {
            "env": "Can trigger real financial transactions (refunds) and send communications (emails) without human approval.",
            "chain": "Dynamically chains order lookup -> refund decision -> email notification -> ticket creation.",
            "memory": "Retains customer interaction history across sessions to personalize support.",
            "adapt": "Can improvise refund amounts and escalation paths based on conversation context.",
        },
        "risks": [
            {
                "severity": "critical",
                "description": "Prompt injection causes unauthorized mass refunds to attacker-controlled accounts.",
                "controls": [
                    "Require human approval for refunds above threshold",
                    "Rate-limit refund actions per session",
                    "Log all financial actions for audit",
                ],
            },
            {
                "severity": "high",
                "description": "Data exfiltration via crafted prompts that extract customer PII through the order lookup tool.",
                "controls": [
                    "Field-level access control on order data",
                    "Redact PII from LLM responses",
                    "Monitor for unusual data access patterns",
                ],
            },
            {
                "severity": "medium",
                "description": "Memory poisoning inserts false customer preferences that persist across support sessions.",
                "controls": [
                    "Expire cached preferences after TTL",
                    "Validate memory updates against source of truth",
                    "Flag memory mutations for review",
                ],
            },
        ],
        "blast_radius": (
            "An attacker who injects a malicious prompt could issue refunds to arbitrary accounts, "
            "exfiltrate PII for thousands of customers, and poison memory so future sessions are "
            "compromised. Financial loss capped at ~$500/transaction but unlimited volume. "
            "Reputational damage from leaked customer data."
        ),
    },
    {
        "name": "Code Review Assistant",
        "purpose": "Analyzes pull requests, suggests improvements, flags security issues, and can approve or request changes.",
        "tools_access": [
            "git_clone",
            "static_analysis",
            "dependency_scanner",
            "pr_comment_api",
            "pr_approval_api",
        ],
        "data_access": {
            "read": ["source_code", "git_history", "dependency_manifests", "security_advisories"],
            "write": ["pr_comments", "pr_reviews", "approval_decisions"],
        },
        "autonomous_actions": [
            "comment_on_pr",
            "approve_pr",
            "request_changes",
            "flag_security_vulnerabilities",
            "suggest_code_fixes",
        ],
        "applicable_challenges": {
            "env": "Can approve PRs that merge to production, directly affecting codebase integrity.",
            "chain": "Chains clone -> static analysis -> dependency scan -> review -> approval in dynamic order.",
            "memory": "Remembers past review decisions and code patterns across repositories.",
            "adapt": "Improvises review strategies based on codebase size, language, and complexity.",
        },
        "risks": [
            {
                "severity": "critical",
                "description": "Malicious PR crafted to trick the assistant into approving vulnerable or backdoored code.",
                "controls": [
                    "Require human sign-off for security-critical files",
                    "Mandatory dual approval for main branch merges",
                    "Sandbox code execution during analysis",
                ],
            },
            {
                "severity": "high",
                "description": "Prompt injection via code comments or variable names that manipulate review output.",
                "controls": [
                    "Strip comments before LLM analysis",
                    "Validate review output against static analysis results",
                    "Log all review decisions with full prompt context",
                ],
            },
            {
                "severity": "medium",
                "description": "Memory poisoning to skew future reviews in favor of attacker's code style or patterns.",
                "controls": [
                    "Isolate memory per repository",
                    "Periodically reset learned patterns",
                    "Audit memory changes against reviewer guidelines",
                ],
            },
        ],
        "blast_radius": (
            "Compromised assistant could silently approve malicious code that reaches production, "
            "expose secrets found in source code, or systematically weaken security reviews for "
            "a targeted developer's PRs. Impact spans all repositories the assistant has access to."
        ),
    },
    {
        "name": "Financial Analysis Agent",
        "purpose": "Pulls market data, runs analysis models, generates reports, and can execute trades within predefined limits.",
        "tools_access": [
            "market_data_api",
            "portfolio_api",
            "trade_execution_api",
            "news_aggregator",
            "report_generator",
        ],
        "data_access": {
            "read": ["market_feeds", "portfolio_positions", "trading_history", "news_articles"],
            "write": ["trade_orders", "analysis_reports", "portfolio_adjustments"],
        },
        "autonomous_actions": [
            "execute_trades_within_limits",
            "generate_analysis_reports",
            "adjust_portfolio_allocations",
            "alert_on_market_events",
        ],
        "applicable_challenges": {
            "env": "Can execute real financial trades, moving actual money in live markets.",
            "chain": "Chains data ingestion -> analysis -> trade decision -> execution -> reporting.",
            "memory": "Retains market analysis models and portfolio strategy preferences across sessions.",
            "adapt": "Improvises trading strategies based on real-time market conditions and news.",
        },
        "risks": [
            {
                "severity": "critical",
                "description": "Prompt injection triggers unauthorized trades or manipulates analysis to mislead investors.",
                "controls": [
                    "Hard limit on trade size per execution",
                    "Human-in-the-loop for trades above threshold",
                    "Real-time anomaly detection on trade patterns",
                ],
            },
            {
                "severity": "high",
                "description": "Data poisoning of news feeds influences analysis output and downstream trade decisions.",
                "controls": [
                    "Cross-reference multiple news sources",
                    "Flag articles from unverified sources",
                    "Separate data ingestion from decision logic",
                ],
            },
            {
                "severity": "high",
                "description": "Memory poisoning alters portfolio strategy preferences, causing systematic misallocation.",
                "controls": [
                    "Version-controlled strategy parameters",
                    "Audit log for all memory mutations",
                    "Periodic reconciliation against baseline strategy",
                ],
            },
        ],
        "blast_radius": (
            "An attacker could trigger trades that drain portfolio value, inject false analysis that "
            "misleads investors, or corrupt long-term strategy memory. Financial exposure limited "
            "by per-trade caps but aggregate losses could be severe. Regulatory reporting obligations "
            "may be triggered."
        ),
    },
]


# ---------- Analysis Functions ----------


def rank_risks(risks: list[dict]) -> list[dict]:
    """Sort risks by severity (critical first), then by description alphabetically."""
    return sorted(risks, key=lambda r: (SEVERITY_ORDER.get(r["severity"], 99), r["description"]))


def build_threat_summary(system: dict) -> dict:
    """Build a full threat summary for one agent system."""
    ranked = rank_risks(system["risks"])
    return {
        "name": system["name"],
        "purpose": system["purpose"],
        "tools_access": system["tools_access"],
        "data_access": system["data_access"],
        "autonomous_actions": system["autonomous_actions"],
        "applicable_challenges": system["applicable_challenges"],
        "risks": ranked,
        "blast_radius": system["blast_radius"],
    }


# ---------- Display Functions ----------


def print_threat_summary(summary: dict) -> None:
    """Print a formatted threat summary for one system."""
    print("=" * 70)
    print(f"  THREAT MODEL: {summary['name'].upper()}")
    print("=" * 70)

    print(f"\n  Purpose: {summary['purpose']}")

    print("\n  Tools / APIs:")
    for tool in summary["tools_access"]:
        print(f"    - {tool}")

    print("\n  Data Access:")
    print(f"    Read:  {', '.join(summary['data_access']['read'])}")
    print(f"    Write: {', '.join(summary['data_access']['write'])}")

    print("\n  Autonomous Actions:")
    for action in summary["autonomous_actions"]:
        print(f"    - {action}")

    print("\n  Security Challenges:")
    for cid, rationale in summary["applicable_challenges"].items():
        print(f"    [{CHALLENGES[cid]}]")
        wrapped = textwrap.fill(rationale, width=62, initial_indent="      ", subsequent_indent="      ")
        print(wrapped)

    print("\n  Top Risks (ranked by severity):")
    for i, risk in enumerate(summary["risks"], 1):
        sev = risk["severity"].upper()
        print(f"    {i}. [{sev}] {risk['description']}")
        print("       Controls:")
        for ctrl in risk["controls"]:
            print(f"         - {ctrl}")

    print("\n  Blast Radius:")
    wrapped = textwrap.fill(summary["blast_radius"], width=62, initial_indent="    ", subsequent_indent="    ")
    print(wrapped)
    print()


def print_comparison_table(systems: list[dict]) -> None:
    """Print ASCII comparison table: challenges vs systems."""
    names = [s["name"] for s in systems]
    col_width = max(len(n) for n in names) + 4

    print("=" * 70)
    print("  CHALLENGE COMPARISON TABLE")
    print("=" * 70)

    # Header
    header = f"  {'Challenge':<40}"
    for name in names:
        header += f" {name:^{col_width}}"
    print(header)
    print("  " + "-" * (40 + col_width * len(names)))

    # Rows
    for cid, label in CHALLENGES.items():
        row = f"  {label:<40}"
        for system in systems:
            applies = cid in system["applicable_challenges"]
            marker = "  YES  " if applies else "   —  "
            row += f" {marker:^{col_width}}"
        print(row)

    print()


def print_blast_radius(systems: list[dict]) -> None:
    """Print blast radius estimates for all systems."""
    print("=" * 70)
    print("  BLAST RADIUS ESTIMATES")
    print("=" * 70)
    for system in systems:
        print(f"\n  {system['name']}:")
        wrapped = textwrap.fill(
            system["blast_radius"],
            width=64,
            initial_indent="    ",
            subsequent_indent="    ",
        )
        print(wrapped)
    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 1 — Understanding Agentic AI Security")
    print("  Threat Model Analyzer for Sample Agent Systems")
    print("=" * 70 + "\n")

    summaries = [build_threat_summary(s) for s in AGENT_SYSTEMS]

    for summary in summaries:
        print_threat_summary(summary)

    print_comparison_table(AGENT_SYSTEMS)
    print_blast_radius(AGENT_SYSTEMS)

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "Every agent system is vulnerable to all four security challenges, but the "
        "severity and blast radius depend on what the agent can do. Financial and code "
        "integrity systems have the highest blast radius. Defense requires layering "
        "controls: guardrails, permissions, and auditability.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
