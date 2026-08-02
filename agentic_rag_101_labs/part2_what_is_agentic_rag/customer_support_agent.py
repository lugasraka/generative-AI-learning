"""
Part 2 — What is Agentic RAG?: Customer support agent simulation

Simulates the 7-step Agentic RAG flow for an ISP support scenario.
Agent uses keyword routing (no LLM) for source selection and LLM for
analysis, generation, and follow-up suggestions.

Run:  python customer_support_agent.py
"""

import datetime
import json
import os
import subprocess
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
CONFIDENCE_THRESHOLD = 0.3

# ---------- Data sources ----------

SERVICE_HISTORY: dict[str, list[dict[str, str]]] = {
    "downtown": [
        {
            "date": "2025-07-15",
            "issue": "Complete outage for 4 hours",
            "resolved": "Yes",
        },
        {
            "date": "2025-07-08",
            "issue": "Intermittent slow speeds during peak hours",
            "resolved": "Yes",
        },
        {"date": "2025-06-20", "issue": "DNS resolution failures", "resolved": "Yes"},
    ],
    "midtown": [
        {"date": "2025-07-12", "issue": "Slow upload speeds", "resolved": "No"},
        {
            "date": "2025-06-30",
            "issue": "Router reboot required after power outage",
            "resolved": "Yes",
        },
    ],
    "suburbs": [
        {
            "date": "2025-07-18",
            "issue": "Fiber cut affecting 200 homes",
            "resolved": "Yes",
        },
        {
            "date": "2025-07-01",
            "issue": "WiFi dead spots in new development",
            "resolved": "No",
        },
    ],
}

NETWORK_REPORTS: dict[str, list[dict[str, str]]] = {
    "morning": [
        {"metric": "avg_speed", "value": "95 Mbps", "status": "normal"},
        {"metric": "congestion", "value": "12%", "status": "low"},
        {"metric": "latency", "value": "8ms", "status": "normal"},
    ],
    "evening": [
        {"metric": "avg_speed", "value": "42 Mbps", "status": "degraded"},
        {"metric": "congestion", "value": "78%", "status": "high"},
        {"metric": "latency", "value": "45ms", "status": "elevated"},
    ],
    "night": [
        {"metric": "avg_speed", "value": "88 Mbps", "status": "normal"},
        {"metric": "congestion", "value": "20%", "status": "low"},
        {"metric": "latency", "value": "10ms", "status": "normal"},
    ],
}

KNOWLEDGE_BASE: list[dict[str, str]] = [
    {
        "id": "kb-001",
        "title": "Slow Internet: Peak Hours",
        "content": (
            "During peak hours (6-10 PM), network congestion can reduce speeds by "
            "40-60%. This is normal for shared bandwidth neighborhoods. Solutions: "
            "use wired connection for critical tasks, schedule large downloads for "
            "off-peak hours, or upgrade to a higher tier plan."
        ),
    },
    {
        "id": "kb-002",
        "title": "Router Troubleshooting",
        "content": (
            "Step 1: Unplug router for 30 seconds, plug back in. Step 2: Check all "
            "cable connections. Step 3: Verify WiFi password hasn't changed. "
            "Step 4: Test with ethernet cable to rule out WiFi issues. Step 5: "
            "Check for firmware updates at router admin page (192.168.1.1)."
        ),
    },
    {
        "id": "kb-003",
        "title": "Port Forwarding Setup",
        "content": (
            "1) Log into router admin (192.168.1.1). 2) Go to Advanced > Port "
            "Forwarding. 3) Add new rule: external port, internal IP, internal port, "
            "protocol (TCP/UDP). 4) Save and restart router. Common ports: 80 (HTTP), "
            "443 (HTTPS), 25565 (Minecraft), 3074 (Xbox Live)."
        ),
    },
    {
        "id": "kb-004",
        "title": "Outage Reporting",
        "content": (
            "Check status at status.example.com. If outage is listed, wait for "
            "updates. If not listed, report via the app or call 1-800-555-HELP. "
            "Include: address, time issue started, affected devices. Outages are "
            "typically resolved within 2-4 hours."
        ),
    },
    {
        "id": "kb-005",
        "title": "WiFi Coverage Optimization",
        "content": (
            "Place router in central, elevated location. Avoid metal objects and "
            "microwave interference. For multi-story homes, place router on the "
            "middle floor. Consider mesh WiFi extenders for homes over 2000 sq ft. "
            "Use 5GHz band for speed, 2.4GHz for range."
        ),
    },
]

# Source routing keywords (used for step 3 — no LLM)

