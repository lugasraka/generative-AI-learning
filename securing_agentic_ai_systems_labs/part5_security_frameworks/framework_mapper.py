"""
Part 5 -- Security Frameworks for Agentic AI: Framework Mapper

Maps 2 agent systems against three security frameworks (OWASP Top 10,
NIST AI RMF, MITRE ATLAS), scores coverage, prints summary tables,
and identifies the biggest gap per framework.

Run:  python framework_mapper.py
"""

import json
import sys
import textwrap

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Constants ----------

OWASP_CATEGORIES = [
    ("goal_hijacking", "Goal Hijacking", "Manipulating agent objectives over time"),
    ("identity_abuse", "Identity Abuse", "Exploiting agent identity and authentication systems"),
    ("human_trust_manipulation", "Human Trust Manipulation", "Exploiting human trust in agent recommendations"),
    ("rogue_autonomous_behaviors", "Rogue Autonomous Behaviors", "Unexpected, unauthorized, or harmful autonomous actions"),
    ("tool_misuse", "Tool Misuse & Privilege Escalation", "Unauthorized tool invocation or chaining"),
    ("memory_poisoning", "Memory Poisoning", "Compromising persistent memory through injection"),
    ("supply_chain", "Supply Chain Vulnerabilities", "Risks from compromised frameworks, models, plugins"),
    ("multi_agent_coordination", "Multi-Agent Coordination Attacks", "Exploiting communication between agents"),
    ("context_manipulation", "Context Manipulation", "Poisoning RAG systems, knowledge bases, data sources"),
    ("insufficient_monitoring", "Insufficient Monitoring & Response", "Lack of visibility or response capability"),
]

NIST_FUNCTIONS = [
    ("govern", "GOVERN", "Cultivates a culture of risk management"),
    ("map", "MAP", "Establishes context for AI systems"),
    ("measure", "MEASURE", "Analyzes and monitors risk"),
    ("manage", "MANAGE", "Ongoing risk management and response"),
]

ATLAS_TECHNIQUES = [
    ("ai_agent_context_poisoning", "AI Agent Context Poisoning", "Manipulating agent context to persistently influence behavior"),
    ("memory_manipulation", "Memory Manipulation", "Altering long-term memory across sessions"),
    ("modify_agent_config", "Modify AI Agent Configuration", "Changing config files for persistent malicious behavior"),
    ("exfiltration_via_tool", "Exfiltration via Tool Invocation", "Using legitimate write tools to leak data"),
    ("rag_credential_harvesting", "RAG Credential Harvesting", "Collecting credentials from ingested documents"),
    ("agent_config_discovery", "Agent Configuration Discovery", "Enumerating agent configs and permissions"),
    ("tool_definitions_discovery", "Tool Definitions Discovery", "Enumerating available tools"),
    ("prompt_injection_direct", "Direct Prompt Injection", "Crafting inputs to override system instructions"),
    ("prompt_injection_indirect", "Indirect Prompt Injection", "Embedding instructions in external content"),
    ("privilege_escalation", "Privilege Escalation", "Chain permissions to gain unauthorized capabilities"),
    ("data_exfiltration", "Data Exfiltration", "Extracting sensitive data through agent actions"),
    ("denial_of_service", "Denial of Service", "Overwhelming agent with requests or resource consumption"),
    ("model_theft", "Model Theft / Extraction", "Extracting model parameters or training data"),
    ("supply_chain_attack", "Supply Chain Attack", "Compromising dependencies, plugins, or model updates"),
]

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "none": 3}


# ---------- Agent System Definitions ----------

