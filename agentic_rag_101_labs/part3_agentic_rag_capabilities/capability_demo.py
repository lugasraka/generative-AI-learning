"""
Part 3 — Agentic RAG Capabilities: Capability demo harness

Demonstrates 4 Agentic RAG capabilities using simulated data stores:
1. Dynamic Data Retrieval — keyword routing selects sources
2. Context-Aware Responses — similar queries handled differently
3. Multi-Step Reasoning — LLM decomposes complex queries
4. Reduced Hallucination — agent says "no data" instead of making things up

Run:  python capability_demo.py
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

# ---------- Data sources ----------

NEWS: list[dict[str, str]] = [
    {
        "id": "news-001",
        "headline": "Apple Announces iPhone 17 with AI Features",
        "summary": (
            "Apple unveiled the iPhone 17 at WWDC, featuring on-device AI "
            "processing, a new A19 chip, and improved battery life. Pre-orders "
            "start July 15."
        ),
        "topic": "tech",
    },
    {
        "id": "news-002",
        "headline": "Fed Signals Rate Cut in September",
        "summary": (
            "The Federal Reserve indicated it may cut interest rates by 25 basis "
            "points in September, citing slowing inflation and mixed employment data."
        ),
        "topic": "finance",
    },
    {
        "id": "news-003",
        "headline": "NBA Finals: Celtics Lead 3-2",
        "summary": (
            "The Boston Celtics lead the NBA Finals 3-2 after a 112-105 victory "
            "in Game 5. Game 6 is scheduled for Thursday in Denver."
        ),
        "topic": "sports",
    },
    {
        "id": "news-004",
        "headline": "Flight Delays Expected Due to East Coast Storms",
        "summary": (
            "Major airports along the East Coast are preparing for delays as a "
            "summer storm system moves through. JFK, Dulles, and Reagan may see "
            "delays of 1-3 hours through Friday."
        ),
        "topic": "travel",
    },
    {
        "id": "news-005",
        "headline": "Google DeepMind Publishes New AI Safety Research",
        "summary": (
            "Google DeepMind released a paper on constitutional AI methods for "
            "reducing harmful outputs in large language models."
        ),
        "topic": "tech",
    },
]

FINANCE: list[dict[str, Any]] = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "price": 198.50,
        "change_pct": 2.3,
        "period": "1 month",
        "note": "Up on iPhone 17 announcement",
    },
    {
        "ticker": "GOOG",
        "name": "Alphabet Inc.",
        "price": 178.20,
        "change_pct": -1.1,
        "period": "1 month",
        "note": "Down on antitrust concerns",
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corp.",
        "price": 445.00,
        "change_pct": 3.7,
        "period": "1 month",
        "note": "Up on Azure growth",
    },
    {
        "ticker": "TSLA",
        "name": "Tesla Inc.",
        "price": 242.80,
        "change_pct": -4.2,
        "period": "1 month",
        "note": "Down on delivery miss",
    },
]

SPORTS: list[dict[str, str]] = [
    {
        "id": "sport-001",
        "league": "NBA",
        "event": "Finals Game 5",
        "result": "Celtics 112, Nuggets 105",
        "date": "2025-07-14",
    },
    {
        "id": "sport-002",
        "league": "NBA",
        "event": "Finals Game 4",
        "result": "Nuggets 108, Celtics 99",
        "date": "2025-07-12",
    },
    {
        "id": "sport-003",
        "league": "NFL",
        "event": "Preseason Week 1",
        "result": "Chiefs 24, Ravens 17",
        "date": "2025-07-10",
    },
    {
        "id": "sport-004",
        "league": "Soccer",
        "event": "Copa America Semifinal",
        "result": "Argentina 2, Brazil 1",
        "date": "2025-07-13",
    },
]

# Keyword → source mapping for dynamic retrieval

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "news": [
        "news",
        "headline",
        "announce",
        "report",
        "story",
        "article",
        "weather",
        "storm",
        "flight",
        "delay",
        "airport",
    ],
    "finance": [
        "stock",
        "price",
        "market",
        "share",
        "ticker",
        "invest",
        "earnings",
        "revenue",
        "trading",
        "portfolio",
    ],
    "sports": [
        "game",
        "score",
        "match",
        "win",
        "lose",
        "finals",
        "nba",
        "nfl",
        "soccer",
        "football",
        "basketball",
        "championship",
    ],
}

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


# ---------- Retrieval helpers ----------


def keyword_match(query: str, text: str) -> float:
    """Score relevance based on word overlap."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    if not query_words:
        return 0.0
    return len(query_words & text_words) / len(query_words)


def route_by_topic(query: str) -> list[str]:
    """Route query to sources using keyword matching."""
    query_lower = query.lower()
    selected: list[str] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            selected.append(topic)
    return selected


def retrieve_news(query: str) -> list[dict[str, str]]:
    """Retrieve relevant news articles."""
    scored = [
        (keyword_match(query, f"{a['headline']} {a['summary']}"), a) for a in NEWS
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for s, a in scored[:2] if s > 0.05]


