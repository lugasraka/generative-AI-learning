"""
Part 6 — Build Your Own Agent: Capstone

A complete mini-agent combining all harness components: core loop,
memory, tools, planning, reflection, and evaluation. Uses a task
tracking domain to demonstrate end-to-end agent behavior.

Run:  python capstone_agent.py
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime


# ---------- Tools ----------


def task_store(action: str, **kwargs) -> dict:
    """Mock task storage: add, list, complete, search."""
    if not hasattr(task_store, "_db"):
        task_store._db = {}

    if action == "add":
        task_id = hashlib.md5(kwargs["title"].encode()).hexdigest()[:6]
        task_store._db[task_id] = {
            "title": kwargs["title"],
            "priority": kwargs.get("priority", "medium"),
            "status": "open",
            "created": datetime.now().isoformat(),
        }
        return {"ok": True, "task_id": task_id, "message": f"Added: {kwargs['title']}"}

    if action == "list":
        status_filter = kwargs.get("status", None)
        tasks = task_store._db
        if status_filter:
            tasks = {k: v for k, v in tasks.items() if v["status"] == status_filter}
        return {"ok": True, "tasks": tasks, "count": len(tasks)}

    if action == "complete":
        tid = kwargs.get("task_id", "")
        if tid in task_store._db:
            task_store._db[tid]["status"] = "done"
            return {"ok": True, "message": f"Completed: {task_store._db[tid]['title']}"}
        return {"ok": False, "message": f"Task {tid} not found"}

    if action == "search":
        query = kwargs.get("query", "").lower()
        matches = {
            k: v for k, v in task_store._db.items() if query in v["title"].lower()
        }
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


# ---------- Agent core ----------


class AgentMemory:
    """Short-term + long-term memory with JSON persistence."""

    def __init__(self, persist_path: Path) -> None:
        self.short_term: dict = {}
        self.long_term: list = []
        self.persist_path = persist_path
        self._load()

    def _load(self) -> None:
        if self.persist_path.exists():
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.long_term = data.get("long_term", [])

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


def decompose_task(goal: str) -> list[dict]:
    """Break a goal into subtasks based on keywords."""
    subtasks = []
    lower = goal.lower()

    if "project" in lower or "plan" in lower:
        subtasks.append(
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Define project scope",
                    "priority": "high",
                },
            }
        )
        subtasks.append(
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Break into milestones",
                    "priority": "high",
                },
            }
        )
        subtasks.append(
            {
                "action": "task_store",
                "args": {
                    "action": "add",
                    "title": "Assign owners",
                    "priority": "medium",
                },
            }
        )

    if "clean" in lower or "organize" in lower or "review" in lower:
        subtasks.append({"action": "task_store", "args": {"action": "list"}})
        subtasks.append({"action": "priority_sorter", "args": {}})
        subtasks.append(
            {"action": "task_store", "args": {"action": "list", "status": "open"}}
        )

    if "complete" in lower or "finish" in lower or "done" in lower:
        subtasks.append(
            {"action": "task_store", "args": {"action": "list", "status": "open"}}
        )
        subtasks.append({"action": "task_store", "args": {"action": "complete"}})

    if "summary" in lower or "report" in lower:
        subtasks.append({"action": "task_store", "args": {"action": "list"}})
        subtasks.append({"action": "summary_generator", "args": {}})

    if not subtasks:
        subtasks.append(
            {
                "action": "task_store",
                "args": {"action": "add", "title": goal, "priority": "medium"},
            }
        )
        subtasks.append({"action": "summary_generator", "args": {}})

    return subtasks


def reflect(step_result: dict) -> tuple[bool, str]:
    """Evaluate whether the step result is acceptable."""
    if isinstance(step_result, dict):
        if step_result.get("ok"):
            return True, "Step succeeded"
        return False, step_result.get("message", "Step failed")
    if isinstance(step_result, str) and len(step_result) > 0:
        return True, "Generated output"
    return False, "Empty result"


def run_agent(goal: str, memory: AgentMemory) -> dict:
    """Main agent loop: decompose -> execute -> reflect -> update memory."""
    memory.set_short("goal", goal)
    memory.set_short("start_time", datetime.now().isoformat())

    subtasks = decompose_task(goal)
    memory.set_short("plan", [s["action"] for s in subtasks])

    log: list[dict] = []
    steps_taken = 0
    tools_used: list[str] = []

    for i, subtask in enumerate(subtasks):
        steps_taken += 1
        action = subtask["action"]
        args = subtask.get("args", {})

        # Execute
        if action == "task_store":
            result = task_store(**args)
        elif action == "priority_sorter":
            current = task_store("list")
            sorted_t = priority_sorter(current.get("tasks", {}))
            result = {"sorted": [(t["title"], t["priority"]) for _, t in sorted_t]}
        elif action == "summary_generator":
            current = task_store("list")
            result = summary_generator(current.get("tasks", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        tools_used.append(action)

        # Reflect
        ok, msg = reflect(result)

        entry = {
            "step": i + 1,
            "action": action,
            "args": args,
            "success": ok,
            "message": msg,
            "result_summary": str(result)[:100],
        }
        log.append(entry)

        if not ok:
            print(f"  Step {i + 1}: FAILED — {msg}")

    # Generate summary
    current_tasks = task_store("list")
    summary = summary_generator(current_tasks.get("tasks", {}))

    # Save to long-term memory
    memory.append_long(
        {
            "goal": goal,
            "steps": steps_taken,
            "tools_used": list(set(tools_used)),
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }
    )

    return {
        "goal": goal,
        "steps_taken": steps_taken,
        "tools_used": list(set(tools_used)),
        "log": log,
        "summary": summary,
        "tasks": current_tasks.get("tasks", {}),
    }


# ---------- Evaluation ----------


def run_evaluation() -> list[dict]:
    """Run test cases through the agent and score results."""
    persist = Path(__file__).parent / "agent_memory.json"
    test_goals = [
        "Plan a new project",
        "Review and organize tasks",
        "Give me a summary report",
    ]

    results = []
    for goal in test_goals:
        # Fresh memory per test
        if persist.exists():
            persist.unlink()
        mem = AgentMemory(persist)

        try:
            outcome = run_agent(goal, mem)
            passed = outcome["steps_taken"] > 0 and len(outcome["log"]) > 0
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

    # Cleanup
    if persist.exists():
        persist.unlink()

    return results


# ---------- Display ----------


def print_results(result: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  CAPSTONE AGENT — Run Complete")
    print(f"{'=' * 60}")
    print(f"  Goal:   {result['goal']}")
    print(f"  Steps:  {result['steps_taken']}")
    print(f"  Tools:  {', '.join(result['tools_used'])}")
    print(f"\n  Transcript:")
    for entry in result["log"]:
        status = "OK" if entry["success"] else "FAIL"
        print(
            f"    [{status}] Step {entry['step']}: {entry['action']} — {entry['message']}"
        )
    print(f"\n  Summary: {result['summary']}")
    print(f"{'=' * 60}")


def main() -> None:
    print("=" * 60)
    print("  CAPSTONE AGENT — Complete Mini-Agent Demo")
    print("=" * 60)

    # Run the agent
    persist = Path(__file__).parent / "agent_memory.json"
    mem = AgentMemory(persist)
    result = run_agent("Plan a new project and give me a summary report", mem)
    print_results(result)

    # Run evaluation
    print(f"\n{'=' * 60}")
    print("  EVALUATION — Running 3 test cases")
    print(f"{'=' * 60}")

    eval_results = run_evaluation()
    for r in eval_results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['goal']} — {r['steps']} step(s)")

    passed = sum(1 for r in eval_results if r["passed"])
    print(f"\n  Result: {passed}/{len(eval_results)} passed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
