"""
Part 4 — Types of Agentic RAG: Architecture selector

Classifies 10 task descriptions into the right Agentic RAG architecture
(Single-Agent, Multi-Agent, Hierarchical) using keyword signals, then
outputs a summary table with statistics.

Run:  python architecture_selector.py
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

# ---------- Architecture definitions ----------

ARCHITECTURES: dict[str, dict[str, Any]] = {
    "Single-Agent": {
        "keywords": [
            "find",
            "lookup",
            "what is",
            "simple",
            "search",
            "get",
            "check",
            "look up",
            "retrieve",
            "fetch",
            "list",
            "show",
        ],
        "agents": 1,
        "description": "One agent manages the entire retrieval and generation process.",
        "color": "#3b82f6",
    },
    "Multi-Agent": {
        "keywords": [
            "compare",
            "multiple",
            "research",
            "comprehensive",
            "analyze",
            "cross-reference",
            "synthesize",
            "aggregate",
            "summarize all",
            "across",
            "all sources",
            "multifaceted",
        ],
        "agents": "2-3",
        "description": "Multiple agents collaborate, each handling different retrieval aspects.",
        "color": "#22c55e",
    },
    "Hierarchical": {
        "keywords": [
            "prioritize",
            "critical",
            "enterprise",
            "audit",
            "compliance",
            "governance",
            "escalate",
            "regulatory",
            "policy review",
            "risk assessment",
            "approval",
            "oversight",
        ],
        "agents": "3-5",
        "description": "Agents organized in a hierarchy. Higher-level agents supervise; lower-level agents execute.",
        "color": "#a855f7",
    },
}

# ---------- Test tasks ----------

TASKS: list[dict[str, str]] = [
    {
        "task": "Find the latest stock price of Apple",
        "expected": "Single-Agent",
    },
    {
        "task": "Compare AI regulation policies across US, EU, and China",
        "expected": "Multi-Agent",
    },
    {
        "task": "Audit our vendor contracts for compliance risks",
        "expected": "Hierarchical",
    },
    {
        "task": "What is our company's travel policy?",
        "expected": "Single-Agent",
    },
    {
        "task": "Research all competitors' pricing strategies",
        "expected": "Multi-Agent",
    },
    {
        "task": "Prioritize security vulnerabilities by criticality",
        "expected": "Hierarchical",
    },
    {
        "task": "Look up employee handbook section on remote work",
        "expected": "Single-Agent",
    },
    {
        "task": "Analyze customer sentiment across all review platforms",
        "expected": "Multi-Agent",
    },
    {
        "task": "Enterprise-wide compliance report for Q2",
        "expected": "Hierarchical",
    },
    {
        "task": "Get the current weather in New York",
        "expected": "Single-Agent",
    },
]

# ---------- Classification logic ----------


def classify_task(task: str) -> dict[str, Any]:
    """Classify a task into an architecture using keyword signals."""
    task_lower = task.lower()
    scores: dict[str, list[str]] = {}

    for arch_name, arch_info in ARCHITECTURES.items():
        matched = [kw for kw in arch_info["keywords"] if kw in task_lower]
        scores[arch_name] = matched

    # Pick architecture with most keyword matches
    best_arch = max(scores, key=lambda k: len(scores[k]))
    matched_keywords = scores[best_arch]

    # If no keywords matched, default to Single-Agent
    if not matched_keywords:
        best_arch = "Single-Agent"
        matched_keywords = ["(default — no strong signals)"]

    # Estimate complexity
    total_matches = sum(len(v) for v in scores.values())
    if total_matches >= 4:
        complexity = "high"
    elif total_matches >= 2:
        complexity = "medium"
    else:
        complexity = "low"

    arch_info = ARCHITECTURES[best_arch]

    return {
        "task": task,
        "architecture": best_arch,
        "why": f"Matched keywords: {', '.join(matched_keywords)}",
        "complexity": complexity,
        "agents": arch_info["agents"],
        "description": arch_info["description"],
        "all_scores": {k: len(v) for k, v in scores.items()},
    }


def suggest_hybrid(classifications: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Identify tasks that could benefit from a second architecture."""
    hybrids: list[dict[str, str]] = []
    for c in classifications:
        scores = c["all_scores"]
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) >= 2:
            top, second = sorted_scores[0], sorted_scores[1]
            if second[1] > 0 and top[1] - second[1] <= 1:
                hybrids.append(
                    {
                        "task": c["task"],
                        "primary": top[0],
                        "secondary": second[0],
                        "reason": (
                            f"Strong signals for both {top[0]} ({top[1]} matches) "
                            f"and {second[0]} ({second[1]} matches). "
                            f"Could use {top[0]} for initial query, "
                            f"{second[0]} for follow-up analysis."
                        ),
                    }
                )
    return hybrids


