"""
Part 5 — Implementing Agentic RAG: Mini RAG pipeline from scratch

Builds a minimal RAG system with explicit chunking, keyword retrieval,
and LLM generation — no external DB or embeddings. Includes a bonus
re-retrieval pass where the agent evaluates confidence and re-queries
if needed.

Run:  python mini_rag_pipeline.py
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------- UTF-8 fix for Windows ----------

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- Configuration ----------

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/mimo-v2.5")
CHUNK_SIZE = 2  # sentences per chunk
CHUNK_OVERLAP = 1  # overlapping sentences between chunks
TOP_K = 3  # chunks to retrieve
CONFIDENCE_THRESHOLD = 0.25
MAX_RETRIEVAL_PASSES = 2

# ---------- Document store ----------

DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "doc-001",
        "title": "Python Decorators",
        "content": (
            "A decorator in Python is a function that takes another function and extends "
            "its behavior without explicitly modifying it. Decorators are denoted with "
            "the @ symbol before the function definition. They are commonly used for "
            "logging, authentication, caching, and timing. Decorators leverage the fact "
            "that functions are first-class objects in Python."
        ),
    },
    {
        "id": "doc-002",
        "title": "List Comprehensions",
        "content": (
            "List comprehensions provide a concise way to create lists in Python. "
            "The syntax is [expression for item in iterable if condition]. They are "
            "generally faster than equivalent for loops because the iteration is "
            "performed in C. List comprehensions can be nested for multi-dimensional "
            "lists but should be kept simple for readability."
        ),
    },
    {
        "id": "doc-003",
        "title": "Python Data Types",
        "content": (
            "Python has several built-in data types. Numeric types include int, float, "
            "and complex. Sequence types include str, list, tuple, and range. Mapping "
            "type is dict. Set types are set and frozenset. Boolean type is bool. "
            "Binary types include bytes, bytearray, and memoryview. NoneType represents "
            "the absence of a value."
        ),
    },
    {
        "id": "doc-004",
        "title": "Virtual Environments",
        "content": (
            "Virtual environments allow you to create isolated Python environments for "
            "different projects. The venv module is the standard way to create virtual "
            "environments in Python 3.3+. Use python -m venv myenv to create one. "
            "Activate it with source myenv/bin/activate on Unix or "
            "myenv\\Scripts\\activate on Windows."
        ),
    },
    {
        "id": "doc-005",
        "title": "Generators and Iterators",
        "content": (
            "Generators are functions that yield values one at a time instead of "
            "returning a complete list. They use the yield keyword and are memory "
            "efficient for large datasets. Generators implement the iterator protocol "
            "with __iter__ and __next__ methods. The range function and generator "
            "expressions are common examples of generators in Python."
        ),
    },
    {
        "id": "doc-006",
        "title": "Exception Handling",
        "content": (
            "Python uses try, except, else, and finally blocks for exception handling. "
            "The try block contains code that might raise an exception. The except block "
            "handles specific exceptions. The else block runs if no exception occurs. "
            "The finally block always executes for cleanup. Always catch specific "
            "exceptions rather than using bare except clauses."
        ),
    },
    {
        "id": "doc-007",
        "title": "Lambda Functions",
        "content": (
            "Lambda functions are anonymous functions defined with the lambda keyword. "
            "They can take any number of arguments but must contain a single expression. "
            "Lambda functions are commonly used with map, filter, and sorted. They are "
            "limited to single expressions and cannot contain statements. For complex "
            "logic, use regular def functions instead."
        ),
    },
    {
        "id": "doc-008",
        "title": "String Formatting",
        "content": (
            "Python offers three main string formatting methods: %-formatting, str.format(), "
            "and f-strings. F-strings (formatted string literals) are the most modern and "
            "readable, available since Python 3.6. They embed expressions directly in "
            "strings using curly braces: f'Hello {name}'. F-strings are faster than "
            "both alternatives and support debugging with the = syntax."
        ),
    },
]

# ---------- Test questions ----------

TESTS: list[dict[str, Any]] = [
    {
        "question": "What is a decorator in Python?",
        "expected_keywords": ["decorator", "function", "@", "first-class"],
        "note": "Answer exists in doc-001",
    },
    {
        "question": "How do list comprehensions work?",
        "expected_keywords": ["list", "comprehension", "expression", "iterable"],
        "note": "Answer exists in doc-002",
    },
    {
        "question": "What are Python's data types?",
        "expected_keywords": ["int", "float", "str", "list", "dict"],
        "note": "Answer exists in doc-003",
    },
    {
        "question": "How do you implement a red-black tree?",
        "expected_keywords": [],
        "note": "NOT in docs — agent should say it doesn't know",
    },
]

# ---------- LLM via opencode CLI ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode CLI and return the response text."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Step 1: Chunker ----------


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Split text into overlapping sentence windows."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(sentences):
        end = min(start + chunk_size, len(sentences))
        chunk = ". ".join(sentences[start:end])
        if not chunk.endswith("."):
            chunk += "."
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_index(documents: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Chunk all documents and build a retrieval index."""
    index: list[dict[str, Any]] = []
    for doc in documents:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            words = set(chunk.lower().split())
            index.append(
                {
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "chunk_index": i,
                    "text": chunk,
                    "words": words,
                }
            )
    return index