AGENT_SYSTEMS: list[dict] = [
    {
        "name": "Customer Support Agent",
        "purpose": "Handles customer inquiries, processes refunds, accesses CRM and order data. User-facing with direct tool access.",
        "owasp_scores": {
            "goal_hijacking": "high",
            "identity_abuse": "medium",
            "human_trust_manipulation": "high",
            "rogue_autonomous_behaviors": "medium",
            "tool_misuse": "high",
            "memory_poisoning": "medium",
            "supply_chain": "low",
            "multi_agent_coordination": "none",
            "context_manipulation": "medium",
            "insufficient_monitoring": "medium",
        },
        "nist_scores": {
            "govern": {"score": 4, "evidence": "Deployment approval process, monitoring policies, misbehavior handling documented"},
            "map": {"score": 3, "evidence": "Data sources mapped, tool access documented, but harm analysis incomplete"},
            "measure": {"score": 2, "evidence": "Basic monitoring in place, no behavioral testing or goal alignment metrics"},
            "manage": {"score": 3, "evidence": "Incident response plan exists, three-pillar defense partially implemented"},
        },
        "atlas_coverage": {
            "ai_agent_context_poisoning": {"applies": True, "mitigated": False, "mitigation": ""},
            "memory_manipulation": {"applies": True, "mitigated": True, "mitigation": "Memory TTL expiration, write validation"},
            "modify_agent_config": {"applies": False, "mitigated": False, "mitigation": ""},
            "exfiltration_via_tool": {"applies": True, "mitigated": True, "mitigation": "Data export rate limits"},
            "rag_credential_harvesting": {"applies": False, "mitigated": False, "mitigation": ""},
            "agent_config_discovery": {"applies": True, "mitigated": False, "mitigation": ""},
            "tool_definitions_discovery": {"applies": True, "mitigated": True, "mitigation": "Tool access logging"},
            "prompt_injection_direct": {"applies": True, "mitigated": True, "mitigation": "Input validation, regex filters"},
            "prompt_injection_indirect": {"applies": True, "mitigated": False, "mitigation": ""},
            "privilege_escalation": {"applies": True, "mitigated": True, "mitigation": "Least privilege, scope validation"},
            "data_exfiltration": {"applies": True, "mitigated": True, "mitigation": "PII detection, rate limits"},
            "denial_of_service": {"applies": False, "mitigated": False, "mitigation": ""},
            "model_theft": {"applies": False, "mitigated": False, "mitigation": ""},
            "supply_chain_attack": {"applies": True, "mitigated": False, "mitigation": ""},
        },
    },
    {
        "name": "Financial Trading Agent",
        "purpose": "Executes trades within limits, generates analysis reports, accesses market data and portfolio systems. High autonomy, financial impact.",
        "owasp_scores": {
            "goal_hijacking": "high",
            "identity_abuse": "high",
            "human_trust_manipulation": "medium",
            "rogue_autonomous_behaviors": "high",
            "tool_misuse": "high",
            "memory_poisoning": "high",
            "supply_chain": "high",
            "multi_agent_coordination": "medium",
            "context_manipulation": "high",
            "insufficient_monitoring": "high",
        },
        "nist_scores": {
            "govern": {"score": 3, "evidence": "Authority limits defined, but approval processes informal for automated trades"},
            "map": {"score": 4, "evidence": "Data sources, tools, and harm scenarios well-documented"},
            "measure": {"score": 3, "evidence": "Trade monitoring active, some behavioral baselines, no adversarial testing"},
            "manage": {"score": 2, "evidence": "Circuit breakers partial, incident response untested for agent-specific scenarios"},
        },
        "atlas_coverage": {
            "ai_agent_context_poisoning": {"applies": True, "mitigated": False, "mitigation": ""},
            "memory_manipulation": {"applies": True, "mitigated": False, "mitigation": ""},
            "modify_agent_config": {"applies": True, "mitigated": True, "mitigation": "Config versioning, change alerts"},
            "exfiltration_via_tool": {"applies": True, "mitigated": True, "mitigation": "Trade log auditing, anomaly detection"},
            "rag_credential_harvesting": {"applies": True, "mitigated": False, "mitigation": ""},
            "agent_config_discovery": {"applies": True, "mitigated": True, "mitigation": "Access control on config endpoints"},
            "tool_definitions_discovery": {"applies": True, "mitigated": False, "mitigation": ""},
            "prompt_injection_direct": {"applies": True, "mitigated": True, "mitigation": "Input validation, intent checking"},
            "prompt_injection_indirect": {"applies": True, "mitigated": False, "mitigation": ""},
            "privilege_escalation": {"applies": True, "mitigated": True, "mitigation": "Trade size caps, API scope limits"},
            "data_exfiltration": {"applies": True, "mitigated": True, "mitigation": "Network segmentation, export monitoring"},
            "denial_of_service": {"applies": True, "mitigated": False, "mitigation": ""},
            "model_theft": {"applies": False, "mitigated": False, "mitigation": ""},
            "supply_chain_attack": {"applies": True, "mitigated": False, "mitigation": ""},
        },
    },
]


# ---------- Analysis Functions ----------


def map_owasp(system: dict) -> dict:
    """Assess OWASP Top 10 risks for a system."""
    scores = system["owasp_scores"]
    high = sum(1 for v in scores.values() if v == "high")
    medium = sum(1 for v in scores.values() if v == "medium")
    low = sum(1 for v in scores.values() if v == "low")
    none = sum(1 for v in scores.values() if v == "none")
    return {"scores": scores, "high": high, "medium": medium, "low": low, "none": none}


def map_nist(system: dict) -> dict:
    """Assess NIST AI RMF function scores for a system."""
    scores = system["nist_scores"]
    overall = sum(s["score"] for s in scores.values()) / len(scores) if scores else 0
    return {"scores": scores, "overall": overall}


