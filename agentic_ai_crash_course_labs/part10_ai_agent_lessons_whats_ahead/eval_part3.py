"""
Part 10 — Eval harness for the Part 3 tools agent.

Runs test cases, captures behavior, prints a results table, and saves a JSON
log for comparison across runs. No real "token counting" — we use characters
as a proxy since we're going through the CLI.

Run:  python eval_part3.py
"""

import json
import os
import subprocess
import sys
import time

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/minimax-m3")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "eval_results.json")


# ---------- Test cases ----------
# Each case:
#   id           — short label
#   prompt       — user input
#   must_call    — tool(s) the agent MUST call (empty list = no tool)
#   must_not_call — tool(s) the agent MUST NOT call
#   must_contain — substrings expected in the final answer
#   must_not_contain — substrings forbidden in the final answer

TEST_CASES = [
    {
        "id": "add_simple",
        "prompt": "What's 17 + 25?",
        "must_call": ["add"],
        "must_not_call": ["get_joke", "get_weather"],
        "must_contain": ["42"],
        "must_not_contain": [],
    },
    {
        "id": "joke_cats",
        "prompt": "Tell me a joke about cats",
        "must_call": ["get_joke"],
        "must_not_call": ["add", "get_weather"],
        "must_contain": [],  # hard to assert joke content
        "must_not_contain": [],
    },
    {
        "id": "philosophy_no_tool",
        "prompt": "What's the meaning of life?",
        "must_call": [],  # should NOT call any tool
        "must_not_call": ["add", "get_joke", "get_weather"],
        "must_contain": [],
        "must_not_contain": [],
    },
    {
        "id": "weather_london",
        "prompt": "What's the weather in London right now?",
        "must_call": ["get_weather"],
        "must_not_call": ["add", "get_joke"],
        "must_contain": ["14"],
        "must_not_contain": [],
    },
    {
        "id": "chained_2step",
        "prompt": "Add 7 and 8, then tell me a joke about the result.",
        "must_call": ["add", "get_joke"],
        "must_not_call": ["get_weather"],
        "must_contain": ["15"],
        "must_not_contain": [],
    },
]


# ---------- LLM call (same shape as part 3, kept self-contained) ----------

SYSTEM_PROMPT = """You are an agent that can call tools to answer the user.

RULES (strict):
- Output ONLY a single JSON object. No prose, no markdown outside the JSON.
- If a relevant tool is available, you MUST call it before answering.
- Use {"action": "answer", ...} ONLY when you have all the info needed to fully answer the user.
- Never invent tools that are not listed below.
- CRITICAL: Once you have received the tool result you asked for, your NEXT turn MUST be
  {"action": "answer", "text": "..."} with the final answer to the user. Do not call another
  tool after you already have the result you need. Do not loop.

Available tools (schemas):

1. add(a: number, b: number) -> number
   Use for: any arithmetic addition.

2. get_joke(topic: string) -> string
   Use for: requests for jokes, humor, funny lines. Topic is a single word.

3. get_weather(city: string) -> {"found": bool, "temp_c": int, "condition": str}
   Use for: current weather questions about a specific city.

Response shape (one of these, nothing else):

{"action": "call_tool", "tool": "<name>", "args": { ... }}
{"action": "answer", "text": "<final answer to the user>"}
"""

JOKES = {
    "cats": "Why do cats love laptops? Because they have mice.",
    "dogs": "What do you call a dog that does magic? A Labracadabrador.",
    "ai": "Why did the LLM cross the road? To optimize the chicken's path on the other side.",
    "default": "Why did the developer go broke? Because they used up all their cache.",
}
WEATHER = {
    "london": {"temp_c": 14, "condition": "rainy and overcast"},
    "tokyo": {"temp_c": 31, "condition": "humid and partly cloudy"},
    "new york": {"temp_c": 22, "condition": "sunny"},
    "sydney": {"temp_c": 18, "condition": "clear"},
}

TOOLS = {
    "add": lambda a, b: float(a) + float(b),
    "get_joke": lambda topic: JOKES.get(
        (topic or "").strip().lower(), JOKES["default"]
    ),
    "get_weather": lambda city: (
        {"found": True, **WEATHER[city.strip().lower()]}
        if city.strip().lower() in WEATHER
        else {"found": False, "error": f"no data for '{city}'"}
    ),
}


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


