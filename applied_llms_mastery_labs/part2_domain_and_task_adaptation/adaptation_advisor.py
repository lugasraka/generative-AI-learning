"""
Part 2 — Domain & Task Adaptation: Adaptation Advisor

Asks 6 questions about your constraints, scores 3 adaptation methods
(pre-training, fine-tuning, RAG), and compares with an LLM recommendation.

Run:  python adaptation_advisor.py
"""

import os
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode/mimo-v2.5-free")

# ---------- Method definitions ----------

METHODS = {
    "pre_training": {
        "desc": "Train from scratch on domain data",
        "cost": "very high",
        "time": "weeks-months",
        "data_needed": "massive",
        "performance": "highest",
        "privacy": "full control",
    },
    "fine_tuning": {
        "desc": "Fine-tune a pre-trained model on your data",
        "cost": "moderate",
        "time": "hours-days",
        "data_needed": "moderate",
        "performance": "high",
        "privacy": "good",
    },
    "rag": {
        "desc": "Retrieve docs at query time, no training needed",
        "cost": "low",
        "time": "hours-days",
        "data_needed": "documents only",
        "performance": "good",
        "privacy": "excellent (no training)",
    },
}

# ---------- Questions + scoring matrix ----------
# Each question: (prompt_text, options_list, score_per_method_per_option)
# Scores are 0-100 per method. Order of options matters for relaxation analysis.

QUESTIONS = [
    {
        "prompt": "What's your budget?",
        "key": "budget",
        "options": ["low", "moderate", "high", "very high"],
        "scores": {
            "pre_training": [0, 25, 75, 100],
            "fine_tuning": [25, 50, 75, 75],
            "rag": [75, 75, 50, 25],
        },
    },
    {
        "prompt": "How much domain-specific data do you have?",
        "key": "data",
        "options": ["none", "small", "moderate", "massive"],
        "scores": {
            "pre_training": [0, 10, 50, 100],
            "fine_tuning": [0, 40, 80, 60],
            "rag": [80, 70, 50, 20],
        },
    },
    {
        "prompt": "How quickly do you need this?",
        "key": "timeline",
        "options": ["today", "this week", "this month", "no rush"],
        "scores": {
            "pre_training": [0, 5, 30, 100],
            "fine_tuning": [20, 50, 80, 80],
            "rag": [100, 80, 60, 40],
        },
    },
    {
        "prompt": "How sensitive is the data?",
        "key": "sensitivity",
        "options": ["public", "internal", "confidential", "regulated"],
        "scores": {
            "pre_training": [50, 40, 30, 20],
            "fine_tuning": [40, 50, 60, 50],
            "rag": [60, 70, 80, 90],
        },
    },
    {
        "prompt": "What performance level do you need?",
        "key": "performance",
        "options": ["good enough", "high", "highest possible"],
        "scores": {
            "pre_training": [10, 40, 100],
            "fine_tuning": [50, 80, 90],
            "rag": [80, 50, 20],
        },
    },
    {
        "prompt": "Does your team have ML expertise?",
        "key": "expertise",
        "options": ["no", "basic", "experienced", "expert"],
        "scores": {
            "pre_training": [0, 10, 40, 100],
            "fine_tuning": [10, 40, 80, 90],
            "rag": [80, 70, 50, 30],
        },
    },
]

# ---------- LLM via opencode CLI ----------


def ask_llm(prompt: str) -> str:
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Scoring ----------


def score_methods(answers: dict[str, int]) -> dict[str, dict]:
    """Score all 3 methods based on user answers. Returns scores 0-100 + reasons."""
    raw = {"pre_training": 0, "fine_tuning": 0, "rag": 0}
    reasons = {"pre_training": [], "fine_tuning": [], "rag": []}

    for q in QUESTIONS:
        idx = answers[q["key"]]
        for method in raw:
            raw[method] += q["scores"][method][idx]
            # Track which answers helped or hurt
            score = q["scores"][method][idx]
            if score >= 70:
                reasons[method].append(f"{q['key']}={q['options'][idx]} (+{score})")
            elif score <= 20:
                reasons[method].append(f"{q['key']}={q['options'][idx]} ({score})")

    # Normalize to 0-100 (max possible = 6 questions * 100 = 600)
    result = {}
    for method in raw:
        normalized = round(raw[method] / 6, 1)
        # Pick the top reason (highest contributing factor)
        top_reasons = reasons[method][:2] if reasons[method] else ["neutral fit"]
        result[method] = {"score": normalized, "reasons": top_reasons}

    return result