def map_atlas(system: dict) -> dict:
    """Assess MITRE ATLAS technique coverage for a system."""
    coverage = system["atlas_coverage"]
    applies = sum(1 for v in coverage.values() if v["applies"])
    mitigated = sum(1 for v in coverage.values() if v["applies"] and v["mitigated"])
    unmitigated = applies - mitigated
    coverage_pct = (mitigated / applies * 100) if applies > 0 else 0
    return {
        "scores": coverage,
        "applies": applies,
        "mitigated": mitigated,
        "unmitigated": unmitigated,
        "coverage_pct": coverage_pct,
    }


def find_biggest_gap(owasp: dict, nist: dict, atlas: dict) -> dict:
    """Find which framework reveals the most risk for a system."""
    owasp_risk = owasp["high"] + owasp["medium"] * 0.5
    nist_risk = 5 - nist["overall"]
    atlas_risk = atlas["unmitigated"]

    gaps = [
        {"framework": "OWASP Top 10", "risk_score": owasp_risk, "detail": f"{owasp['high']} high, {owasp['medium']} medium risks"},
        {"framework": "NIST AI RMF", "risk_score": nist_risk, "detail": f"Overall score {nist['overall']:.1f}/5.0"},
        {"framework": "MITRE ATLAS", "risk_score": atlas_risk, "detail": f"{atlas['unmitigated']}/{atlas['applies']} techniques unmitigated"},
    ]
    biggest = max(gaps, key=lambda g: g["risk_score"])
    return {"biggest": biggest, "all": gaps}


# ---------- Display Functions ----------


def print_owasp_mapping(name: str, owasp: dict) -> None:
    """Print OWASP Top 10 mapping."""
    print("=" * 70)
    print(f"  OWASP TOP 10 MAPPING: {name.upper()}")
    print("=" * 70)

    print(f"\n  {'Category':<35} {'Applies?':<10} {'Severity':<10}")
    print("  " + "-" * 55)

    for cat_id, cat_label, cat_desc in OWASP_CATEGORIES:
        severity = owasp["scores"].get(cat_id, "none")
        applies = "YES" if severity != "none" else "NO"
        print(f"  {cat_label:<35} {applies:<10} {severity.upper():<10}")

    print(f"\n  Summary: {owasp['high']} high, {owasp['medium']} medium, {owasp['low']} low, {owasp['none']} none")
    print()


def print_nist_mapping(name: str, nist: dict) -> None:
    """Print NIST AI RMF mapping."""
    print("=" * 70)
    print(f"  NIST AI RMF MAPPING: {name.upper()}")
    print("=" * 70)

    for func_id, func_label, func_desc in NIST_FUNCTIONS:
        data = nist["scores"].get(func_id, {"score": 0, "evidence": ""})
        score = data["score"]
        bar = "#" * (score * 2) + "." * ((5 - score) * 2)
        print(f"\n  {func_label} ({func_desc})")
        print(f"    Score: [{bar}] {score}/5")
        evidence = textwrap.fill(data["evidence"], width=60, initial_indent="    Evidence: ", subsequent_indent="              ")
        print(evidence)

    print(f"\n  Overall: {nist['overall']:.1f}/5.0")
    print()


def print_atlas_mapping(name: str, atlas: dict) -> None:
    """Print MITRE ATLAS mapping."""
    print("=" * 70)
    print(f"  MITRE ATLAS MAPPING: {name.upper()}")
    print("=" * 70)

    print(f"\n  {'Technique':<40} {'Applies':<10} {'Mitigated':<10}")
    print("  " + "-" * 60)

    for tech_id, tech_label, tech_desc in ATLAS_TECHNIQUES:
        data = atlas["scores"].get(tech_id, {"applies": False, "mitigated": False, "mitigation": ""})
        applies = "YES" if data["applies"] else "NO"
        mitigated = "YES" if data["mitigated"] else ("NO" if data["applies"] else "N/A")
        print(f"  {tech_label:<40} {applies:<10} {mitigated:<10}")

    print(f"\n  Coverage: {atlas['mitigated']}/{atlas['applies']} techniques mitigated ({atlas['coverage_pct']:.0f}%)")
    print(f"  Unmitigated: {atlas['unmitigated']} techniques")
    print()