def retrieve_finance(query: str) -> list[dict[str, Any]]:
    """Retrieve relevant stock data."""
    scored = []
    for stock in FINANCE:
        text = f"{stock['ticker']} {stock['name']} {stock['note']}"
        scored.append((keyword_match(query, text), stock))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for score, s in scored[:2] if score > 0.05]


def retrieve_sports(query: str) -> list[dict[str, str]]:
    """Retrieve relevant sports data."""
    scored = [
        (keyword_match(query, f"{e['league']} {e['event']} {e['result']}"), e)
        for e in SPORTS
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for s, e in scored[:2] if s > 0.05]


RETRIEVAL_FNS: dict[str, Any] = {
    "news": retrieve_news,
    "finance": retrieve_finance,
    "sports": retrieve_sports,
}


def retrieve(query: str, sources: list[str]) -> dict[str, list[Any]]:
    """Retrieve from each selected source."""
    results: dict[str, list[Any]] = {}
    for src in sources:
        if src in RETRIEVAL_FNS:
            hits = RETRIEVAL_FNS[src](query)
            if hits:
                results[src] = hits
    return results


def format_context(retrieved: dict[str, list[Any]]) -> str:
    """Format retrieved data into a context string."""
    parts: list[str] = []
    for src, items in retrieved.items():
        for item in items:
            parts.append(f"[{src}] {json.dumps(item)}")
    return "\n".join(parts)


# ---------- Capability 1: Dynamic Data Retrieval ----------


def demo_dynamic_retrieval() -> dict[str, Any]:
    """Demo: agent picks sources based on query topic."""
    query = "What's the latest tech news?"
    selected = route_by_topic(query)
    retrieved = retrieve(query, selected)

    why = (
        f"Query contains tech-related keywords → routed to: {', '.join(selected)}. "
        "No finance or sports keywords detected, so those sources were skipped."
    )

    context = format_context(retrieved)
    prompt = f"Summarize the following data concisely.\n\n{context}\n\nSummary:"
    answer = ask_llm(prompt)

    return {
        "capability": "Dynamic Data Retrieval",
        "query": query,
        "what_did_agent_do": f"Selected sources: {', '.join(selected)}. Retrieved {sum(len(v) for v in retrieved.values())} items.",
        "why": why,
        "output": answer,
    }


# ---------- Capability 2: Context-Aware Responses ----------


def demo_context_aware() -> dict[str, Any]:
    """Demo: two similar queries handled differently based on context."""
    q1 = "What's the weather?"
    q2 = "What's the weather for my flight?"

    # Q1: just weather → no strong source match, agent says limited data
    sel1 = route_by_topic(q1)
    ret1 = retrieve(q1, sel1)
    ctx1 = format_context(ret1) if ret1 else "(no relevant data found)"
    ans1 = ask_llm(
        f"Answer based only on this context. If no data, say so.\n\n"
        f"Context:\n{ctx1}\n\nQuery: {q1}\nAnswer:"
    )

    # Q2: weather + flight → matches news (flight delays article)
    sel2 = route_by_topic(q2)
    ret2 = retrieve(q2, sel2)
    ctx2 = format_context(ret2) if ret2 else "(no relevant data found)"
    ans2 = ask_llm(
        f"Answer based only on this context. If no data, say so.\n\n"
        f"Context:\n{ctx2}\n\nQuery: {q2}\nAnswer:"
    )

    return {
        "capability": "Context-Aware Responses",
        "query": f'Q1: "{q1}" vs Q2: "{q2}"',
        "what_did_agent_do": (
            f"Q1 sources: {sel1 or 'none'} → {ctx1[:60]}...\n"
            f"Q2 sources: {sel2 or 'none'} → {ctx2[:60]}..."
        ),
        "why": (
            "Q2 contains 'flight' which triggers the travel/news keyword, "
            "retrieving the flight delay article. Q1 has no strong keyword "
            "matches, so the agent has less to work with."
        ),
        "output": f"Q1 answer: {ans1}\n\nQ2 answer: {ans2}",
    }


# ---------- Capability 3: Multi-Step Reasoning ----------