# ---------- Step 2: Retriever ----------


def retrieve(
    index: list[dict[str, Any]], query: str, top_k: int = TOP_K
) -> list[dict[str, Any]]:
    """Retrieve top-k chunks by keyword overlap score."""
    query_words = set(query.lower().split())
    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in index:
        overlap = len(query_words & entry["words"])
        score = overlap / len(query_words) if query_words else 0.0
        scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


# ---------- Step 3: Generator ----------


def generate(query: str, chunks: list[dict[str, Any]]) -> str:
    """Generate an answer from retrieved chunks using the LLM."""
    if not chunks or all(c["text"].strip() == "" for c in chunks):
        return "I don't have enough information to answer that question."

    context = "\n\n".join(
        f"[{c['title']} / chunk {c['chunk_index']}]\n{c['text']}" for c in chunks
    )
    prompt = (
        "You are a helpful Python assistant. Answer using ONLY the context below.\n"
        "If the context does not contain enough information, say so.\n\n"
        f"--- Context ---\n{context}\n--- End Context ---\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    return ask_llm(prompt)


# ---------- Step 4: Confidence evaluator ----------


def compute_confidence(chunks: list[dict[str, Any]], query: str) -> float:
    """Estimate confidence based on retrieval scores."""
    if not chunks:
        return 0.0
    query_words = set(query.lower().split())
    scores = [
        len(query_words & c["words"]) / len(query_words) for c in chunks if query_words
    ]
    return max(scores) if scores else 0.0


# ---------- Bonus: Re-retrieval pass ----------


def run_pipeline(query: str) -> dict[str, Any]:
    """Run the full RAG pipeline with optional re-retrieval."""
    index = build_index(DOCUMENTS)
    log: list[str] = []

    # Pass 1
    chunks = retrieve(index, query)
    confidence = compute_confidence(chunks, query)
    answer = generate(query, chunks)
    passes = 1

    log.append(f"Pass 1: retrieved {len(chunks)} chunks, confidence={confidence:.2f}")

    # Re-retrieve if low confidence
    if confidence < CONFIDENCE_THRESHOLD and passes < MAX_RETRIEVAL_PASSES:
        reformulated = f"{query} explanation tutorial guide"
        chunks2 = retrieve(index, reformulated)
        confidence2 = compute_confidence(chunks2, reformulated)
        log.append(
            f"Pass 2 (reformulated): query='{reformulated}', "
            f"retrieved {len(chunks2)} chunks, confidence={confidence2:.2f}"
        )
        if confidence2 > confidence:
            chunks = chunks2
            confidence = confidence2
            answer = generate(query, chunks)
        passes += 1

    # Return results
    return {
        "query": query,
        "chunks": chunks,
        "answer": answer,
        "confidence": confidence,
        "passes": passes,
        "log": log,
    }


def check_answer(answer: str, expected_keywords: list[str]) -> tuple[bool, float]:
    """Check if answer contains expected keywords."""
    if not expected_keywords:
        # For "not in docs" questions, check that agent says it doesn't know
        refused = any(
            phrase in answer.lower()
            for phrase in [
                "don't have",
                "not enough",
                "don't know",
                "not available",
                "no information",
                "doesn't contain",
            ]
        )
        return refused, 1.0 if refused else 0.0
    lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in lower)
    ratio = hits / len(expected_keywords)
    return ratio >= 0.3, ratio