def print_summary_table(systems: list[dict]) -> None:
    """Print side-by-side summary."""
    print("=" * 70)
    print("  SUMMARY TABLE")
    print("=" * 70)

    col_w = 30
    header = f"  {'Metric':<25}"
    for s in systems:
        header += f" {s['name']:^{col_w}}"
    print(header)
    print("  " + "-" * (25 + col_w * len(systems)))

    owasp_results = [map_owasp(s) for s in systems]
    for label, key in [("OWASP High Risks", "high"), ("OWASP Medium Risks", "medium")]:
        row = f"  {label:<25}"
        for o in owasp_results:
            row += f" {o[key]:^{col_w}}"
        print(row)

    nist_results = [map_nist(s) for s in systems]
    row = f"  {'NIST Overall Score':<25}"
    for n in nist_results:
        val = f"{n['overall']:.1f}/5.0"
        row += f" {val:^{col_w}}"
    print(row)

    atlas_results = [map_atlas(s) for s in systems]
    row = f"  {'ATLAS Mitigated':<25}"
    for a in atlas_results:
        cell = f"{a['mitigated']}/{a['applies']} ({a['coverage_pct']:.0f}%)"
        row += f" {cell:^{col_w}}"
    print(row)

    row = f"  {'ATLAS Unmitigated':<25}"
    for a in atlas_results:
        row += f" {a['unmitigated']:^{col_w}}"
    print(row)

    print()


def print_gap_analysis(systems: list[dict]) -> None:
    """Print gap analysis per system."""
    print("=" * 70)
    print("  GAP ANALYSIS")
    print("=" * 70)

    for system in systems:
        owasp = map_owasp(system)
        nist = map_nist(system)
        atlas = map_atlas(system)
        gap = find_biggest_gap(owasp, nist, atlas)

        print(f"\n  {system['name']}:")
        print(f"    Biggest Gap: {gap['biggest']['framework']}")
        print(f"    Detail:      {gap['biggest']['detail']}")
        print("    All frameworks:")
        for g in gap["all"]:
            marker = ">>>" if g["framework"] == gap["biggest"]["framework"] else "   "
            print(f"      {marker} {g['framework']:<20} Risk: {g['risk_score']:.1f}  {g['detail']}")

    print()


def print_integration_view(systems: list[dict]) -> None:
    """Print cross-framework integration view."""
    print("=" * 70)
    print("  FRAMEWORK INTEGRATION VIEW")
    print("=" * 70)

    print("\n  How the three frameworks work together:")
    print("  - OWASP identifies WHAT the risks are")
    print("  - NIST provides HOW to organize risk management")
    print("  - ATLAS explains HOW attackers will try")
    print()

    for system in systems:
        owasp = map_owasp(system)
        nist = map_nist(system)
        atlas = map_atlas(system)

        print(f"  {system['name']}:")
        print(f"    OWASP:  {owasp['high']} high-priority risks to address")
        print(f"    NIST:   {nist['overall']:.1f}/5.0 overall governance maturity")
        print(f"    ATLAS:  {atlas['unmitigated']} attack techniques without defense")

        if owasp["high"] > 2 and atlas["unmitigated"] > 3:
            print(f"    Insight: HIGH RISK -- many OWASP risks with weak ATLAS defense coverage")
        elif nist["overall"] < 3:
            print(f"    Insight: GOVERNANCE GAP -- NIST maturity below 3.0, framework needs strengthening")
        else:
            print(f"    Insight: Moderate risk profile, focus on unmitigated ATLAS techniques")

    print()


# ---------- Main ----------


def main() -> None:
    print("\n" + "=" * 70)
    print("  PART 5 -- Security Frameworks for Agentic AI")
    print("  Framework Mapper: OWASP | NIST | ATLAS")
    print("=" * 70 + "\n")

    for system in AGENT_SYSTEMS:
        print(f"\n>>> System: {system['name']}")
        print(f"    {system['purpose']}\n")

        owasp = map_owasp(system)
        nist = map_nist(system)
        atlas = map_atlas(system)

        print_owasp_mapping(system["name"], owasp)
        print_nist_mapping(system["name"], nist)
        print_atlas_mapping(system["name"], atlas)

    print_summary_table(AGENT_SYSTEMS)
    print_gap_analysis(AGENT_SYSTEMS)
    print_integration_view(AGENT_SYSTEMS)

    json_output = {
        "systems": [
            {
                "name": s["name"],
                "owasp": map_owasp(s),
                "nist": map_nist(s),
                "atlas": map_atlas(s),
            }
            for s in AGENT_SYSTEMS
        ],
    }
    json_path = "framework_mapper.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"  JSON mapping written to {json_path}\n")

    print("=" * 70)
    print("  KEY TAKEAWAY")
    print("=" * 70)
    print(textwrap.fill(
        "Use all three frameworks together: OWASP for threat modeling, NIST for "
        "governance, ATLAS for attack techniques. Each reveals different risks. "
        "Frameworks give you a foundation but don't solve security problems -- "
        "you must design controls specific to your agent's context.",
        width=66,
        initial_indent="    ",
        subsequent_indent="    ",
    ))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