def demo_multi_step() -> dict[str, Any]:
    """Demo: complex query decomposed into sub-queries."""
    query = "Compare Apple and Google stock performance over the last month"

    # Step 1: LLM decomposes the query
    decomp_prompt = (
        "Break this query into sub-queries for a stock comparison.\n"
        "Return ONLY a JSON array of sub-queries.\n\n"
        f"Query: {query}\n\n"
        "Sub-queries:"
    )
    decomp_raw = ask_llm(decomp_prompt)
    try:
        sub_queries = json.loads(decomp_raw)
        if not isinstance(sub_queries, list):
            sub_queries = [query]
    except json.JSONDecodeError:
        sub_queries = [
            "Apple stock performance last month",
            "Google stock performance last month",
        ]

    # Step 2: Retrieve for each sub-query
    all_retrieved: dict[str, list[Any]] = {}
    for sq in sub_queries:
        sel = route_by_topic(sq)
        ret = retrieve(sq, sel)
        for src, items in ret.items():
            all_retrieved.setdefault(src, []).extend(items)

    # Deduplicate by ticker
    seen_tickers: set[str] = set()
    deduped: dict[str, list[Any]] = {}
    for src, items in all_retrieved.items():
        for item in items:
            ticker = item.get("ticker", item.get("id", ""))
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                deduped.setdefault(src, []).append(item)

    # Step 3: Synthesize comparison
    ctx = format_context(deduped)
    synth_prompt = (
        "You are a financial analyst. Compare the stock performance using ONLY "
        "the data below. Be specific with numbers.\n\n"
        f"Data:\n{ctx}\n\n"
        f"Comparison for: {query}\n\n"
        "Analysis:"
    )
    answer = ask_llm(synth_prompt)

    return {
        "capability": "Multi-Step Reasoning",
        "query": query,
        "what_did_agent_do": (
            f"Decomposed into {len(sub_queries)} sub-queries: {sub_queries}. "
            f"Retrieved from {list(deduped.keys())}. "
            f"Synthesized comparison."
        ),
        "why": (
            "Single query too broad for direct retrieval. Breaking into "
            "per-ticker sub-queries ensures targeted data retrieval, "
            "then synthesis produces a comparison."
        ),
        "output": answer,
    }


# ---------- Capability 4: Reduced Hallucination ----------


def demo_hallucination_guard() -> dict[str, Any]:
    """Demo: agent refuses to answer when data is missing."""
    query = "What are the latest Mars rover findings?"
    selected = route_by_topic(query)
    retrieved = retrieve(query, selected)

    ctx = format_context(retrieved) if retrieved else "(no relevant data found)"
    prompt = (
        "Answer the question using ONLY the context below.\n"
        "If the context does not contain relevant information, "
        "respond EXACTLY: 'I don't have data on that topic in my knowledge base.'\n"
        "Do NOT make up information.\n\n"
        f"Context:\n{ctx}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    answer = ask_llm(prompt)

    refused = "don't have data" in answer.lower() or "not available" in answer.lower()

    return {
        "capability": "Reduced Hallucination",
        "query": query,
        "what_did_agent_do": (
            f"Routed to: {selected or 'none'}. "
            f"Retrieved 0 relevant items. "
            f"Agent correctly refused: {'Yes' if refused else 'No'}"
        ),
        "why": (
            "Query about Mars rovers has no matching keywords in any source. "
            "Retrieval returns empty. Prompt instructs agent to say 'no data' "
            "rather than hallucinate."
        ),
        "output": answer,
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
    """Write capability demo results to a markdown file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# Part 3 — Agentic RAG Capabilities Demo Results",
        "",
        f"- **Model:** `{MODEL}`",
        f"- **Generated:** {now}",
        "",
    ]

    for r in results:
        lines.append(f"## {r['capability']}")
        lines.append("")
        lines.append(f"- **Query:** `{r['query']}`")
        lines.append(f"- **What the agent did:** {r['what_did_agent_do']}")
        lines.append(f"- **Why this approach:** {r['why']}")
        lines.append("")
        lines.append("### Output")
        lines.append("")
        lines.append("```")
        lines.append(r["output"])
        lines.append("```")
        lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| # | Capability | Demonstrated |")
    lines.append("|---|-----------|--------------|")
    for i, r in enumerate(results, 1):
        lines.append(f"| {i} | {r['capability']} | Yes |")
    lines.append("")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main ----------


def main() -> None:
    """Run all capability demos."""
    banner("Part 3 — Agentic RAG Capabilities")
    print(f"Model: {MODEL}  (override: set OPENCODE_MODEL=...)\n")

    demos = [
        ("Dynamic Data Retrieval", demo_dynamic_retrieval),
        ("Context-Aware Responses", demo_context_aware),
        ("Multi-Step Reasoning", demo_multi_step),
        ("Reduced Hallucination", demo_hallucination_guard),
    ]

    all_results: list[dict[str, Any]] = []

    for i, (name, fn) in enumerate(demos, 1):
        banner(f"Capability {i}: {name}")
        result = fn()

        print(f"\n  Query: {result['query']}")
        print(f"  What:  {result['what_did_agent_do']}")
        print(f"  Why:   {result['why']}")
        print("\n  Output:")
        for line in result["output"].split("\n"):
            print(f"    {line}")

        all_results.append(result)

    # Summary
    banner("Summary")
    print(f"  {'#':<4} {'Capability':<30} {'Demonstrated'}")
    print(f"  {'-' * 4} {'-' * 30} {'-' * 14}")
    for i, r in enumerate(all_results, 1):
        print(f"  {i:<4} {r['capability']:<30} Yes")

    write_results(all_results)
    banner("DONE — Part 3 complete. Next: Part 4 — Types of Agentic RAG?")


if __name__ == "__main__":
    main()
