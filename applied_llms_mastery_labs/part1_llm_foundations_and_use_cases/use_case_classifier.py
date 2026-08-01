"""
Part 1 — LLM Foundations: Use-Case Classifier

Classifies business problems into 7 LLM use cases using:
  1. Rule-based (keyword matching + confidence score)
  2. LLM-based (opencode CLI)

Run:  python use_case_classifier.py
"""

import json
import os
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# Pick a model. Free options (no payment needed):
#   opencode/mimo-v2.5-free
#   opencode/deepseek-v4-flash-free
#   opencode/laguna-s-2.1-free
#   opencode/ling-3.0-flash-free
#   opencode/nemotron-3-ultra-free
#   opencode/north-mini-code-free
# Or set the OPENCODE_MODEL env var to override.
MODEL = os.environ.get("OPENCODE_MODEL", "opencode/mimo-v2.5-free")

# ---------- Use-case definitions ----------

USE_CASES = {
    "content_generation": {
        "desc": "Writing, drafting, creative text",
        "keywords": [
            "generate",
            "write",
            "draft",
            "create",
            "compose",
            "produce",
            "content",
            "copy",
            "blog",
            "post",
        ],
    },
    "translation": {
        "desc": "Language-to-language conversion",
        "keywords": [
            "translate",
            "localize",
            "language",
            "multilingual",
            "bilingual",
            "interpret",
        ],
    },
    "summarization": {
        "desc": "Condensing long text",
        "keywords": [
            "summarize",
            "condense",
            "brief",
            "digest",
            "tldr",
            "recap",
            "overview",
        ],
    },
    "qa_chatbot": {
        "desc": "Question answering, conversational",
        "keywords": [
            "answer",
            "reply",
            "support",
            "chat",
            "conversation",
            "respond",
            "faq",
            "assist",
        ],
    },
    "content_moderation": {
        "desc": "Detecting harmful/inappropriate content",
        "keywords": [
            "moderate",
            "filter",
            "toxic",
            "harmful",
            "inappropriate",
            "abuse",
            "flag",
            "safe",
        ],
    },
    "information_retrieval": {
        "desc": "Extracting facts from documents",
        "keywords": [
            "extract",
            "search",
            "retrieve",
            "find",
            "lookup",
            "review",
            "scan",
            "index",
        ],
    },
    "educational_tools": {
        "desc": "Tutoring, explaining, teaching",
        "keywords": [
            "teach",
            "explain",
            "tutor",
            "learn",
            "educate",
            "quiz",
            "coach",
            "train",
        ],
    },
}

VALID_LABELS = set(USE_CASES.keys())

# ---------- Test cases ----------

TEST_CASES = [
    ("We need to automatically reply to customer support tickets", "qa_chatbot"),
    (
        "Our legal team needs to review 500 contracts for key clauses",
        "information_retrieval",
    ),
    (
        "We want to generate product descriptions from specifications",
        "content_generation",
    ),
    ("Translate our help center articles into 12 languages", "translation"),
    ("Summarize 200-page earnings calls into 1-page briefs", "summarization"),
    ("Flag toxic comments on our forum before they go live", "content_moderation"),
    ("Build a tutor that explains calculus step by step", "educational_tools"),
    ("Find all mentions of our brand across news articles", "information_retrieval"),
    ("Draft social media posts for our product launch", "content_generation"),
    ("Auto-answer common questions from our FAQ page", "qa_chatbot"),
]

# ---------- LLM via opencode CLI ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode CLI and return the response text."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Rule-based classifier ----------


def classify_rules(text: str) -> tuple[str, float]:
    """Classify by counting keyword matches. Returns (label, confidence)."""
    tokens = set(text.lower().split())
    scores = {}
    for label, info in USE_CASES.items():
        matches = tokens & set(info["keywords"])
        if matches:
            scores[label] = (len(matches), len(info["keywords"]))

    if not scores:
        return ("uncertain", 0.0)

    best_label, (matched, total) = max(scores.items(), key=lambda x: x[1][0])
    confidence = matched / total
    return (best_label, round(confidence, 2))


# ---------- LLM classifier ----------


def classify_llm(text: str) -> str:
    """Ask the LLM to classify a business problem into one of the 7 categories."""
    categories = ", ".join(sorted(VALID_LABELS))
    prompt = (
        f"Classify the following business problem into exactly ONE of these "
        f"categories:\n{categories}\n\n"
        f"Problem: {text}\n\n"
        f"Reply with ONLY the category name, nothing else."
    )
    raw = ask_llm(prompt).strip().lower()

    # Direct match
    if raw in VALID_LABELS:
        return raw

    # Try to find a valid label inside the response
    for label in VALID_LABELS:
        if label in raw:
            return label

    return "unknown"


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_results(rows: list[dict]) -> None:
    """Print a side-by-side comparison table."""
    print(f"\n{'Problem':<55} {'Rules':<25} {'LLM':<25} {'Match'}")
    print("-" * 120)
    for r in rows:
        problem_short = (
            r["problem"][:52] + "..." if len(r["problem"]) > 55 else r["problem"]
        )
        match_icon = "  OK" if r["match"] else "  --"
        print(
            f"{problem_short:<55} {r['rules_label']:<25} {r['llm_label']:<25} {match_icon}"
        )


def print_summary(rows: list[dict]) -> None:
    """Print agreement/disagreement summary."""
    agreements = [r for r in rows if r["match"]]
    disagreements = [r for r in rows if not r["match"]]

    banner("SUMMARY")
    print(f"  Agreements:    {len(agreements)}/{len(rows)}")
    print(f"  Disagreements: {len(disagreements)}/{len(rows)}")

    if disagreements:
        print("\n  Disagreements detail:")
        for r in disagreements:
            print(f'    - "{r["problem"][:60]}"')
            print(f"        Rules: {r['rules_label']}  |  LLM: {r['llm_label']}")


# ---------- Bonus: custom mode ----------


def custom_mode() -> None:
    """Let the user type a business problem and see both classifiers."""
    banner("CUSTOM MODE — type a business problem (or 'quit' to exit)")
    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text or text.lower() in ("quit", "exit", "q"):
            break

        rules_label, confidence = classify_rules(text)
        llm_label = classify_llm(text)
        match = rules_label == llm_label

        print(f"\n  Rule-based: {rules_label} (confidence: {confidence})")
        print(f"  LLM:        {llm_label}")
        print(f"  Match:      {'Yes' if match else 'No'}")


# ---------- Main ----------


def main() -> None:
    print(f"Model: {MODEL}")

    banner("RUNNING 10 TEST CASES")
    rows = []
    for problem, expected in TEST_CASES:
        rules_label, confidence = classify_rules(problem)
        llm_label = classify_llm(problem)
        match = rules_label == llm_label
        rows.append(
            {
                "problem": problem,
                "expected": expected,
                "rules_label": rules_label,
                "rules_confidence": confidence,
                "llm_label": llm_label,
                "match": match,
            }
        )
        status = "OK" if match else "DIFF"
        print(f"  [{status}] {problem[:50]}...  rules={rules_label}  llm={llm_label}")

    show_results(rows)
    print_summary(rows)

    # Bonus: custom mode
    print("\n")
    try:
        choice = input("Try custom mode? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "n"
    if choice == "y":
        custom_mode()

    banner("DONE — Part 1 complete. Next: Part 2 (Domain & Task Adaptation)")


if __name__ == "__main__":
    main()
