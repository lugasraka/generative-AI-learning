"""
Part 4 — Agents in the Real World: Agent Archetype Classifier

Classifies task descriptions into agent archetypes and outputs the
required harness components for each. Demonstrates real-world agent taxonomy.

Run:  python agent_archetype_classifier.py
"""

import sys
import json
from collections import Counter


# ---------- Archetype definitions ----------

ARCHETYPES = {
    "coding": {
        "description": "Plans, edits files, runs code, and verifies",
        "tools": ["file_system", "code_execution", "terminal", "git"],
        "memory": "session",
        "planning": "iterative with reflection",
        "safety": ["sandbox", "no_network_by_default"],
    },
    "computer_use": {
        "description": "Operates a screen or browser to complete tasks across apps",
        "tools": ["browser_control", "screenshot", "keyboard", "mouse"],
        "memory": "short-term",
        "planning": "visual_step_by_step",
        "safety": ["rate_limiting", "confirm_before_actions"],
    },
    "deep_research": {
        "description": "Plans a research question, searches the web, synthesizes a cited report",
        "tools": ["web_search", "page_fetch", "summarization", "citation"],
        "memory": "session_with_citations",
        "planning": "multi_step_with_reflection",
        "safety": ["source_verification", "no_executable_output"],
    },
    "enterprise_workflow": {
        "description": "Customer support, operations, and analysis in production",
        "tools": ["api_calls", "database_query", "email", "ticketing"],
        "memory": "persistent",
        "planning": "rule_based_with_escalation",
        "safety": ["human_in_loop", "audit_logging", "guardrails"],
    },
}

# Keyword signals for classification
SIGNALS = {
    "coding": [
        "code",
        "debug",
        "function",
        "script",
        "file",
        "git",
        "test",
        "compile",
        "refactor",
        "bug",
        "implement",
        "api endpoint",
        "database schema",
    ],
    "computer_use": [
        "browser",
        "click",
        "screen",
        "screenshot",
        "navigate",
        "form",
        "website",
        "login",
        "scroll",
        "button",
        "ui",
    ],
    "deep_research": [
        "research",
        "analyze",
        "report",
        "compare",
        "survey",
        "literature",
        "find sources",
        "summarize",
        "cite",
        "investigate",
        "study",
    ],
    "enterprise_workflow": [
        "customer",
        "support ticket",
        "escalate",
        "process",
        "workflow",
        "approve",
        "notify",
        "schedule",
        "invoice",
        "onboard",
    ],
}

# ---------- Sample tasks ----------

TASKS = [
    {
        "id": 1,
        "text": "Fix the failing unit test in auth.py and refactor the login function",
        "expected": "coding",
    },
    {
        "id": 2,
        "text": "Research the top 5 AI agent frameworks and write a comparison report",
        "expected": "deep_research",
    },
    {
        "id": 3,
        "text": "Fill out the vendor registration form on the supplier portal",
        "expected": "computer_use",
    },
    {
        "id": 4,
        "text": "Route this support ticket to the billing team and send a status update",
        "expected": "enterprise_workflow",
    },
    {
        "id": 5,
        "text": "Write a Python script to parse CSV files and generate a summary report",
        "expected": "coding",
    },
    {
        "id": 6,
        "text": "Search for recent papers on multi-agent systems and extract key findings",
        "expected": "deep_research",
    },
    {
        "id": 7,
        "text": "Book a flight on the travel portal and update the expense sheet",
        "expected": "computer_use",
    },
    {
        "id": 8,
        "text": "Onboard the new hire by creating accounts and sending welcome emails",
        "expected": "enterprise_workflow",
    },
    {
        "id": 9,
        "text": "Debug the memory leak in the production server and deploy the fix",
        "expected": "coding",
    },
    {
        "id": 10,
        "text": "Analyze customer feedback from the last quarter and identify top issues",
        "expected": "deep_research",
    },
]


# ---------- Classifier ----------


