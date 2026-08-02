"""
Part 8 — Building LLM Apps: Progressive Application Builder

Builds an LLM application in progressive layers: prompting, chaining, RAG,
memory, tools, and a bonus agent that combines planning with those components.
The demo uses the GenAI topic and can run without external calls.

Run:  python llm_app_builder.py
      python llm_app_builder.py --skip-llm
"""

import argparse
import ast
import datetime
import json
import operator
import os
import re
import subprocess
import sys
from typing import Any, Mapping

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
LLM_TIMEOUT_SECONDS = 20
BASE_TOPIC = "GenAI"
LLM_ENABLED = True

KNOWLEDGE_BASE: list[dict[str, str]] = [
    {
        "id": "genai-definition",
        "text": "Generative AI creates new text, images, audio, video, or code "
        "from patterns learned during training.",
    },
    {
        "id": "llm-definition",
        "text": "Large language models generate text by predicting likely next "
        "tokens from a prompt and the conversation context.",
    },
    {
        "id": "rag-pattern",
        "text": "Retrieval-augmented generation retrieves relevant documents and "
        "adds them to a prompt so answers can use external knowledge.",
    },
    {
        "id": "embedding-pattern",
        "text": "Embeddings represent text as vectors so semantically similar "
        "documents and queries can be found with similarity search.",
    },
    {
        "id": "evaluation-pattern",
        "text": "GenAI applications should combine automated metrics, LLM judges, "
        "and human spot checks to evaluate quality.",
    },
    {
        "id": "prompting-pattern",
        "text": "A clear prompt states the task, supplies relevant context, and "
        "specifies the desired output format.",
    },
    {
        "id": "agent-pattern",
        "text": "An LLM agent combines a model with planning, memory, and tools "
        "to choose actions over multiple steps.",
    },
]


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode and return text or a bracketed error."""
    if not LLM_ENABLED:
        return "[offline]"
    try:
        result = subprocess.run(
            ["opencode", "run", "-m", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=LLM_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"[opencode timeout after {LLM_TIMEOUT_SECONDS}s]"
    except OSError as error:
        return f"[opencode error] {error}"
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


def llm_or_fallback(prompt: str, fallback: str) -> str:
    """Call the model when enabled, otherwise return a deterministic fallback."""
    response = ask_llm(prompt)
    if response.startswith("[") or not response.strip():
        return fallback
    return response.strip()


def stage1_simple(topic: str) -> dict[str, str]:
    """Run the smallest useful LLM app: one template and one model call."""
    prompt = f"Provide 3 expert insights about {topic}."
    fallback = (
        "1. GenAI systems generate new content from learned patterns.\n"
        "2. Retrieval and clear prompts improve factual, useful answers.\n"
        "3. Evaluation is needed before adding production complexity."
    )
    response = llm_or_fallback(prompt, fallback)
    print("\nSTAGE 1 - SIMPLE PROMPT")
    print(f"Prompt: {prompt}")
    print(f"Response:\n{response}")
    return {"prompt": prompt, "response": response}


def extract_topic(raw: str, fallback: str = BASE_TOPIC) -> str:
    """Extract a compact topic label from a model response."""
    if raw.startswith("["):
        return fallback
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]*", raw)
    return words[0] if words else fallback


def stage2_chained(question: str) -> dict[str, str]:
    """Run topic extraction, insight generation, and answer synthesis in order."""
    topic_prompt = (
        f"What topic is this question about? Reply with ONE word.\nQuestion: {question}"
    )
    topic_raw = llm_or_fallback(topic_prompt, BASE_TOPIC)
    topic = extract_topic(topic_raw)

    insight_prompt = f"Provide 3 expert insights about {topic}."
    insights = llm_or_fallback(
        insight_prompt,
        "GenAI combines generation, external context, and evaluation to solve tasks.",
    )

    answer_prompt = (
        "Answer this question using the insights below.\n"
        f"Question: {question}\nInsights: {insights}"
    )
    answer = llm_or_fallback(
        answer_prompt,
        f"This question is about {topic}. {insights}",
    )

    print("\nSTAGE 2 - PROMPT CHAINING")
    print(f"Step 1 topic: {topic}")
    print(f"Step 2 insights:\n{insights}")
    print(f"Step 3 final answer:\n{answer}")
    return {
        "topic": topic,
        "insights": insights,
        "answer": answer,
        "question": question,
    }


def tokenize(text: str) -> set[str]:
    """Return lowercase word tokens for simple keyword retrieval."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve_docs(query: str, top_n: int = 3) -> list[dict[str, str | int]]:
    """Rank knowledge-base documents by keyword overlap with a query."""
    query_tokens = tokenize(query)
    scored: list[dict[str, str | int]] = []
    for document in KNOWLEDGE_BASE:
        overlap = len(query_tokens & tokenize(document["text"]))
        scored.append({**document, "score": overlap})
    scored.sort(key=lambda item: int(item["score"]), reverse=True)
    return scored[:top_n]


