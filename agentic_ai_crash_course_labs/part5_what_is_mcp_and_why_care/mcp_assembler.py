"""
Part 5 — MCP-style request assembler: package task + tools + docs + memory
into one structured JSON payload, validate it, simulate a model call.

This is NOT a real MCP client — it's a tiny "what does the payload look like"
demo. The real Model Context Protocol is JSON-RPC over a transport; here we
just show the shape.

Run:  python mcp_assembler.py
"""

import json
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")


# ---------- The Context data structure ----------


# Schema (in plain Python — would be a Pydantic model / dataclass in prod)
TOOL_SCHEMA_EXAMPLE = {
    "name": "send_email",
    "description": "Send an email to a recipient.",
    "params": {
        "to": "string (email address)",
        "subject": "string",
        "body": "string",
    },
}


def make_context(
    task: str,
    tools: list[dict] | None = None,
    retrieved_docs: list[str] | None = None,
    memory: list[dict] | None = None,
    instructions: str = "",
) -> dict:
    return {
        "protocol": "mcp-like/v1",
        "task": task,
        "tools": tools or [],
        "retrieved_docs": retrieved_docs or [],
        "memory": memory or [],
        "instructions": instructions,
    }


# ---------- The assembler ----------


def assemble_mcp_request(context: dict) -> dict:
    """Package the context into a single JSON-ready payload (the 'request')."""
    return {
        "jsonrpc": "2.0",  # MCP-style framing
        "method": "model.complete",  # what we're asking for
        "params": {
            "task": context["task"],
            "tools": context["tools"],
            "context": {
                "retrieved_docs": context["retrieved_docs"],
                "memory": context["memory"],
                "instructions": context["instructions"],
            },
            # A "model hint" — what we'd want the LLM to do
            "response_shape": {
                "action": "call_tool | answer",
                "tool": "<name if call_tool>",
                "args": "<object of tool params>",
                "text": "<answer if action=answer>",
            },
        },
    }


# ---------- Validator (bonus) ----------


def validate_request(request: dict) -> list[str]:
    """Return a list of human-readable warnings about missing/odd fields."""
    warnings: list[str] = []
    params = request.get("params", {})

    if not params.get("task"):
        warnings.append("no task provided")

    tools = params.get("tools", [])
    if not tools:
        warnings.append("no tools registered")
    for t in tools:
        if not t.get("name"):
            warnings.append(f"tool missing 'name': {t}")
        if not t.get("description"):
            warnings.append(f"tool '{t.get('name', '?')}' has no description")

    docs = params.get("context", {}).get("retrieved_docs", [])
    if not docs:
        warnings.append("no retrieved docs (RAG layer is empty)")

    memory = params.get("context", {}).get("memory", [])
    if not memory:
        warnings.append("memory is empty (no prior conversation)")

    instructions = params.get("context", {}).get("instructions", "")
    if not instructions:
        warnings.append("no system instructions")

    if "response_shape" not in params:
        warnings.append("no response_shape declared — model output may be unstructured")

    return warnings


# ---------- Simulated LLM call ----------


def simulate_llm_call(request: dict) -> dict:
    """Print the assembled request and return a hardcoded response.
    (In real MCP, this is where the model client would be invoked.)"""
    print("--- ASSEMBLED MCP REQUEST (what the model actually sees) ---")
    try:
        print(json.dumps(request, indent=2, ensure_ascii=False))
    except TypeError as e:
        print(f"(could not JSON-serialize: {e})")
        print(repr(request))
    print("--- END REQUEST ---\n")

    # Look at the task + tools and produce a plausible hardcoded response
    params = request["params"]
    task = params["task"]
    tool_names = [t["name"] for t in params["tools"]]

    if "send_email" in tool_names and "email" in task.lower():
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "action": "call_tool",
                "tool": "send_email",
                "args": {
                    "to": "john@example.com",
                    "subject": "Summary as requested",
                    "body": "(summary text from retrieved doc would go here)",
                },
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "action": "answer",
            "text": f"(hardcoded response to: {task[:60]})",
        },
    }


# ---------- Display helpers ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# ---------- The test from the README ----------


if __name__ == "__main__":
    banner("TEST 1: The README's example")
    context = make_context(
        task="Summarize the doc and email it to john@example.com using send_email.",
        tools=[
            {
                "name": "send_email",
                "description": "Send an email to a recipient.",
                "params": {
                    "to": "string (email address)",
                    "subject": "string",
                    "body": "string",
                },
            },
            {
                "name": "search_docs",
                "description": "Search the internal knowledge base.",
                "params": {"query": "string"},
            },
        ],
        retrieved_docs=[
            "opencode is an open source AI coding agent that runs in your terminal.",
        ],
        memory=[
            {"role": "user", "content": "Hey, can you help with a quick summary?"},
            {"role": "assistant", "content": "Sure — which doc?"},
            {"role": "user", "content": "The opencode one. Then email it to John."},
        ],
        instructions="You are a helpful assistant. Always ground answers in the provided context.",
    )

    request = assemble_mcp_request(context)

    warnings = validate_request(request)
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("No warnings — request is complete.\n")

    response = simulate_llm_call(request)
    print("--- SIMULATED LLM RESPONSE ---")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    # ---------- Bonus: a deliberately empty / broken request to show the validator in action ----------

    banner("TEST 2: Empty / broken request (validator in action)")
    empty_context = make_context(task="", tools=[], retrieved_docs=[], memory=[])
    empty_request = assemble_mcp_request(empty_context)
    print("WARNINGS for empty request:")
    for w in validate_request(empty_request):
        print(f"  - {w}")

    # ---------- Bonus: a request that's missing the 'description' on a tool ----------

    banner("TEST 3: Tool with missing description")
    weird_context = make_context(
        task="Do something.",
        tools=[{"name": "do_thing", "params": {}}],  # no description
        retrieved_docs=["some doc"],
        memory=[{"role": "user", "content": "hi"}],
        instructions="be helpful",
    )
    weird_request = assemble_mcp_request(weird_context)
    print("WARNINGS for weird request:")
    for w in validate_request(weird_request):
        print(f"  - {w}")