def classify_task(text: str) -> tuple[str, dict[str, int]]:
    """Classify a task by counting keyword signals. Returns archetype + scores."""
    lower = text.lower()
    scores: dict[str, int] = {}
    for archetype, keywords in SIGNALS.items():
        scores[archetype] = sum(1 for kw in keywords if kw in lower)

    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        best = "enterprise_workflow"
    return best, scores


def get_harness(archetype: str) -> dict:
    """Return the harness requirements for an archetype."""
    return ARCHETYPES[archetype]


# ---------- Display ----------


def print_results(results: list[dict]) -> None:
    print(f"\n{'=' * 80}")
    print("  AGENT ARCHETYPE CLASSIFIER — Results")
    print(f"{'=' * 80}\n")

    # Table header
    print(f"  {'#':>2}  {'Archetype':<20} {'Match':>5}  Task")
    print(f"  {'—' * 2}  {'—' * 20} {'—' * 5}  {'—' * 45}")

    for r in results:
        match = "OK" if r["classified"] == r["expected"] else "MISS"
        task_short = r["text"][:45] + "..." if len(r["text"]) > 45 else r["text"]
        print(f"  {r['id']:>2}  {r['classified']:<20} {match:>5}  {task_short}")

    # Correct rate
    correct = sum(1 for r in results if r["classified"] == r["expected"])
    print(
        f"\n  Accuracy: {correct}/{len(results)} ({100 * correct // len(results)}%)\n"
    )

    # Harness details
    print(f"{'=' * 80}")
    print("  HARNESS REQUIREMENTS BY ARCHETYPE")
    print(f"{'=' * 80}")

    for archetype, info in ARCHETYPES.items():
        count = sum(1 for r in results if r["classified"] == archetype)
        print(f"\n  [{archetype.upper()}] ({count} tasks)")
        print(f"    Description:  {info['description']}")
        print(f"    Tools:        {', '.join(info['tools'])}")
        print(f"    Memory:       {info['memory']}")
        print(f"    Planning:     {info['planning']}")
        print(f"    Safety:       {', '.join(info['safety'])}")

    # Statistics
    archetype_counts = Counter(r["classified"] for r in results)
    all_tools = []
    for r in results:
        all_tools.extend(ARCHETYPES[r["classified"]]["tools"])
    tool_counts = Counter(all_tools)

    print(f"\n{'=' * 80}")
    print("  STATISTICS")
    print(f"{'=' * 80}")
    print(f"\n  Tasks per archetype:")
    for arch, cnt in archetype_counts.most_common():
        bar = "#" * (cnt * 4)
        print(f"    {arch:<20} {cnt:>2}  {bar}")

    print(f"\n  Most common tools needed:")
    for tool, cnt in tool_counts.most_common(5):
        print(f"    {tool:<20} {cnt:>2}x")


# ---------- Main ----------


def main() -> None:
    print("=" * 80)
    print("  AGENT ARCHETYPE CLASSIFIER")
    print("  Classify tasks -> agent type -> harness requirements")
    print("=" * 80)

    results = []
    for task in TASKS:
        classified, scores = classify_task(task["text"])
        harness = get_harness(classified)
        results.append(
            {
                "id": task["id"],
                "text": task["text"],
                "expected": task["expected"],
                "classified": classified,
                "scores": scores,
                "harness": harness,
            }
        )

    print_results(results)

    # Bonus: hybrid detection
    print(f"\n{'=' * 80}")
    print("  HYBRID ARCHETYPE DETECTION")
    print(f"{'=' * 80}")
    for r in results:
        sorted_scores = sorted(r["scores"].items(), key=lambda x: -x[1])
        if len(sorted_scores) >= 2 and sorted_scores[1][1] > 0:
            gap = sorted_scores[0][1] - sorted_scores[1][1]
            if gap <= 1:
                print(
                    f"  Task {r['id']}: {sorted_scores[0][0]} + {sorted_scores[1][0]} "
                    f"(scores: {r['scores']})"
                )
    print()


if __name__ == "__main__":
    main()