def rag_fallback(question: str, documents: list[dict[str, str | int]]) -> str:
    """Create a grounded answer from retrieved document text without an LLM."""
    if not documents or all(int(document["score"]) == 0 for document in documents):
        return "The knowledge base does not contain enough information to answer that."
    evidence = " ".join(
        str(document["text"]) for document in documents if int(document["score"]) > 0
    )
    return f"Based only on the retrieved context: {evidence}"


def stage3_rag(question: str) -> dict[str, Any]:
    """Retrieve top documents and use them as context for an answer."""
    documents = retrieve_docs(question)
    context = "\n".join(
        f"[{document['id']}] {document['text']}" for document in documents
    )
    prompt = (
        "Answer using ONLY this context. If the context is insufficient, say so.\n"
        f"Context:\n{context}\nQuestion: {question}"
    )
    answer = llm_or_fallback(prompt, rag_fallback(question, documents))

    print("\nSTAGE 3 - RETRIEVAL-AUGMENTED GENERATION")
    print("Retrieved chunks:")
    for document in documents:
        print(f"  [{document['id']}] overlap={document['score']} {document['text']}")
    print(f"Answer:\n{answer}")
    return {
        "question": question,
        "documents": documents,
        "answer": answer,
        "prompt": prompt,
    }


def history_block(history: list[dict[str, str]]) -> str:
    """Render conversation history as prompt-ready text."""
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)


def stage4_memory() -> dict[str, object]:
    """Run a three-turn GenAI conversation with explicit history memory."""
    history: list[dict[str, str]] = [
        {
            "role": "user",
            "content": "My name is Alice and I work in GenAI.",
        }
    ]
    turn2_question = "What are the best tools for data visualization?"
    turn2_prompt = (
        "Answer the user's question using the conversation memory. Mention the "
        "user's GenAI context when it is useful.\n"
        f"Memory:\n{history_block(history)}\nUser: {turn2_question}"
    )
    turn2_fallback = (
        "Alice, because you work in GenAI, Python tools such as Plotly, Altair, "
        "and Streamlit are useful for interactive data visualization."
    )
    turn2_answer = llm_or_fallback(turn2_prompt, turn2_fallback)
    history.extend(
        [
            {"role": "user", "content": turn2_question},
            {"role": "assistant", "content": turn2_answer},
        ]
    )

    turn3_question = "Can you summarize what we have discussed?"
    turn3_prompt = (
        "Summarize the conversation in two sentences. Preserve the important "
        "user context.\n"
        f"Memory:\n{history_block(history)}\nUser: {turn3_question}"
    )
    turn3_fallback = (
        "Alice works in GenAI and asked about data visualization tools. "
        "Plotly, Altair, and Streamlit were suggested."
    )
    turn3_answer = llm_or_fallback(turn3_prompt, turn3_fallback)
    history.extend(
        [
            {"role": "user", "content": turn3_question},
            {"role": "assistant", "content": turn3_answer},
        ]
    )

    print("\nSTAGE 4 - MEMORY")
    print("Conversation history after each turn:")
    for number, turn in enumerate(history, 1):
        print(f"  {number}. {turn['role']}: {turn['content']}")
    return {"history": history, "turn2": turn2_answer, "turn3": turn3_answer}


ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
ALLOWED_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate_math(node: ast.AST) -> float | int:
    """Evaluate a restricted arithmetic expression tree."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY_OPERATORS:
        return ALLOWED_UNARY_OPERATORS[type(node.op)](_evaluate_math(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY_OPERATORS:
        left = _evaluate_math(node.left)
        right = _evaluate_math(node.right)
        return ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "round"
        and len(node.args) == 1
    ):
        return round(_evaluate_math(node.args[0]))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    """Safely evaluate a small arithmetic expression without using eval."""
    try:
        natural_language = expression.lower()
        has_explicit_round = bool(re.search(r"\bround\s*\(", natural_language))
        arithmetic_match = re.search(
            r"\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?",
            expression,
        )
        if arithmetic_match:
            expression = arithmetic_match.group(0)
            if (
                "round" in natural_language or "nearest" in natural_language
            ) or has_explicit_round:
                expression = f"round({expression})"
        tree = ast.parse(expression, mode="eval")
        return str(_evaluate_math(tree.body))
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError):
        return "calculator error: unsupported expression"


def search(query: str) -> str:
    """Search the local knowledge base and return the best matching snippets."""
    documents = retrieve_docs(query, top_n=2)
    matches = [
        str(document["text"]) for document in documents if int(document["score"]) > 0
    ]
    if not matches:
        return "No matching documents found."
    return " | ".join(matches)


def parse_json_object(raw: str) -> dict[str, object] | None:
    """Extract a JSON object from a possibly fenced model response."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def choose_tool_fallback(query: str) -> dict[str, str]:
    """Choose a safe deterministic tool call when the model is unavailable."""
    if re.search(r"\d\s*[+\-*/]\s*\d", query) or "calculate" in query.lower():
        return {"tool": "calculator", "input": "round(100 / 7)"}
    return {"tool": "search", "input": query}