def run_agent(question: str, max_steps: int = 5) -> dict:
    """Same loop as part 3; returns transcript + final + tools called."""
    transcript = []
    tools_called: list[str] = []
    step = ask_llm(f"{SYSTEM_PROMPT}\nUser question: {question}")
    transcript.append(("llm", step))

    for _ in range(max_steps):
        try:
            decision = json.loads(step)
        except json.JSONDecodeError:
            return {
                "transcript": transcript,
                "final": f"(LLM did not return valid JSON: {step[:200]})",
                "tools_called": tools_called,
            }
        if decision.get("action") == "answer":
            return {
                "transcript": transcript,
                "final": decision.get("text", ""),
                "tools_called": tools_called,
            }
        if decision.get("action") == "call_tool":
            name = decision.get("tool")
            args = decision.get("args", {})
            tools_called.append(name)
            transcript.append(("call", {"tool": name, "args": args}))
            try:
                observation = TOOLS[name](**args)
            except Exception as e:
                observation = {"error": str(e)}
            transcript.append(("obs", observation))
            step = ask_llm(
                f"{SYSTEM_PROMPT}\n"
                f"User question: {question}\n"
                f"Last tool call: {name}({args})\n"
                f"Tool returned: {json.dumps(observation)}\n\n"
                f"What next?"
            )
            transcript.append(("llm", step))
            continue
        return {
            "transcript": transcript,
            "final": f"(unknown action: {step[:200]})",
            "tools_called": tools_called,
        }
    return {
        "transcript": transcript,
        "final": "(hit max steps)",
        "tools_called": tools_called,
    }


# ---------- Eval runner ----------


def evaluate_case(case: dict) -> dict:
    started = time.time()
    result = run_agent(case["prompt"])
    elapsed = time.time() - started

    final = result["final"].lower()
    called = result["tools_called"]
    transcript_chars = sum(len(str(t)) for t in result["transcript"])

    checks: list[tuple[str, bool, str]] = []

    # must_call
    for tool in case["must_call"]:
        ok = tool in called
        checks.append(
            (f"called {tool}", ok, "" if ok else f"expected {tool}, got {called}")
        )
    # must_not_call
    for tool in case["must_not_call"]:
        ok = tool not in called
        checks.append((f"not {tool}", ok, "" if ok else f"unexpectedly called {tool}"))

    # must_contain (case-insensitive)
    for needle in case["must_contain"]:
        ok = needle.lower() in final
        checks.append(
            (
                f"contains '{needle}'",
                ok,
                "" if ok else f"final did not contain '{needle}'",
            )
        )
    # must_not_contain
    for needle in case["must_not_contain"]:
        ok = needle.lower() not in final
        checks.append(
            (
                f"!contains '{needle}'",
                ok,
                "" if ok else f"final unexpectedly contained '{needle}'",
            )
        )

    passed = all(c[1] for c in checks)
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "tools_called": called,
        "final": result["final"],
        "elapsed_s": round(elapsed, 2),
        "transcript_chars": transcript_chars,
        "checks": [{"name": n, "ok": ok, "note": note} for n, ok, note in checks],
        "passed": passed,
    }


def print_table(results: list[dict]) -> None:
    print()
    print(f"{'ID':<22} {'PASS/FAIL':<10} {'TIME':<7} {'CHARS':<7} TOOLS")
    print("-" * 72)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        tools = ",".join(r["tools_called"]) or "-"
        print(
            f"{r['id']:<22} {status:<10} {r['elapsed_s']:<7} {r['transcript_chars']:<7} {tools}"
        )
    print()
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"Summary: {passed}/{total} passed ({100 * passed / total:.0f}%)")
    print()
    # Detail for any failure
    for r in results:
        if not r["passed"]:
            print(f"  FAIL: {r['id']}  (prompt: {r['prompt']!r})")
            for c in r["checks"]:
                if not c["ok"]:
                    print(f"     - {c['name']}: {c['note']}")
            print(f"     final: {r['final']!r}")


# ---------- Main ----------


if __name__ == "__main__":
    print(f"Model: {MODEL}\n")
    print(f"Running {len(TEST_CASES)} test cases...\n")

    results = []
    for case in TEST_CASES:
        print(f"  -> {case['id']} ...", end="", flush=True)
        r = evaluate_case(case)
        results.append(r)
        print(f" {'PASS' if r['passed'] else 'FAIL'}  ({r['elapsed_s']}s)")

    print_table(results)

    # Persist for future comparison
    log = {
        "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": results,
    }
    # Strip the verbose transcript from the logged version
    slim = {
        "model": MODEL,
        "timestamp": log["timestamp"],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
        },
        "results": [
            {
                k: v
                for k, v in r.items()
                if k != "checks"
                if k != "final"
                if k != "prompt"
            }
            for r in results
        ],
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(slim, f, indent=2)
    print(f"Results saved to {RESULTS_PATH}")
