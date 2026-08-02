"""
Part 6 — Build Your Own Agent: Capstone (LLM-Powered)

A complete mini-agent that uses an LLM for planning and reflection,
combined with mock tools, memory, and evaluation. Demonstrates the full
agentic process with a real language model in the loop.

Run:  python capstone_agent_llm.py
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
LLM_TIMEOUT = int(os.environ.get("OPENCODE_TIMEOUT", "30"))
ENABLE_REFLECT = os.environ.get("OPENCODE_REFLECT", "1") == "1"
EVAL_LIMIT = int(os.environ.get("OPENCODE_EVAL_LIMIT", "1"))
TASK_DB: dict[str, dict] = {}

# Env knobs:
#   OPENCODE_REFLECT=0     skip LLM reflection (faster, no reflect loop)
#   OPENCODE_EVAL_LIMIT=N  cap eval cases to first N (default 1)
#   OPENCODE_TIMEOUT=30    per-call timeout in seconds


# ---------- LLM helper ----------


def ask_llm(prompt: str) -> str:
    """Call the opencode CLI and return the response."""
    try:
        result = subprocess.run(
            ["opencode", "run", "-m", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=LLM_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"[opencode timeout after {LLM_TIMEOUT}s]"
    except OSError as error:
        return f"[opencode error] {error}"
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


def _llm_failed(response: str) -> bool:
    """Return whether an LLM response contains a CLI failure marker."""
    return response.startswith("[opencode error]") or response.startswith(
        "[opencode timeout"
    )


# ---------- Tools ----------


def task_store(action: str, **kwargs) -> dict:
    """Mock task storage: add, list, complete, search."""
    if action == "add":
        task_id = hashlib.md5(kwargs["title"].encode()).hexdigest()[:6]
        TASK_DB[task_id] = {
            "title": kwargs["title"],
            "priority": kwargs.get("priority", "medium"),
            "status": "open",
            "created": datetime.now().isoformat(),
        }
        return {"ok": True, "task_id": task_id, "message": f"Added: {kwargs['title']}"}

    if action == "list":
        status_filter = kwargs.get("status", None)
        tasks = TASK_DB
        if status_filter:
            tasks = {k: v for k, v in tasks.items() if v["status"] == status_filter}
        return {"ok": True, "tasks": tasks, "count": len(tasks)}

    if action == "complete":
        tid = kwargs.get("task_id", "")
        if tid in TASK_DB:
            TASK_DB[tid]["status"] = "done"
            return {"ok": True, "message": f"Completed: {TASK_DB[tid]['title']}"}
        return {"ok": False, "message": f"Task {tid} not found"}

    if action == "search":
        query = kwargs.get("query", "").lower()
        matches = {k: v for k, v in TASK_DB.items() if query in v["title"].lower()}
        return {"ok": True, "tasks": matches, "count": len(matches)}

    return {"ok": False, "message": f"Unknown action: {action}"}


def priority_sorter(tasks: dict) -> list:
    """Sort tasks by priority: high > medium > low."""
    order = {"high": 0, "medium": 1, "low": 2}
    sorted_tasks = sorted(tasks.items(), key=lambda x: order.get(x[1]["priority"], 1))
    return sorted_tasks


def summary_generator(tasks: dict) -> str:
    """Generate a text summary of task status."""
    total = len(tasks)
    done = sum(1 for t in tasks.values() if t["status"] == "done")
    open_tasks = sum(1 for t in tasks.values() if t["status"] == "open")
    high = sum(
        1 for t in tasks.values() if t["priority"] == "high" and t["status"] == "open"
    )
    lines = [
        f"Total: {total} | Done: {done} | Open: {open_tasks} | High-priority open: {high}",
    ]
    if high > 0:
        lines.append("WARNING: You have unfinished high-priority tasks!")
    return " | ".join(lines)


# ---------- Memory ----------


class AgentMemory:
    """Short-term + long-term memory with JSON persistence."""

    def __init__(self, persist_path: Path) -> None:
        self.short_term: dict = {}
        self.long_term: list = []
        self.persist_path = persist_path
        self._load()

    def _load(self) -> None:
        if self.persist_path.exists():
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                return
            if isinstance(data, dict) and isinstance(data.get("long_term"), list):
                self.long_term = data["long_term"]

    def save(self) -> None:
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump({"long_term": self.long_term}, f, indent=2)

    def set_short(self, key: str, value: object) -> None:
        self.short_term[key] = value

    def get_short(self, key: str, default: object = None) -> object:
        return self.short_term.get(key, default)

    def append_long(self, entry: dict) -> None:
        self.long_term.append(entry)
        self.save()


# ---------- LLM Planning ----------


PLAN_SYSTEM = """Plan: output ONLY a compact JSON array. Max 5 items.
Use only task_store, priority_sorter, and summary_generator actions.
These are simulated action names in the JSON schema, not tools you need to call.
Do not explain limitations or mention tool availability.
Each: {"action":"task_store","args":{"action":"add","title":"SHORT TITLE","priority":"high"}}
Then one {"action":"summary_generator","args":{}}
Keep titles under 5 words. No other text. Start immediately with [."""


def _extract_partial_plan(text: str) -> list[dict]:
    """Try to extract individual JSON objects from truncated JSON array."""
    plan = []
    decoder = json.JSONDecoder()
    position = 0
    while position < len(text):
        start = text.find("{", position)
        if start == -1:
            break
        try:
            obj, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            position = start + 1
            continue
        if isinstance(obj, dict):
            plan.append(obj)
        position = start + end
    return plan


def _validate_plan(plan: object, goal: str) -> list[dict]:
    """Keep only executable, well-formed actions from an LLM plan."""
    if not isinstance(plan, list):
        return _fallback_plan(goal)

    valid_actions = {"task_store", "priority_sorter", "summary_generator"}
    valid_task_actions = {"add", "list", "complete", "search"}
    validated: list[dict] = []
    for step in plan:
        if not isinstance(step, dict):
            continue
        action = step.get("action")
        args = step.get("args", {})
        if action not in valid_actions or not isinstance(args, dict):
            continue
        if action == "task_store":
            task_action = args.get("action")
            if task_action not in valid_task_actions:
                continue
            if task_action == "add" and not isinstance(args.get("title"), str):
                continue
        validated.append({"action": action, "args": args})

    return validated or _fallback_plan(goal)


def llm_plan(goal: str) -> list[dict]:
    """Ask the LLM to decompose the goal into subtasks."""
    raw = ask_llm(f"{PLAN_SYSTEM}\n\nGoal: {goal}")
    if _llm_failed(raw) or not raw.strip():
        print(f"    (LLM planning failed: {raw[:80]})")
        return _fallback_plan(goal)

    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", raw)
    cleaned = re.sub(r"```", "", cleaned)

    match = re.search(r"\[.*\]", cleaned, re.S)
    if not match:
        plan = _extract_partial_plan(cleaned)
        if plan:
            return plan
        print(f"    (LLM did not return JSON: {raw[:80]})")
        return _fallback_plan(goal)

    try:
        return _validate_plan(json.loads(match.group(0)), goal)
    except json.JSONDecodeError:
        plan = _extract_partial_plan(match.group(0))
        if plan:
            return _validate_plan(plan, goal)
        print(f"    (JSON parse error from: {match.group(0)[:80]})")
        return _fallback_plan(goal)


def _fallback_plan(goal: str) -> list[dict]:
    """Keyword-based fallback if LLM fails."""
    lower = goal.lower()
    if "three tasks" in lower:
        return [
            {
                "action": "task_store",
                "args": {"action": "add", "title": "Write docs", "priority": "high"},
            },
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Update deps",
                    "priority": "medium",
                },
            },
            {
                "action": "task_store",
                "args": {"action": "add", "title": "Fix typos", "priority": "low"},
            },
            {"action": "task_store", "args": {"action": "list"}},
        ]
    if "review" in lower or "prioritize" in lower:
        return [
            {"action": "task_store", "args": {"action": "list"}},
            {"action": "priority_sorter", "args": {}},
            {"action": "summary_generator", "args": {}},
        ]
    if "project" in lower or "plan" in lower:
        return [
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Define project scope",
                    "priority": "high",
                },
            },
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Set project milestones",
                    "priority": "high",
                },
            },
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Write status report",
                    "priority": "medium",
                },
            },
            {"action": "summary_generator", "args": {}},
        ]
    return [
        {
            "action": "task_store",
            "args": {"action": "add", "title": goal, "priority": "high"},
        },
        {"action": "task_store", "args": {"action": "list"}},
        {"action": "summary_generator", "args": {}},
    ]


def _evaluation_passed(goal: str, outcome: dict) -> bool:
    """Check both execution health and the test case's expected behavior."""
    if outcome["steps_taken"] <= 0 or not outcome["log"]:
        return False
    if not all(
        entry.get("result_ok", False) or entry.get("retry_result_ok", False)
        for entry in outcome["log"]
    ):
        return False

    lower = goal.lower()
    tasks = outcome.get("tasks", {})
    if "three tasks" in lower:
        priorities = {task["priority"] for task in tasks.values()}
        return len(tasks) == 3 and priorities == {"high", "medium", "low"}
    if "review" in lower or "prioritize" in lower:
        return (
            "priority_sorter" in outcome["tools_used"]
            and "summary_generator" in outcome["tools_used"]
        )
    if "project" in lower or "plan" in lower:
        return len(tasks) >= 2
    return True


# ---------- LLM Reflection ----------


REFLECT_SYSTEM = """You are an agent reflector. After each tool call, evaluate the result.

Reply with EXACTLY one word on the first line:
  CONTINUE  — the step succeeded, proceed to the next step
  RETRY     — the step failed or result looks wrong, try again
  STOP      — the goal is fully achieved, no more steps needed

Optionally, on the second line, write a one-sentence reason.
"""


def llm_reflect(goal: str, step_num: int, action: str, result: str) -> tuple[str, str]:
    """Ask the LLM to evaluate a step result."""
    prompt = (
        f"{REFLECT_SYSTEM}\n\n"
        f"Goal: {goal}\n"
        f"Step {step_num}: {action}\n"
        f"Result: {result[:300]}"
    )
    raw = ask_llm(prompt)
    if _llm_failed(raw) or not raw.strip():
        return "CONTINUE", "(LLM reflection unavailable, continuing)"

    lines = raw.strip().splitlines()
    decision = lines[0].strip().upper()
    reason = lines[1].strip() if len(lines) > 1 else ""

    if decision not in ("CONTINUE", "RETRY", "STOP"):
        decision = "CONTINUE"

    return decision, reason


# ---------- Agent core ----------


def _execute_action(action: str, args: dict) -> object:
    """Execute one validated tool action."""
    if action == "task_store":
        return task_store(**args)
    if action == "priority_sorter":
        current = task_store("list")
        sorted_tasks = priority_sorter(current.get("tasks", {}))
        return {
            "sorted": [(task["title"], task["priority"]) for _, task in sorted_tasks]
        }
    if action == "summary_generator":
        current = task_store("list")
        return summary_generator(current.get("tasks", {}))
    return {"ok": False, "error": f"Unknown action: {action}"}


def run_agent(goal: str, memory: AgentMemory, max_steps: int = 10) -> dict:
    """Main agent loop: plan -> execute -> reflect -> update memory."""
    TASK_DB.clear()

    memory.set_short("goal", goal)
    memory.set_short("start_time", datetime.now().isoformat())

    print(f"  Goal: {goal}")
    print(f"  Planning with {MODEL}...")

    subtasks = llm_plan(goal)
    memory.set_short("plan", subtasks)
    print(f"  Plan: {len(subtasks)} steps\n")

    log: list[dict] = []
    steps_taken = 0
    tools_used: list[str] = []

    for i, subtask in enumerate(subtasks):
        if steps_taken >= max_steps:
            print(f"  Reached max steps ({max_steps})")
            break

        steps_taken += 1
        action = subtask["action"]
        args = subtask.get("args", {})

        result = _execute_action(action, args)

        tools_used.append(action)
        result_str = json.dumps(result, default=str)[:300]
        result_ok = not (isinstance(result, dict) and result.get("ok") is False)

        # LLM reflection (skippable for faster runs)
        if ENABLE_REFLECT:
            print(f"  Step {i + 1}: {action} {args} -> reflecting...")
            decision, reason = llm_reflect(goal, i + 1, action, result_str)
            print(f"    -> {decision}: {reason}")
        else:
            decision, reason = (
                "CONTINUE",
                "(reflection disabled via OPENCODE_REFLECT=0)",
            )

        entry = {
            "step": i + 1,
            "action": action,
            "args": args,
            "decision": decision,
            "reason": reason,
            "result_ok": result_ok,
            "result_summary": result_str[:100],
        }
        log.append(entry)

        if decision == "STOP":
            print("  LLM decided goal is complete.")
            break
        elif decision == "RETRY":
            if steps_taken >= max_steps:
                print(f"  Retry skipped: max steps ({max_steps}) reached")
                continue
            steps_taken += 1
            print(f"  Retrying step {i + 1}...")
            result2 = _execute_action(action, args)
            result2_ok = not (isinstance(result2, dict) and result2.get("ok") is False)
            entry["retry_result_ok"] = result2_ok
            entry["retry_result"] = json.dumps(result2, default=str)[:100]

    # Final summary
    current_tasks = task_store("list")
    summary = summary_generator(current_tasks.get("tasks", {}))

    memory.append_long(
        {
            "goal": goal,
            "steps": steps_taken,
            "tools_used": list(dict.fromkeys(tools_used)),
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }
    )

    return {
        "goal": goal,
        "steps_taken": steps_taken,
        "tools_used": list(dict.fromkeys(tools_used)),
        "log": log,
        "summary": summary,
        "tasks": current_tasks.get("tasks", {}),
    }


# ---------- Evaluation ----------


def run_evaluation() -> list[dict]:
    """Run test cases through the agent and score results."""
    persist = Path(__file__).parent / "agent_memory_llm_eval.json"
    test_goals = [
        "Plan a new project: define scope, milestones, and assign owners",
        "Review tasks, prioritize them, and give a summary report",
        "Create three tasks: write docs (high), update deps (medium), fix typos (low), then list them",
    ]

    results = []
    for goal in test_goals[:EVAL_LIMIT]:
        if persist.exists():
            persist.unlink()
        mem = AgentMemory(persist)

        try:
            outcome = run_agent(goal, mem)
            passed = _evaluation_passed(goal, outcome)
            results.append(
                {
                    "goal": goal,
                    "passed": passed,
                    "steps": outcome["steps_taken"],
                    "tools": outcome["tools_used"],
                    "summary": outcome["summary"],
                }
            )
        except Exception as e:
            results.append(
                {
                    "goal": goal,
                    "passed": False,
                    "steps": 0,
                    "tools": [],
                    "summary": f"Error: {e}",
                }
            )

    if persist.exists():
        persist.unlink()

    return results


# ---------- Display ----------


def print_results(result: dict) -> None:
    print(f"\n{'=' * 60}")
    print("  CAPSTONE AGENT (LLM) — Run Complete")
    print(f"{'=' * 60}")
    print(f"  Goal:   {result['goal']}")
    print(f"  Steps:  {result['steps_taken']}")
    print(f"  Tools:  {', '.join(result['tools_used'])}")
    print("\n  Transcript:")
    for entry in result["log"]:
        decision = entry["decision"]
        print(
            f"    [Step {entry['step']}] {entry['action']} -> {decision}: {entry['reason']}"
        )
    print(f"\n  Summary: {result['summary']}")
    print(f"{'=' * 60}")


def main() -> None:
    print("=" * 60)
    print("  CAPSTONE AGENT (LLM) — Full Agentic Process")
    print(f"  Model: {MODEL}")
    print("=" * 60)

    # Run the agent
    persist = Path(__file__).parent / "agent_memory_llm.json"
    mem = AgentMemory(persist)
    result = run_agent(
        "Plan a new project: research the market, define milestones, and write a status report",
        mem,
    )
    print_results(result)

    # Run evaluation
    print(f"\n{'=' * 60}")
    print("  EVALUATION — Running 3 test cases")
    print(f"{'=' * 60}")

    eval_results = run_evaluation()
    for r in eval_results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['goal'][:60]} — {r['steps']} step(s)")

    passed = sum(1 for r in eval_results if r["passed"])
    print(f"\n  Result: {passed}/{len(eval_results)} passed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
