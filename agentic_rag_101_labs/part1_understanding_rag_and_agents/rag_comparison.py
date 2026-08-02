"""
Part 1 — Understanding RAG and Agents: Side-by-side comparison

Implements three systems — Plain LLM, Basic RAG, and Agentic RAG — and runs
the same questions through each to highlight the differences.

Run:  python rag_comparison.py
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

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")

# ---------- Document stores ----------

COMPANY_DOCS: list[dict[str, str]] = [
    {
        "id": "travel-001",
        "title": "Travel Policy",
        "content": (
            "All domestic flights must be booked at least 14 days in advance. "
            "Hotel stays are capped at $200/night. Rental cars require manager "
            "approval for trips under 3 days. Receipts must be submitted within "
            "30 days of travel completion."
        ),
    },
    {
        "id": "expense-002",
        "title": "Expense Reimbursement",
        "content": (
            "Expenses under $50 do not require receipts but need a written "
            "justification. Meals during travel are reimbursed up to $75/day. "
            "International expenses must be converted to USD at the rate on the "
            "date of the transaction. Submit claims via the expense portal."
        ),
    },
    {
        "id": "holiday-003",
        "title": "Company Holidays 2025",
        "content": (
            "Office is closed on: Jan 1 (New Year's), May 26 (Memorial Day), "
            "Jul 4 (Independence Day), Sep 1 (Labor Day), Nov 27-28 "
            "(Thanksgiving), Dec 25-26 (Christmas). Floating holidays: 2 per year."
        ),
    },
]

TECH_KB: list[dict[str, str]] = [
    {
        "id": "api-001",
        "title": "API Rate Limits",
        "content": (
            "Free tier: 60 requests/minute, 1000 requests/day. Pro tier: "
            "600 requests/minute, 50000 requests/day. Enterprise: custom limits. "
            "Rate limit headers are included in every response: X-RateLimit-Remaining "
            "and X-RateLimit-Reset."
        ),
    },
    {
        "id": "deploy-002",
        "title": "Deployment Steps",
        "content": (
            "1) Run 'make test' locally. 2) Push to staging branch. 3) Wait for "
            "CI green check. 4) Open a PR with deployment notes. 5) After approval, "
            "merge to main triggers automatic deploy via GitHub Actions."
        ),
    },
    {
        "id": "incident-003",
        "title": "Incident Response",
        "content": (
            "Severity 1 (full outage): page on-call immediately, start incident "
            "bridge. Severity 2 (degraded): notify team in #incidents, investigate "
            "within 1 hour. Severity 3 (minor): file a ticket, address in next sprint."
        ),
    },
]

HR_HANDBOOK: list[dict[str, str]] = [
    {
        "id": "remote-001",
        "title": "Remote Work Policy",
        "content": (
            "Employees may work remotely up to 3 days per week with manager "
            "approval. Full remote requires VP sign-off and a signed remote work "
            "agreement. Core hours are 10am-3pm in the employee's local timezone."
        ),
    },
    {
        "id": "pto-002",
        "title": "PTO Policy",
        "content": (
            "New hires accrue 15 days PTO per year. After 3 years: 20 days. "
            "After 7 years: 25 days. PTO rolls over up to 5 days. Unused PTO "
            "beyond the cap is forfeited on Dec 31. PTO must be requested at "
            "least 1 week in advance."
        ),
    },
    {
        "id": "onboard-003",
        "title": "Onboarding Process",
        "content": (
            "Day 1: orientation and laptop setup. Week 1: buddy pairing and "
            "team intro meetings. Month 1: complete compliance training and "
            "first project deliverable. Manager checks in at day 30, 60, and 90."
        ),
    },
]

ALL_SOURCES: dict[str, list[dict[str, str]]] = {
    "company_docs": COMPANY_DOCS,
    "tech_kb": TECH_KB,
    "hr_handbook": HR_HANDBOOK,
}

SOURCE_DESCRIPTIONS: dict[str, str] = {
    "company_docs": "Company policies (travel, expenses, holidays)",
    "tech_kb": "Technical knowledge base (APIs, deployment, incidents)",
    "hr_handbook": "HR handbook (remote work, PTO, onboarding)",
}

# ---------- Test questions ----------

TESTS: list[dict[str, str | list[str]]] = [
    {
        "question": "What is 2 + 2?",
        "difficulty": "easy",
        "expected_keywords": ["4"],
        "note": "Should be answerable by plain LLM — no retrieval needed",
    },
    {
        "question": "What is the company travel policy?",
        "difficulty": "requires retrieval",
        "expected_keywords": ["travel", "booked", "14 days", "hotel", "$200"],
        "note": "Needs retrieval from company_docs",
    },
    {
        "question": "What are the API rate limits and PTO policy?",
        "difficulty": "multi-source",
        "expected_keywords": ["rate limit", "60", "1000", "PTO", "15 days"],
        "note": "Needs tech_kb AND hr_handbook — only agentic RAG should handle both",
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


# ---------- Retrieval helpers ----------


def keyword_score(query: str, text: str) -> float:
    """Score how relevant a text chunk is to a query based on keyword overlap."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    if not query_words:
        return 0.0
    overlap = query_words & text_words
    return len(overlap) / len(query_words)


