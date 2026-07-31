"""
Part 1 — Thinking vs. Doing: a side-by-side demo of an LLM with and without tools.

Run:  python thinking_vs_doing.py
"""

import json
import random
import subprocess
import sys
import os

# ---------- Config ----------

# Pick a model. Free options (no payment needed):
#   opencode/deepseek-v4-flash-free
#   opencode/laguna-s-2.1-free
#   opencode/ling-3.0-flash-free
#   opencode/mimo-v2.5-free
#   opencode/nemotron-3-ultra-free
#   opencode/north-mini-code-free
# Or set the OPENCODE_MODEL env var to override.
MODEL = os.environ.get("OPENCODE_MODEL", "opencode/deepseek-v4-flash-free")

# ---------- Tool definition (the "hands") ----------

WEATHER_DATA = {
    "tokyo": {"temp_c": 31, "condition": "humid and partly cloudy"},
    "london": {"temp_c": 14, "condition": "rainy and overcast"},
    "new york": {"temp_c": 22, "condition": "sunny"},
    "sydney": {"temp_c": 18, "condition": "clear"},
}


def get_weather(city: str) -> dict:
    """Look up the current weather for a city."""
    key = city.strip().lower()
    if key in WEATHER_DATA:
        return {"found": True, **WEATHER_DATA[key]}
    return {"found": False, "error": f"no data for '{city}'"}


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


# ---------- Two modes ----------


def mode_without_tools(question: str) -> str:
    """Just ask the LLM. It can only guess — no tool available."""
    prompt = f"""Answer the following question in 1-2 sentences.
Be honest if you don't actually know the real-time answer.

Question: {question}"""
    return ask_llm(prompt)


def mode_with_tool(question: str) -> dict:
    """Ask the LLM, but give it a tool to call. The loop: reason -> call tool -> answer."""
    system = """You have access to a tool called get_weather(city).
If the user asks about weather, you MUST call it. Respond with a single JSON object in this exact shape:

{"action": "call_tool", "tool": "get_weather", "args": {"city": "<city name in english>"}}

If the question is not about weather, respond with:

{"action": "answer", "text": "<your short answer>"}
"""

    step1 = ask_llm(f"{system}\n\nUser question: {question}")

    # Parse the LLM's structured decision
    try:
        decision = json.loads(step1)
    except json.JSONDecodeError:
        return {
            "llm_decision": step1,
            "observation": None,
            "final_answer": "(LLM did not return valid JSON — try again)",
        }

    if decision.get("action") == "call_tool":
        tool_name = decision["tool"]
        args = decision.get("args", {})
        if tool_name == "get_weather":
            observation = get_weather(**args)
        else:
            observation = {"error": f"unknown tool: {tool_name}"}

        # Step 2: feed the observation back to the LLM for a final grounded answer
        final = ask_llm(
            f"User question: {question}\n"
            f"Tool call: {tool_name}({args})\n"
            f"Tool returned: {json.dumps(observation)}\n\n"
            f"Now answer the user in 1 short paragraph, grounded in the tool result."
        )
        return {
            "llm_decision": step1,
            "tool_called": f"{tool_name}({args})",
            "observation": observation,
            "final_answer": final,
        }

    return {
        "llm_decision": step1,
        "tool_called": None,
        "observation": None,
        "final_answer": decision.get("text", ""),
    }


# ---------- Side-by-side demo ----------


def banner(title: str):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def demo():
    question = "What's the weather in Tokyo right now?"

    banner("WITHOUT TOOLS  (LLM is just guessing)")
    without = mode_without_tools(question)
    print(without)

    banner("WITH TOOLS  (LLM reasons -> calls get_weather -> grounds answer)")
    with_tool = mode_with_tool(question)
    print(f"LLM's structured decision : {with_tool['llm_decision']}")
    print(f"Tool called               : {with_tool.get('tool_called')}")
    print(f"Tool returned (observe)   : {json.dumps(with_tool['observation'])}")
    print(f"Final grounded answer     :\n{with_tool['final_answer']}")

    banner("THE DIFFERENCE")
    print("Without tools, the LLM produces plausible text but can't know reality.")
    print(
        "With tools,    the LLM produces a structured call, gets real data, and grounds its answer."
    )


if __name__ == "__main__":
    demo()