# ---------- Display ----------


def banner(title: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------- Markdown output ----------

RESULTS_PATH = Path(__file__).parent / "results.md"


def write_results(
    results: list[dict[str, Any]], evaluations: list[dict[str, Any]]
) -> None:
    """Write pipeline results to a markdown file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    correct = sum(1 for e in evaluations if e["correct"])

    lines: list[str] = [
        "# Part 5 — Mini RAG Pipeline Results",
        "",
        f"- **Model:** `{MODEL}`",
        f"- **Generated:** {now}",
        f"- **Chunk size:** {CHUNK_SIZE} sentences, overlap={CHUNK_OVERLAP}",
        f"- **Top-k:** {TOP_K}",
        f"- **Confidence threshold:** {CONFIDENCE_THRESHOLD}",
        "",
        "## Pipeline Architecture",
        "",
        "```",
        "Documents → Chunker → Index → Retriever → Generator → Answer",
        "                                    ↑",
        "                              Re-retrieval (if low confidence)",
        "```",
        "",
    ]

    for i, (r, e) in enumerate(zip(results, evaluations), 1):
        lines.append(f"## Query {i}: {r['query']}")
        lines.append("")
        lines.append(f"- **Passes:** {r['passes']}")
        lines.append(f"- **Confidence:** {r['confidence']:.2f}")
        lines.append(
            f"- **Correct:** {'Yes' if e['correct'] else 'No'} ({e['ratio']:.0%})"
        )
        lines.append("")
        lines.append("### Retrieval log")
        lines.append("")
        for entry in r["log"]:
            lines.append(f"- {entry}")
        lines.append("")
        lines.append("### Retrieved chunks")
        lines.append("")
        for c in r["chunks"]:
            lines.append(
                f"- **{c['title']}** (chunk {c['chunk_index']}): {c['text'][:100]}..."
            )
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append(f"> {r['answer']}")
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Correct:** {correct}/{len(evaluations)}")
    lines.append("")

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_PATH}")


# ---------- Main ----------


def main() -> None:
    """Run the RAG pipeline on all test questions."""
    banner("Part 5 — Implementing Agentic RAG")
    print(f"Model: {MODEL}  (override: set OPENCODE_MODEL=...)")
    print(f"Chunk size: {CHUNK_SIZE} sentences, overlap: {CHUNK_OVERLAP}")
    print(f"Top-k: {TOP_K}, Confidence threshold: {CONFIDENCE_THRESHOLD}\n")

    # Build index and show stats
    index = build_index(DOCUMENTS)
    print(f"Index: {len(DOCUMENTS)} documents → {len(index)} chunks\n")

    all_results: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []

    for i, test in enumerate(TESTS, 1):
        banner(f"Query {i}: {test['question']}")
        print(f"  Note: {test['note']}\n")

        result = run_pipeline(test["question"])

        # Show retrieval log
        for entry in result["log"]:
            print(f"  {entry}")
        print()

        # Show chunks
        print("  Retrieved chunks:")
        for c in result["chunks"]:
            print(f"    [{c['title']}] {c['text'][:80]}...")
        print()

        # Evaluate
        correct, ratio = check_answer(result["answer"], test["expected_keywords"])
        evaluations.append(
            {
                "query": test["question"],
                "correct": correct,
                "ratio": ratio,
            }
        )

        print(f"  Answer: {result['answer'][:150]}...")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Correct: {'Yes' if correct else 'No'} ({ratio:.0%})")

        all_results.append(result)

    # Summary
    banner("Summary")
    total_correct = sum(1 for e in evaluations if e["correct"])
    print(f"  Correct: {total_correct}/{len(evaluations)}")
    for i, e in enumerate(evaluations, 1):
        status = "OK" if e["correct"] else "FAIL"
        print(f"    {i}. [{status}] {e['query'][:50]}")

    write_results(all_results, evaluations)
    banner("DONE — Part 5 complete. Next: Part 6 — Challenges and Future Directions?")


if __name__ == "__main__":
    main()