def retrieve_top(
    documents: list[dict[str, str]], query: str, top_k: int = 2
) -> list[dict[str, str]]:
    """Return the top_k most relevant documents for a query."""
    scored = [(keyword_score(query, doc["content"]), doc) for doc in documents]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def retrieve_all_sources(query: str) -> dict[str, list[dict[str, str]]]:
    """Retrieve top documents from every source."""
    results: dict[str, list[dict[str, str]]] = {}
    for name, docs in ALL_SOURCES.items():
        hits = retrieve_top(docs, query, top_k=2)
        if hits:
            results[name] = hits
    return results


# ---------- System 1: Plain LLM ----------


def plain_llm(query: str) -> dict[str, str | bool]:
    """Answer using only the LLM's built-in knowledge — no retrieval."""
    prompt = (
        "Answer the following question directly and concisely.\n"
        "If you do not know the answer, say 'I don't know'.\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    answer = ask_llm(prompt)
    return {"answer": answer, "used_retrieval": False}


# ---------- System 2: Basic RAG ----------


def basic_rag(query: str) -> dict[str, str | bool]:
    """Retrieve from company_docs only, then answer."""
    hits = retrieve_top(COMPANY_DOCS, query, top_k=2)
    context = "\n\n".join(f"[{doc['title']}]\n{doc['content']}" for doc in hits)
    prompt = (
        "You are a helpful assistant. Use ONLY the context below to answer.\n"
        "If the context does not contain enough information, say so.\n\n"
        f"--- Context ---\n{context}\n--- End Context ---\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    answer = ask_llm(prompt)
    return {"answer": answer, "used_retrieval": True}


# ---------- System 3: Agentic RAG ----------


def agentic_rag(query: str) -> dict[str, str | bool]:
    """Agent decides which sources to query, retrieves, then synthesizes."""

    source_list = "\n".join(
        f"- {name}: {desc}" for name, desc in SOURCE_DESCRIPTIONS.items()
    )

    plan_prompt = (
        "You are an agent with access to these data sources:\n"
        f"{source_list}\n\n"
        "Given the user's question, decide which sources to query.\n"
        'Respond with ONLY a JSON object: {"sources": ["source_name", ...]}\n\n'
        f"Question: {query}\n\n"
        "Which sources should I query?"
    )
    plan_response = ask_llm(plan_prompt)

    try:
        parsed = json.loads(plan_response)
        selected = parsed.get("sources", [])
    except (json.JSONDecodeError, AttributeError):
        selected = list(ALL_SOURCES.keys())

    selected = [s for s in selected if s in ALL_SOURCES]
    if not selected:
        selected = list(ALL_SOURCES.keys())

    context_parts: list[str] = []
    for source_name in selected:
        hits = retrieve_top(ALL_SOURCES[source_name], query, top_k=2)
        for doc in hits:
            context_parts.append(f"[{source_name} / {doc['title']}]\n{doc['content']}")

    context = "\n\n".join(context_parts)
    synth_prompt = (
        "You are a helpful assistant. Use ONLY the context below to answer.\n"
        "If the context does not contain enough information, say so.\n\n"
        f"--- Context ---\n{context}\n--- End Context ---\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    answer = ask_llm(synth_prompt)
    return {"answer": answer, "used_retrieval": True}


# ---------- Evaluation ----------


def score_answer(answer: str, expected_keywords: list[str]) -> tuple[bool, float]:
    """Check whether the answer contains the expected keywords."""
    lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in lower)
    ratio = hits / len(expected_keywords) if expected_keywords else 0.0
    return ratio >= 0.5, ratio


# ---------- Display ----------


def banner(title: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate text for display."""
    text = text.replace("\n", " ")
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


# ---------- Markdown output ----------

RESULTS_PATH = Path(__file__).parent / "results.md"


def write_results(
    sections: list[dict[str, Any]],
    model: str,
) -> None:
    """Write comparison results to a markdown file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# Part 1 — RAG Comparison Results",
        "",
        f"- **Model:** `{model}`",
        f"- **Generated:** {now}",
        "",
    ]

    for sec in sections:
        lines.append(f"## Question {sec['index']}: {sec['question']}")
        lines.append("")
        lines.append(f"- **Difficulty:** {sec['difficulty']}")
        lines.append(f"- **Note:** {sec['note']}")
        lines.append("")
        lines.append("| System | Retrieval | Correct | Answer |")
        lines.append("|--------|-----------|---------|--------|")
        for row in sec["rows"]:
            escaped = row["Answer"].replace("|", "\\|")
            lines.append(
                f"| {row['System']} | {row['Retrieval']} "
                f"| {row['Correct']} | {escaped} |"
            )
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    total_correct = sum(
        1 for sec in sections for row in sec["rows"] if row["Correct"].startswith("Yes")
    )
    total_rows = sum(len(sec["rows"]) for sec in sections)
    lines.append(f"- **Total correct:** {total_correct}/{total_rows}")
    lines.append("")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main comparison ----------


def main() -> None:
    """Run all three systems on each test question and print a comparison."""
    banner("Part 1 — Understanding RAG and Agents")
    print(f"Model: {MODEL}  (override: set OPENCODE_MODEL=...)\n")

    systems: dict[str, Any] = {
        "Plain LLM": plain_llm,
        "Basic RAG": basic_rag,
        "Agentic RAG": agentic_rag,
    }

    sections: list[dict[str, Any]] = []

    for i, test in enumerate(TESTS, 1):
        q = test["question"]
        banner(f"Question {i} ({test['difficulty']}): {q}")
        print(f"  Note: {test['note']}\n")

        rows: list[dict[str, str]] = []
        for sys_name, sys_fn in systems.items():
            result = sys_fn(q)
            correct, ratio = score_answer(
                result["answer"],
                test["expected_keywords"],  # type: ignore[arg-type]
            )
            rows.append(
                {
                    "System": sys_name,
                    "Retrieval": "Yes" if result["used_retrieval"] else "No",
                    "Correct": f"Yes ({ratio:.0%})" if correct else "No",
                    "Answer": truncate(result["answer"]),
                }
            )

        header = f"{'System':<15} {'Retrieval':<10} {'Correct':<12} Answer"
        print(header)
        print("-" * 72)
        for row in rows:
            print(
                f"{row['System']:<15} {row['Retrieval']:<10} "
                f"{row['Correct']:<12} {row['Answer']}"
            )
        print()

        sections.append(
            {
                "index": i,
                "question": q,
                "difficulty": test["difficulty"],
                "note": test["note"],
                "rows": rows,
            }
        )

    write_results(sections, MODEL)
    banner("DONE — Part 1 complete. Next: Part 2 — What is Agentic RAG?")


if __name__ == "__main__":
    main()