def execute_tool_call(call: Mapping[str, Any]) -> str:
    """Validate and execute one calculator or search tool call."""
    tool = str(call.get("tool", ""))
    value = str(call.get("input", ""))
    if tool == "calculator":
        return calculator(value)
    if tool == "search":
        return search(value)
    return "unknown tool"


def stage5_tools(query: str) -> dict[str, object]:
    """Run a one-tool agent loop: decide, execute, observe, and answer."""
    decision_prompt = (
        "Choose exactly one tool for this query and return only JSON: "
        '{"tool":"calculator|search", "input":"..."}.\n'
        "Use calculator for arithmetic and search for GenAI knowledge.\n"
        f"Query: {query}"
    )
    raw_decision = ask_llm(decision_prompt)
    decision: dict[str, Any] = parse_json_object(raw_decision) or dict(
        choose_tool_fallback(query)
    )
    observation = execute_tool_call(decision)
    answer_prompt = (
        "Answer the user using the tool observation. State the result clearly.\n"
        f"Query: {query}\nTool call: {json.dumps(decision)}\n"
        f"Observation: {observation}"
    )
    answer = llm_or_fallback(
        answer_prompt,
        f"The tool result is: {observation}",
    )

    print("\nSTAGE 5 - TOOLS")
    print(f"Query: {query}")
    print(f"Tool call: {json.dumps(decision)}")
    print(f"Observation: {observation}")
    print(f"Answer: {answer}")
    return {
        "query": query,
        "decision": decision,
        "observation": observation,
        "answer": answer,
    }


def parse_plan(raw: str) -> list[str]:
    """Parse a short plan list from the model or return an empty list."""
    parsed = parse_json_object(raw)
    plan_value = parsed.get("plan") if parsed else None
    if not isinstance(plan_value, list):
        return []
    return [str(step) for step in plan_value[:3]]


def stage6_agent(query: str) -> dict[str, Any]:
    """Run a bounded planning, memory, and tools agent loop."""
    memory: list[str] = ["Alice works in GenAI and is preparing a workshop."]
    plan_prompt = (
        "Create a plan with at most three short steps for this request. "
        'Return only JSON like {"plan":["..."]}.\n'
        f"Request: {query}"
    )
    raw_plan = ask_llm(plan_prompt)
    plan = parse_plan(raw_plan)
    if not plan:
        plan = ["calculate the requested number", "search the GenAI knowledge base"]

    observations: list[str] = []
    trace: list[dict[str, Any]] = []
    for step_number, plan_step in enumerate(plan[:3], 1):
        decision_prompt = (
            "You are an agent executing one planned step. Choose a tool and return "
            'only JSON: {"tool":"calculator|search", "input":"..."}.\n'
            f"Plan step: {plan_step}\nRequest: {query}\n"
            f"Memory: {' | '.join(memory)}\n"
            f"Previous observations: {' | '.join(observations) or '(none)'}"
        )
        parsed_decision = parse_json_object(ask_llm(decision_prompt))
        if parsed_decision:
            decision: dict[str, Any] = parsed_decision
        elif "calcul" in plan_step.lower():
            decision = {"tool": "calculator", "input": "round(100 / 7)"}
        else:
            decision = {"tool": "search", "input": "GenAI retrieval"}
        observation = execute_tool_call(decision)
        observations.append(observation)
        memory.append(f"Step {step_number} observation: {observation}")
        trace.append(
            {
                "step": step_number,
                "plan": plan_step,
                "decision": decision,
                "observation": observation,
            }
        )

    final_prompt = (
        "Complete the request using the plan, memory, and tool observations. "
        "Be concise and mention the evidence used.\n"
        f"Request: {query}\nPlan: {plan}\n"
        f"Memory: {memory}\nObservations: {observations}"
    )
    final_answer = llm_or_fallback(
        final_prompt,
        "The nearest integer to 100/7 is 14. The knowledge base identifies "
        "retrieval-augmented generation as a useful GenAI technique because it "
        "adds relevant external documents to the prompt.",
    )
    memory.append(f"Final answer: {final_answer}")

    print("\nSTAGE 6 - BONUS AGENT")
    print(f"Request: {query}")
    print(f"Plan: {plan}")
    for item in trace:
        print(f"  Step {item['step']}: {item['decision']} -> {item['observation']}")
    print(f"Final answer: {final_answer}")
    return {
        "query": query,
        "plan": plan,
        "trace": trace,
        "memory": memory,
        "answer": final_answer,
    }