# ---------- Display ----------


def banner(title: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------- Markdown output ----------

RESULTS_PATH = Path(__file__).parent / "results.md"


def write_results(
    classifications: list[dict[str, Any]],
    hybrids: list[dict[str, str]],
) -> None:
    """Write classification results to a markdown file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Stats
    arch_counts: dict[str, int] = {}
    complexity_counts: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
    for c in classifications:
        arch_counts[c["architecture"]] = arch_counts.get(c["architecture"], 0) + 1
        complexity_counts[c["complexity"]] = (
            complexity_counts.get(c["complexity"], 0) + 1
        )

    lines: list[str] = [
        "# Part 4 — Types of Agentic RAG: Results",
        "",
        f"- **Generated:** {now}",
        f"- **Total tasks:** {len(classifications)}",
        "",
        "## Classification Results",
        "",
        "| # | Task | Architecture | Complexity | Agents | Why |",
        "|---|------|-------------|------------|--------|-----|",
    ]

    for i, c in enumerate(classifications, 1):
        task_short = c["task"][:50] + ("..." if len(c["task"]) > 50 else "")
        why_short = c["why"][:60] + ("..." if len(c["why"]) > 60 else "")
        lines.append(
            f"| {i} | {task_short} | {c['architecture']} "
            f"| {c['complexity']} | {c['agents']} | {why_short} |"
        )

    lines.append("")
    lines.append("## Statistics")
    lines.append("")
    lines.append("### By Architecture")
    lines.append("")
    lines.append("| Architecture | Count | Percentage |")
    lines.append("|-------------|-------|------------|")
    for arch in ["Single-Agent", "Multi-Agent", "Hierarchical"]:
        count = arch_counts.get(arch, 0)
        pct = count / len(classifications) * 100
        lines.append(f"| {arch} | {count} | {pct:.0f}% |")

    lines.append("")
    lines.append("### By Complexity")
    lines.append("")
    lines.append("| Complexity | Count |")
    lines.append("|-----------|-------|")
    for level in ["low", "medium", "high"]:
        lines.append(f"| {level.title()} | {complexity_counts[level]} |")

    if hybrids:
        lines.append("")
        lines.append("## Hybrid Recommendations")
        lines.append("")
        for h in hybrids:
            lines.append(f"- **{h['task']}**")
            lines.append(f"  - Primary: {h['primary']}, Secondary: {h['secondary']}")
            lines.append(f"  - {h['reason']}")
            lines.append("")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main ----------


def main() -> None:
    """Classify all tasks and print results."""
    banner("Part 4 — Types of Agentic RAG")

    classifications: list[dict[str, Any]] = []
    for t in TASKS:
        result = classify_task(t["task"])
        result["expected"] = t["expected"]
        classifications.append(result)

    # Print table
    header = f"{'#':<4} {'Task':<50} {'Architecture':<15} {'Complexity':<10} {'Agents':<8} {'Match'}"
    print(f"\n{header}")
    print("-" * 110)
    for i, c in enumerate(classifications, 1):
        task_short = c["task"][:47] + ("..." if len(c["task"]) > 47 else "")
        correct = "OK" if c["architecture"] == c["expected"] else "DIFF"
        print(
            f"{i:<4} {task_short:<50} {c['architecture']:<15} "
            f"{c['complexity']:<10} {str(c['agents']):<8} {correct}"
        )

    # Stats
    arch_counts: dict[str, int] = {}
    for c in classifications:
        arch_counts[c["architecture"]] = arch_counts.get(c["architecture"], 0) + 1

    banner("Statistics")
    for arch in ["Single-Agent", "Multi-Agent", "Hierarchical"]:
        count = arch_counts.get(arch, 0)
        bar = "#" * (count * 5)
        print(f"  {arch:<15} {count:>2}  {bar}")

    # Hybrid suggestions
    hybrids = suggest_hybrid(classifications)
    if hybrids:
        banner("Hybrid Recommendations")
        for h in hybrids:
            print(f"  {h['task']}")
            print(f"    → Primary: {h['primary']}, Secondary: {h['secondary']}")
            print(f"    → {h['reason']}")
            print()

    write_results(classifications, hybrids)
    banner("DONE — Part 4 complete. Next: Part 5 — Implementing Agentic RAG?")


if __name__ == "__main__":
    main()