SOURCE_KEYWORDS: dict[str, list[str]] = {
    "service_history": [
        "outage",
        "downtime",
        "last week",
        "last month",
        "complaint",
        "issue",
        "problem",
        "ticket",
        "incident",
        "neighborhood",
        "downtown",
        "midtown",
        "suburbs",
    ],
    "network_reports": [
        "speed",
        "slow",
        "fast",
        "congestion",
        "latency",
        "evening",
        "morning",
        "night",
        "peak",
        "bandwidth",
        "mbps",
        "throughput",
    ],
    "knowledge_base": [
        "how",
        "setup",
        "install",
        "configure",
        "troubleshoot",
        "fix",
        "restart",
        "router",
        "wifi",
        "password",
        "port",
        "forwarding",
        "optimize",
        "extend",
        "coverage",
    ],
}

# ---------- Test queries ----------

TESTS: list[dict[str, Any]] = [
    {
        "query": "Why is my internet slow in the evenings?",
        "note": "Needs network_reports + knowledge_base (peak hours article)",
    },
    {
        "query": "I had an outage last week in downtown",
        "note": "Needs service_history + knowledge_base (outage reporting)",
    },
    {
        "query": "How do I set up port forwarding?",
        "note": "Needs knowledge_base only",
    },
]

# ---------- LLM via opencode CLI ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode CLI and return the response text."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Keyword routing (no LLM) ----------


def keyword_score(query: str, text: str) -> float:
    """Score relevance between a query and text based on word overlap."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    if not query_words:
        return 0.0
    overlap = query_words & text_words
    return len(overlap) / len(query_words)


def route_sources(query: str) -> list[str]:
    """Decide which sources to query using keyword matching (no LLM)."""
    query_lower = query.lower()
    selected: list[str] = []
    for source_name, keywords in SOURCE_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            selected.append(source_name)
    return selected if selected else list(SOURCE_KEYWORDS.keys())


def retrieve_from_service_history(
    query: str,
    neighborhoods: list[str] | None = None,
) -> list[dict[str, str]]:
    """Retrieve relevant service history entries."""
    results: list[dict[str, str]] = []
    search_areas = neighborhoods or list(SERVICE_HISTORY.keys())
    for area in search_areas:
        if area in SERVICE_HISTORY:
            for entry in SERVICE_HISTORY[area]:
                if keyword_score(query, entry["issue"]) > 0.1:
                    results.append({"neighborhood": area, **entry})
    return results[:5]


def retrieve_from_network_reports(query: str) -> list[dict[str, str]]:
    """Retrieve relevant network report entries."""
    results: list[dict[str, str]] = []
    for period, metrics in NETWORK_REPORTS.items():
        for metric in metrics:
            text = f"{period} {metric['metric']} {metric['value']} {metric['status']}"
            if keyword_score(query, text) > 0.1:
                results.append({"period": period, **metric})
    return results[:5]


def retrieve_from_knowledge_base(query: str) -> list[dict[str, str]]:
    """Retrieve relevant knowledge base articles."""
    scored = [
        (keyword_score(query, f"{a['title']} {a['content']}"), a)
        for a in KNOWLEDGE_BASE
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for score, a in scored[:2] if score > 0.05]


# ---------- Retrieval dispatcher ----------


def retrieve(query: str, sources: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Fetch data from each selected source."""
    results: dict[str, list[dict[str, Any]]] = {}
    if "service_history" in sources:
        results["service_history"] = retrieve_from_service_history(query)
    if "network_reports" in sources:
        results["network_reports"] = retrieve_from_network_reports(query)
    if "knowledge_base" in sources:
        results["knowledge_base"] = retrieve_from_knowledge_base(query)
    return results


def compute_confidence(retrieved: dict[str, list[dict[str, Any]]]) -> float:
    """Estimate confidence based on how much data was retrieved."""
    total = sum(len(v) for v in retrieved.values())
    if total == 0:
        return 0.0
    if total >= 4:
        return 0.9
    if total >= 2:
        return 0.7
    return 0.4


# ---------- 7-step agent loop ----------


