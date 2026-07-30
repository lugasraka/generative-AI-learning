"""
Part 3 — Tools in AI: a 3-tool agent built from scratch, no frameworks.

Tools (the "hands"):
  - add(a, b)              -> number
  - get_joke(topic)        -> string
  - get_weather(city)      -> dict  (mocked, reused from Part 1)

The loop (the "agent"):
  user prompt
     -> LLM returns JSON decision (call_tool or answer)
     -> if call_tool: execute, observe, loop back
     -> if answer: print and stop

Run:  python tools_agent.py
"""

import json
import os
import subprocess
import sys

# Force UTF-8 stdout on Windows (for ° etc.)
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/minimax-m3")

# ---------- Tool definitions ----------


JOKES = {
    "cats": "Why do cats love laptops? Because they have mice.",
    "dogs": "What do you call a dog that does magic? A Labracadabrador.",
    "ai": "Why did the LLM cross the road? To optimize the chicken's path on the other side.",
    "default": "Why did the developer go broke? Because they used up all their cache.",
}

WEATHER = {
    "tokyo": {"temp_c": 31, "condition": "humid and partly cloudy"},
    "london": {"temp_c": 14, "condition": "rainy and overcast"},
    "new york": {"temp_c": 22, "condition": "sunny"},
    "sydney": {"temp_c": 18, "condition": "clear"},
}


def add(a: float, b: float) -> float:
    return float(a) + float(b)


def get_joke(topic: str) -> str:
    key = (topic or "").strip().lower()
    return JOKES.get(key, JOKES["default"])


def get_weather(city: str) -> dict:
    key = (city or "").strip().lower()
    if key in WEATHER:
        return {"found": True, **WEATHER[key]}
    return {"found": False, "error": f"no data for '{city}'"}


# Tool registry: name -> (callable, JSON schema for the LLM)
TOOLS = {
    "add": add,
    "get_joke": get_joke,
    "get_weather": get_weather,
}

TOOL_SCHEMAS = {
    "add": {
        "description": "Add two numbers and return the sum.",
        "params": {"a": "number", "b": "number"},
    },
    "get_joke": {
        "description": "Return a hardcoded joke about a topic.",
        "params": {"topic": "string"},
    },
    "get_weather": {
        "description": "Return mocked current weather for a city.",
        "params": {"city": "string"},
    },
}


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


# ---------- Agent loop ----------


SYSTEM_PROMPT = """You are an agent that can call tools to answer the user.

RULES (strict):
- Output ONLY a single JSON object. No prose, no markdown outside the JSON.
- If a relevant tool is available, you MUST call it before answering.
- Use {"action": "answer", ...} ONLY when you have all the info needed.
- Never invent tools that are not listed below.

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


def run_agent(question: str, max_steps: int = 5) -> dict:
    transcript = []

    step = ask_llm(f"{SYSTEM_PROMPT}\nUser question: {question}")
    transcript.append(("llm", step))

    for _ in range(max_steps):
        try:
            decision = json.loads(step)
        except json.JSONDecodeError:
            return {
                "transcript": transcript,
                "final_answer": f"(LLM did not return valid JSON: {step[:200]})",
            }

        if decision.get("action") == "answer":
            return {
                "transcript": transcript,
                "final_answer": decision.get("text", ""),
            }

        if decision.get("action") == "call_tool":
            name = decision.get("tool")
            args = decision.get("args", {})
            transcript.append(("call", {"tool": name, "args": args}))

            if name in TOOLS:
                try:
                    observation = TOOLS[name](**args)
                except TypeError as e:
                    observation = {"error": f"bad args: {e}"}
            else:
                observation = {"error": f"unknown tool: {name}"}
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
            "final_answer": f"(unknown action: {step[:200]})",
        }

    return {"transcript": transcript, "final_answer": "(hit max steps)"}


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def show(transcript, final):
    for i, (role, content) in enumerate(transcript, 1):
        if role == "llm":
            print(f"  [{i}] LLM : {content}")
        elif role == "call":
            print(f"  [{i}] CALL: {content['tool']}({content['args']})")
        elif role == "obs":
            print(f"  [{i}] OBS : {json.dumps(content)}")
    print(f"\n  >> {final}")


# ---------- Test prompts from the README ----------


TESTS = [
    "What's 17 + 25?",
    "Tell me a joke about cats",
    "What's the meaning of life?",
    # bonus 2-step:
    "Add 7 and 8, then tell me a joke about the result.",
    # mix in a third tool:
    "What's the weather in London right now?",
]


if __name__ == "__main__":
    print(f"Model: {MODEL}  (override: set OPENCODE_MODEL=...)\n")
    for q in TESTS:
        banner(f"PROMPT: {q}")
        result = run_agent(q)
        show(result["transcript"], result["final_answer"])