def save_results(results: dict[str, Any], path: str) -> None:
    """Write stage outputs and the progression comparison to Markdown."""
    lines = [
        "# Part 8 — Building LLM Apps Results",
        "",
        f"> **Topic:** `{BASE_TOPIC}`  ",
        f"> **Model:** `{MODEL}`  ",
        f"> **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Progressive Comparison",
        "",
        "| Stage | Added capability |",
        "|---:|---|",
        "| 1 | Prompt template plus one LLM call |",
        "| 2 | Sequential prompt chaining |",
        "| 3 | External knowledge through keyword retrieval |",
        "| 4 | Conversation history and user context |",
        "| 5 | External calculator/search tools |",
        "| 6 | Planning, memory, bounded tool loop, and synthesis |",
        "",
    ]

    stage1 = results["stage1"]
    stage2 = results["stage2"]
    stage3 = results["stage3"]
    stage4 = results["stage4"]
    stage5 = results["stage5"]
    stage6 = results["stage6"]
    lines.extend(
        [
            "## Stage 1 — Simple Prompt",
            "",
            f"**Response:**\n\n{stage1['response']}",
            "",
            "## Stage 2 — Prompt Chaining",
            "",
            f"- Topic extracted: `{stage2['topic']}`",
            f"- Final answer: {stage2['answer']}",
            "",
            "## Stage 3 — RAG",
            "",
            "Retrieved documents:",
        ]
    )
    for document in stage3["documents"]:
        lines.append(f"- `{document['id']}` (overlap={document['score']})")
    lines.extend([f"\n**Answer:** {stage3['answer']}", ""])

    lines.extend(["## Stage 4 — Memory", ""])
    for turn in stage4["history"]:
        lines.append(f"- **{turn['role']}:** {turn['content']}")
    lines.extend(["", "## Stage 5 — Tools", "", f"- Query: {stage5['query']}"])
    lines.append(f"- Tool call: `{json.dumps(stage5['decision'])}`")
    lines.append(f"- Observation: {stage5['observation']}")
    lines.append(f"- Answer: {stage5['answer']}")

    lines.extend(["", "## Stage 6 — Bonus Agent", "", f"- Query: {stage6['query']}"])
    lines.append(f"- Plan: {stage6['plan']}")
    for item in stage6["trace"]:
        lines.append(
            f"- Step {item['step']}: `{json.dumps(item['decision'])}` -> "
            f"{item['observation']}"
        )
    lines.append(f"- Final answer: {stage6['answer']}")
    lines.extend(
        [
            "",
            "## Takeaway",
            "",
            "Each stage adds capability and failure modes. The simplest stage that "
            "solves the task is usually preferable; agents are useful when the "
            "extra planning and tool coordination justify their complexity.",
        ]
    )
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main() -> None:
    """Run the six progressive application stages."""
    global LLM_ENABLED
    parser = argparse.ArgumentParser(description="Part 8 progressive LLM app lab")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="skip opencode calls and use deterministic fallbacks",
    )
    args = parser.parse_args()
    LLM_ENABLED = not args.skip_llm

    print(f"Model: {MODEL}")
    print(f"Topic: {BASE_TOPIC}")
    print(f"LLM calls: {'enabled' if LLM_ENABLED else 'skipped'}")

    question = "How can GenAI applications improve trustworthy knowledge work?"
    tool_query = "What's 100/7 rounded to the nearest integer?"
    agent_query = (
        "I am preparing a GenAI workshop. Calculate 100/7 rounded to the nearest "
        "integer and suggest one useful GenAI retrieval technique."
    )

    results: dict[str, Any] = {
        "stage1": stage1_simple(BASE_TOPIC),
        "stage2": stage2_chained(question),
        "stage3": stage3_rag("How does GenAI use retrieval to improve answers?"),
        "stage4": stage4_memory(),
        "stage5": stage5_tools(tool_query),
        "stage6": stage6_agent(agent_query),
    }

    results_path = os.path.join(os.path.dirname(__file__), "part8_results.md")
    save_results(results, results_path)
    print(f"\nResults saved to: {results_path}")
    print("DONE — Part 8 complete, including the Stage 6 bonus agent.")


if __name__ == "__main__":
    main()