def run_agent(query: str) -> dict[str, Any]:
    """Execute the full 7-step Agentic RAG flow."""
    steps: list[dict[str, Any]] = []
    transcript: list[str] = []

    def log(step_num: int, name: str, detail: str) -> None:
        header = f"Step {step_num}: {name}"
        transcript.append(f"\n{'─' * 60}")
        transcript.append(header)
        transcript.append(f"{'─' * 60}")
        transcript.append(detail)
        steps.append({"step": step_num, "name": name, "detail": detail})

    # Step 1: Receive query
    log(1, "Receive Query", f'"{query}"')

    # Step 2: Analyze query (LLM)
    analysis_prompt = (
        "Analyze this customer support query. Extract:\n"
        "- intent (what the customer wants)\n"
        "- entities (locations, times, technical terms)\n"
        "- urgency (low/medium/high)\n\n"
        'Respond as JSON: {"intent": "...", "entities": [...], "urgency": "..."}\n\n'
        f"Query: {query}"
    )
    analysis_raw = ask_llm(analysis_prompt)
    try:
        analysis = json.loads(analysis_raw)
    except json.JSONDecodeError:
        analysis = {"intent": "unknown", "entities": [], "urgency": "medium"}
    log(2, "Analyze Query", json.dumps(analysis, indent=2))

    # Step 3: Decide sources (keyword routing — no LLM)
    selected_sources = route_sources(query)
    log(3, "Decide Sources", f"Selected: {', '.join(selected_sources)}")

    # Step 4: Retrieve
    retrieved = retrieve(query, selected_sources)
    retrieve_summary = []
    for src, items in retrieved.items():
        retrieve_summary.append(f"  {src}: {len(items)} result(s)")
    log(
        4,
        "Retrieve Data",
        "\n".join(retrieve_summary) if retrieve_summary else "  No results",
    )

    # Step 5: Generate response (LLM)
    confidence = compute_confidence(retrieved)
    if confidence < CONFIDENCE_THRESHOLD:
        answer = (
            "I'm not confident I have enough information to answer this accurately. "
            "Let me escalate this to a human agent who can look into it further."
        )
    else:
        context_parts: list[str] = []
        for src, items in retrieved.items():
            for item in items:
                context_parts.append(f"[{src}] {json.dumps(item)}")
        context = "\n".join(context_parts)

        gen_prompt = (
            "You are a helpful ISP customer support agent.\n"
            "Use ONLY the context below to answer the customer's question.\n"
            "Be specific and cite the data you used.\n"
            "If the context is insufficient, say so.\n\n"
            f"--- Context ---\n{context}\n--- End Context ---\n\n"
            f"Customer: {query}\n\n"
            "Agent response:"
        )
        answer = ask_llm(gen_prompt)
    log(5, "Generate Response", answer)

    # Step 6: Deliver
    log(6, "Deliver Response", answer)

    # Step 7: Follow-up (LLM)
    followup_prompt = (
        "Based on this customer support interaction, suggest ONE follow-up action "
        "or question. Be concise (1 sentence).\n\n"
        f"Customer: {query}\n"
        f"Agent: {answer}\n\n"
        "Follow-up:"
    )
    followup = ask_llm(followup_prompt)
    log(7, "Follow-up", followup)

    return {
        "query": query,
        "analysis": analysis,
        "sources": selected_sources,
        "confidence": confidence,
        "answer": answer,
        "followup": followup,
        "steps": steps,
        "transcript": "\n".join(transcript),
    }


# ---------- Display ----------


def banner(title: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------- Markdown output ----------

RESULTS_PATH = Path(__file__).parent / "results.md"


def write_results(results: list[dict[str, Any]]) -> None:
    """Write all agent runs to a markdown file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# Part 2 — Customer Support Agent Results",
        "",
        f"- **Model:** `{MODEL}`",
        f"- **Generated:** {now}",
        f"- **Confidence threshold:** {CONFIDENCE_THRESHOLD}",
        "",
    ]

    for i, r in enumerate(results, 1):
        lines.append(f"## Query {i}: {r['query']}")
        lines.append("")
        lines.append(f"- **Sources queried:** {', '.join(r['sources'])}")
        lines.append(f"- **Confidence:** {r['confidence']:.0%}")
        lines.append(f"- **Follow-up:** {r['followup']}")
        lines.append("")
        lines.append("### Agent transcript")
        lines.append("")
        lines.append("```")
        lines.append(r["transcript"])
        lines.append("```")
        lines.append("")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main ----------


def main() -> None:
    """Run the agent on all test queries."""
    banner("Part 2 — What is Agentic RAG?")
    print(f"Model: {MODEL}  (override: set OPENCODE_MODEL=...)\n")

    all_results: list[dict[str, Any]] = []

    for i, test in enumerate(TESTS, 1):
        banner(f"Query {i}: {test['query']}")
        print(f"  Note: {test['note']}\n")

        result = run_agent(test["query"])
        print(result["transcript"])

        print(f"\n  Confidence: {result['confidence']:.0%}")
        print(f"  Sources used: {', '.join(result['sources'])}")

        all_results.append(result)

    write_results(all_results)
    banner("DONE — Part 2 complete. Next: Part 3 — Agentic RAG Capabilities?")


if __name__ == "__main__":
    main()