def bar(score: float, width: int = 10) -> str:
    """Visual bar: [██████░░░░]"""
    filled = round(score / 100 * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


# ---------- LLM advisor ----------


def recommend_llm(answers: dict[str, int]) -> str:
    """Ask the LLM for its recommendation based on user constraints."""
    summary_lines = []
    for q in QUESTIONS:
        idx = answers[q["key"]]
        summary_lines.append(f"- {q['key']}: {q['options'][idx]}")
    summary = "\n".join(summary_lines)

    prompt = (
        f"Given these constraints for building an LLM application:\n"
        f"{summary}\n\n"
        f"Which approach would you recommend: pre-training, fine-tuning, or RAG?\n"
        f"Explain your reasoning in 2 sentences."
    )
    return ask_llm(prompt)


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def ask_question(q: dict) -> int:
    """Ask a question and return the selected index."""
    print(f"\n  {q['prompt']}")
    for i, opt in enumerate(q["options"], 1):
        print(f"    {i}. {opt}")
    while True:
        try:
            choice = input(f"  Enter 1-{len(q['options'])}: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(q["options"]):
                return idx
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        print(f"  Please enter a number between 1 and {len(q['options'])}")


def print_method_table(scores: dict[str, dict]) -> None:
    """Print the recommendation table with bars and reasons."""
    print(f"\n  {'Method':<15} {'Score':>6}  {'Bar':<14} Why")
    print("  " + "-" * 68)
    for method in ["pre_training", "fine_tuning", "rag"]:
        s = scores[method]
        desc = METHODS[method]["desc"]
        reasons = "; ".join(s["reasons"])
        print(f"  {method:<15} {s['score']:>5.1f}  {bar(s['score']):<14} {reasons}")
        print(f"  {'':15}        {desc}")


def print_comparison(rule_winner: str, llm_text: str) -> None:
    """Print rule-based vs LLM recommendation side by side."""
    banner("RULE-BASED vs LLM RECOMMENDATION")
    print(f"\n  Rule-based winner:  {rule_winner.upper()}")
    print(f"  LLM recommendation: {llm_text}")


# ---------- Bonus: relaxation analysis ----------


def relaxation_analysis(
    answers: dict[str, int], current_scores: dict[str, dict]
) -> None:
    """Show how the recommendation changes if the user relaxes one constraint."""
    banner("WHAT IF YOU RELAX ONE CONSTRAINT?")
    relaxable = ["budget", "data", "timeline"]
    changed_any = False

    for key in relaxable:
        q = next(q for q in QUESTIONS if q["key"] == key)
        current_idx = answers[key]
        if current_idx >= len(q["options"]) - 1:
            continue  # already at max

        # Simulate upgrading one step
        new_answers = dict(answers)
        new_answers[key] = current_idx + 1
        new_scores = score_methods(new_answers)

        old_winner = max(current_scores, key=lambda m: current_scores[m]["score"])
        new_winner = max(new_scores, key=lambda m: new_scores[m]["score"])

        old_opt = q["options"][current_idx]
        new_opt = q["options"][current_idx + 1]

        if old_winner != new_winner:
            print(f'\n  If {key} goes from "{old_opt}" to "{new_opt}":')
            print(f"    Winner changes: {old_winner} -> {new_winner}")
            for m in ["pre_training", "fine_tuning", "rag"]:
                old_s = current_scores[m]["score"]
                new_s = new_scores[m]["score"]
                delta = new_s - old_s
                sign = "+" if delta >= 0 else ""
                print(f"    {m:<15} {old_s:>5.1f} -> {new_s:>5.1f} ({sign}{delta:.1f})")
            changed_any = True

    if not changed_any:
        print("\n  No single constraint change would flip the recommendation.")
        print("  Your scenario is stable — the recommended method fits well.")


# ---------- Main ----------


def main() -> None:
    print(f"Model: {MODEL}")
    banner("DOMAIN ADAPTATION ADVISOR")
    print("\n  I'll ask you 6 questions about your project constraints.")
    print("  Then I'll recommend the best adaptation method:\n")
    for name, info in METHODS.items():
        print(f"    {name:<15} {info['desc']}")
        print(
            f"    {'':15} cost={info['cost']}, time={info['time']}, data={info['data_needed']}"
        )
    print()

    # Collect answers
    answers = {}
    for q in QUESTIONS:
        answers[q["key"]] = ask_question(q)

    # Score and display
    scores = score_methods(answers)
    banner("SCORING RESULTS")
    print_method_table(scores)

    rule_winner = max(scores, key=lambda m: scores[m]["score"])

    # LLM recommendation
    banner("LLM RECOMMENDATION")
    llm_text = recommend_llm(answers)
    print(f"\n  {llm_text}")

    print_comparison(rule_winner, llm_text)

    # Bonus: relaxation
    relaxation_analysis(answers, scores)

    banner("DONE — Part 2 complete. Next: Part 3 (Prompting & Prompt Engineering)")


if __name__ == "__main__":
    main()
