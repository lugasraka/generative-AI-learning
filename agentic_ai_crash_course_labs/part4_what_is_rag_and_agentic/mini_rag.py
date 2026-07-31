"""
Part 4 — RAG from scratch: chunk -> index (keyword) -> retrieve -> generate.

Topic: the opencode CLI (because you're literally using it).
Methods: naive sentence chunking, keyword-overlap retrieval, opencode CLI as generator.

Run:  python mini_rag.py
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

# ---------- 1. The "knowledge base" (8 short docs about opencode) ----------

DOCS = [
    "opencode is an open source AI coding agent that runs in your terminal.",
    "It supports many model providers including OpenAI, Anthropic, Google, and Groq.",
    "The default command `opencode` launches an interactive TUI in your project directory.",
    "The `opencode run <prompt>` command lets you send a one-shot prompt and print the response.",
    "You can pick a model with `opencode run -m <provider/model>`, for example `opencode run -m opencode/gpt-5-nano`.",
    "Free models are available in the `opencode-go/` namespace, for example `opencode-go/minimax-m3`.",
    "Sessions can be resumed with `opencode run -c` (last session) or `opencode run -s <session-id>`.",
    "opencode ships with an ACP server (`opencode acp`) and a headless server (`opencode serve`) for IDE integrations.",
    "The `opencode mcp` subcommand manages Model Context Protocol servers for tool integrations.",
    "opencode is written in Go and TypeScript and is distributed under the MIT license.",
]

# ---------- 2. Naive chunker (sentence-level) ----------


def chunk(text: str) -> list[str]:
    """Split a document into sentence-level chunks."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


CHUNKS: list[dict] = []  # list of {"id", "text", "tokens"}
for di, doc in enumerate(DOCS):
    for ci, sentence in enumerate(chunk(doc)):
        tokens = set(re.findall(r"[a-z0-9]+", sentence.lower()))
        CHUNKS.append({"id": f"d{di}s{ci}", "text": sentence, "tokens": tokens})


# ---------- 3. Retriever (keyword overlap) ----------


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "you",
    "it",
    "this",
    "that",
    "as",
    "by",
    "be",
    "at",
}


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS}


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Score chunks by keyword overlap; return top_k."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return []
    scored = []
    for ch in CHUNKS:
        overlap = len(q_tokens & ch["tokens"])
        if overlap > 0:
            scored.append((overlap, ch))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [ch for _, ch in scored[:top_k]]


# ---------- 4. Generator (opencode CLI) ----------


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


def generate(query: str, chunks: list[dict]) -> str:
    """Generator: stuff retrieved chunks into the prompt, ask the LLM."""
    if not chunks:
        context = "(no relevant context found in the knowledge base)"
    else:
        context = "\n".join(f"- {c['text']}" for c in chunks)
    prompt = f"""You are answering using ONLY the context below. If the answer is not in the context, say so.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
    return ask_llm(prompt)


# ---------- 5. Agentic RAG (bonus): retrieve -> answer -> retrieve-again -> refine ----------


def agentic_rag(query: str) -> dict:
    """First pass: retrieve and answer. Second pass: re-retrieve to check/refine."""
    chunks_1 = retrieve(query, top_k=2)
    answer_1 = generate(query, chunks_1)

    # Reflect: ask the model what it would want to look up next to verify or improve
    reflection = ask_llm(
        f"You just answered the question below using the provided context.\n\n"
        f"QUESTION: {query}\n"
        f"YOUR ANSWER: {answer_1}\n"
        f"CONTEXT USED: {json.dumps([c['text'] for c in chunks_1])}\n\n"
        f"Reply in ONE LINE with a follow-up search query that would help you "
        f"verify or refine the answer. If the answer is solid, reply: NONE"
    ).strip()

    chunks_2 = []
    if reflection and reflection.upper() != "NONE":
        chunks_2 = retrieve(reflection, top_k=2)

    if chunks_2:
        # Second pass: refine using both contexts
        context = "\n".join(f"- {c['text']}" for c in chunks_1 + chunks_2)
        answer_2 = ask_llm(
            f"Refine the earlier answer using the additional context.\n\n"
            f"QUESTION: {query}\n"
            f"EARLIER ANSWER: {answer_1}\n"
            f"ADDITIONAL CONTEXT:\n{context}\n\n"
            f"FINAL ANSWER:"
        )
    else:
        answer_2 = answer_1

    return {
        "chunks_pass1": chunks_1,
        "answer_pass1": answer_1,
        "reflection_query": reflection,
        "chunks_pass2": chunks_2,
        "answer_pass2": answer_2,
    }


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# ---------- Demo ----------


def show_chunks(label, chunks):
    if not chunks:
        print(f"  {label}: (none)")
        return
    print(f"  {label}:")
    for c in chunks:
        print(f"    [{c['id']}] {c['text']}")


if __name__ == "__main__":
    print(f"Model: {MODEL}\n")
    print(f"Knowledge base: {len(DOCS)} docs, {len(CHUNKS)} chunks.\n")

    # Test queries: 3 in-corpus, 1 out-of-corpus
    queries = [
        "How do I pick a model when running opencode?",  # in corpus
        "Is opencode free to use? Do I need to pay?",  # partial
        "What subcommands does opencode have for MCP?",  # in corpus
        "What's the capital of France?",  # out of corpus
    ]

    for q in queries:
        banner(f"QUERY: {q}")
        chunks = retrieve(q, top_k=3)
        show_chunks("Top retrieved chunks", chunks)
        answer = generate(q, chunks)
        print(f"\n  ANSWER:\n    {answer}")

    banner("BONUS — AGENTIC RAG (retrieve -> reflect -> re-retrieve -> refine)")
    q = "What languages is opencode written in, and is it free?"
    print(f"QUERY: {q}\n")
    result = agentic_rag(q)
    show_chunks("Pass 1 chunks", result["chunks_pass1"])
    print(f"\n  Pass 1 answer: {result['answer_pass1']}")
    print(f"\n  Reflection query: {result['reflection_query']}")
    show_chunks("Pass 2 chunks (new)", result["chunks_pass2"])
    print(f"\n  Pass 2 (refined) answer: {result['answer_pass2']}")
