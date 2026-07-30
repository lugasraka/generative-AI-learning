"""
Part 6 — Planning: a planner that turns a complex task into a list of steps.

Two planners side-by-side:
  - rule_based_plan(task): keyword/pattern matching, deterministic
  - llm_plan(task):       asks opencode CLI to plan, parses JSON

The bonus: each plan also flags which steps need a human-in-the-loop check.

Run:  python planner.py
"""

import json
import os
import re
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/minimax-m3")

# ---------- LLM helper ----------


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


# ---------- 1. Rule-based planner ----------


# Keywords -> action templates
RULES = [
    (re.compile(r"\b(draft|write|compose)\b.*\bemail", re.I), "draft_email"),
    (re.compile(r"\bsend\b.*\bemail", re.I), "send_email"),
    (
        re.compile(r"\b(payment\s*link|checkout|pay\s*now)", re.I),
        "generate_payment_link",
    ),
    (re.compile(r"\b(overdue|unpaid|past\s*due)\b", re.I), "query_db"),
    (re.compile(r"\b(q[1-4]|quarter)\b", re.I), "query_db"),
    (re.compile(r"\bhealthcare|finance|retail|sector\b", re.I), "query_db"),
    (re.compile(r"\bclient|customer|account\b", re.I), "query_db"),
    (re.compile(r"\b(research|find|look\s*up|search)\b", re.I), "search_docs"),
    (re.compile(r"\bsummar(y|ize)\b", re.I), "summarize"),
    (re.compile(r"\b\d+\s*[\*x×]\s*\d+", re.I), "calculate"),
]


def rule_based_plan(task: str) -> list[dict]:
    """Naive rule-based planner: scan task text for keywords, emit a step list."""
    plan: list[dict] = []
    seen_actions: set[str] = set()

    for pattern, action in RULES:
        if pattern.search(task) and action not in seen_actions:
            plan.append(
                {
                    "step": len(plan) + 1,
                    "action": action,
                    "details": _details_for(action, task),
                }
            )
            seen_actions.add(action)

    if not plan:
        plan.append(
            {
                "step": 1,
                "action": "answer",
                "details": "No multi-step plan needed; answer directly.",
            }
        )

    _flag_human_checkpoints(plan, task)
    return plan


def _details_for(action: str, task: str) -> str:
    defaults = {
        "query_db": "filter on the relevant entities from the task",
        "search_docs": "search the knowledge base for context",
        "summarize": "summarize retrieved information",
        "draft_email": "draft a personalized message using gathered context",
        "send_email": "send via the send_email tool",
        "generate_payment_link": "create a fresh payment link for the client",
        "calculate": "compute the requested arithmetic",
        "answer": "produce a direct answer",
    }
    return defaults.get(action, "see task text")


# ---------- 2. Human-in-the-loop flagging ----------


HUMAN_REQUIRED_ACTIONS = {"send_email", "generate_payment_link", "draft_email"}


def _flag_human_checkpoints(plan: list[dict], task: str) -> None:
    """Mutate each step to add 'human_checkpoint' based on action + risk words."""
    high_risk = bool(re.search(r"\b(send|delete|charge|payment|wire)\b", task, re.I))
    for step in plan:
        needs_human = step["action"] in HUMAN_REQUIRED_ACTIONS or (
            high_risk and step["action"] in {"send_email", "generate_payment_link"}
        )
        step["human_checkpoint"] = needs_human


# ---------- 3. LLM-based planner ----------


LLM_SYSTEM = """You are a planner. Break the user's task into a small number of steps.

RULES (strict):
- Output ONLY a single JSON array. No prose, no markdown outside the array.
- Each step is an object: {"step": <int>, "action": "<verb_noun>", "details": "<one short sentence>"}
- Add a "human_checkpoint": true/false field on every step.
- Mark human_checkpoint=true for any step that sends email, makes a payment,
  deletes data, or other irreversible/external action. Mark false for read-only
  steps like query, search, summarize, calculate.
- Prefer 3-7 steps. If the task is truly one-step (e.g. "what's 13 times 47"),
  return a single-step plan with action "answer" and human_checkpoint=false.
- Do NOT include any step that just says "the LLM" — name the action verb.
- Do NOT execute anything; you are only planning.

Available action vocabulary (use these or close synonyms):
  query_db, search_docs, summarize, draft_email, send_email,
  generate_payment_link, calculate, answer
"""


def llm_plan(task: str) -> list[dict]:
    """Ask the LLM to produce a plan; parse JSON array."""
    raw = ask_llm(f"{LLM_SYSTEM}\nTask: {task}")
    # Try to extract the first JSON array from the response
    match = re.search(r"\[.*\]", raw, re.S)
    if not match:
        return [
            {
                "step": 1,
                "action": "answer",
                "details": f"(LLM did not return JSON; raw: {raw[:120]})",
                "human_checkpoint": False,
            }
        ]
    try:
        plan = json.loads(match.group(0))
        # Normalize: ensure human_checkpoint field exists
        for s in plan:
            s.setdefault("human_checkpoint", False)
            s.setdefault("step", plan.index(s) + 1)
        return plan
    except json.JSONDecodeError as e:
        return [
            {
                "step": 1,
                "action": "answer",
                "details": f"(could not parse JSON: {e}; raw: {raw[:120]})",
                "human_checkpoint": False,
            }
        ]


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def print_plan(label: str, plan: list[dict]) -> None:
    print(f"\n  {label}:")
    for s in plan:
        flag = "  [HUMAN CHECKPOINT]" if s.get("human_checkpoint") else ""
        print(f"    {s['step']}. {s['action']}  —  {s['details']}{flag}")


# ---------- Demo ----------


COMPLEX_TASK = (
    "Find all our Q1 healthcare clients who are overdue on payments, "
    "and draft personalized emails with new payment links."
)
SIMPLE_TASK = "What's 13 times 47?"
MID_TASK = (
    "Research the latest news about the 2026 World Cup host cities, "
    "summarize the top 3 announcements, and email the summary to my team."
)


if __name__ == "__main__":
    print(f"Model: {MODEL}\n")

    for label, task in [
        ("COMPLEX", COMPLEX_TASK),
        ("SIMPLE", SIMPLE_TASK),
        ("MID", MID_TASK),
    ]:
        banner(f"{label} TASK: {task}")
        print_plan("RULE-BASED PLAN", rule_based_plan(task))
        print_plan("LLM PLAN", llm_plan(task))
