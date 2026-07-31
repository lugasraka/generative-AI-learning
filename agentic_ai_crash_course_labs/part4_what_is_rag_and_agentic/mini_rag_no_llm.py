"""
Part 4 — RAG from scratch (no LLM): chunk -> index (keyword) -> retrieve -> template.

Topic: FIFA World Cup / international football. Methods: sentence chunking,
keyword overlap, hand-rolled answer template (no LLM call).

Run:  python mini_rag_no_llm.py
"""

import re
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

# ---------- 1. Knowledge base ----------

DOCS = [
    "The FIFA World Cup is the most prestigious international football tournament, held every four years.",
    "The 2022 FIFA World Cup was held in Qatar, and was won by Argentina, led by Lionel Messi.",
    "Argentina defeated France in the 2022 final on penalties after a 3-3 draw, one of the most dramatic finals in history.",
    "Kylian Mbappe scored a hat-trick for France in the 2022 final, only the second player to do so in a World Cup final after Geoff Hurst in 1966.",
    "Brazil has won the most World Cups with five titles (1958, 1962, 1970, 1994, 2002).",
    "Germany and Italy are tied with four World Cup titles each.",
    "The next FIFA World Cup will be held in 2026 across the United States, Canada, and Mexico.",
    "The 2026 World Cup will be the first to feature 48 teams, expanded from the traditional 32.",
    "The World Cup trophy is made of 18-carat gold and weighs about 6.1 kilograms.",
    "The Golden Ball is awarded to the best player of the tournament; Lionel Messi won it in 2022, and Diego Maradona won it in 1986.",
    "Miroslav Klose of Germany holds the record for most World Cup goals with 16, scored across four tournaments.",
    "The first FIFA World Cup was held in 1930 in Uruguay, who also won the inaugural tournament.",
]

# ---------- 2. Chunker (sentence-level) ----------


def chunk(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


CHUNKS: list[dict] = []
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


def retrieve(query: str, top_k: int = 3, min_overlap: int = 2) -> list[dict]:
    """Score chunks by keyword overlap; return top_k.

    min_overlap: minimum shared tokens to consider a chunk relevant.
    A query like 'capital of France' (only 1 meaningful token) won't match
    chunks just because the country name happens to appear in them.
    """
    q_tokens = tokenize(query)
    if not q_tokens:
        return []
    scored = []
    for ch in CHUNKS:
        overlap = len(q_tokens & ch["tokens"])
        if overlap >= min_overlap:
            scored.append((overlap, ch))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [ch for _, ch in scored[:top_k]]


# ---------- 4. Generator (pure template, no LLM) ----------


def generate(query: str, chunks: list[dict]) -> str:
    """Build an answer by quoting top chunk + listing others. No LLM."""
    if not chunks:
        return (
            "I could not find anything in the knowledge base that matches this "
            "question. The knowledge base only covers the FIFA World Cup "
            "(tournaments, winners, records, the trophy). Try rephrasing or "
            "asking about the World Cup."
        )

    top, *rest = chunks
    lines = [f"Top match: {top['text']}"]
    if rest:
        extras = "; ".join(c["text"] for c in rest)
        lines.append(f"Also relevant: {extras}")
    lines.append(f"(Source: {top['id']}, based on keyword overlap.)")
    return "\n".join(lines)


# ---------- 5. Agentic RAG (bonus): retrieve -> reflect -> re-retrieve -> refine ----------


def agentic_rag(query: str) -> dict:
    """Two-pass RAG: first answer, then a 'reflection' that may add more chunks."""
    chunks_1 = retrieve(query, top_k=2)
    answer_1 = generate(query, chunks_1)

    # Simple reflection rule (no LLM): if the top chunk shares fewer than 2
    # tokens with the query, ask a follow-up using the top chunk's text.
    top = chunks_1[0] if chunks_1 else None
    if top and len(tokenize(query) & top["tokens"]) < 2:
        reflection_query = top["text"]
    else:
        reflection_query = ""

    chunks_2 = []
    if reflection_query:
        chunks_2 = retrieve(reflection_query, top_k=2)
        # Drop duplicates already in pass 1
        seen = {c["id"] for c in chunks_1}
        chunks_2 = [c for c in chunks_2 if c["id"] not in seen]

    if chunks_2:
        extras = " ".join(c["text"] for c in chunks_2)
        answer_2 = answer_1 + "\n\nRefined with: " + extras
    else:
        answer_2 = answer_1

    return {
        "chunks_pass1": chunks_1,
        "answer_pass1": answer_1,
        "reflection_query": reflection_query,
        "chunks_pass2": chunks_2,
        "answer_pass2": answer_2,
    }


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def show_chunks(label, chunks):
    if not chunks:
        print(f"  {label}: (none)")
        return
    print(f"  {label}:")
    for c in chunks:
        print(f"    [{c['id']}] {c['text']}")


if __name__ == "__main__":
    print("No LLM — pure template generator.\n")
    print(f"Knowledge base: {len(DOCS)} docs, {len(CHUNKS)} chunks.\n")

    queries = [
        "Who won the 2022 World Cup?",
        "Which country has the most World Cup titles?",
        "When and where is the next World Cup?",
        "Who scored the most World Cup goals of all time?",
        "What's the capital of France?",  # out of corpus (single-token false match)
        "Tell me about the moon landing",  # out of corpus (truly off-topic)
    ]

    for q in queries:
        banner(f"QUERY: {q}")
        chunks = retrieve(q, top_k=3)
        show_chunks("Top retrieved chunks", chunks)
        answer = generate(q, chunks)
        print(f"\n  ANSWER:\n    " + answer.replace("\n", "\n    "))

    banner("BONUS — AGENTIC RAG (retrieve -> reflect -> re-retrieve -> refine)")
    q = "What country has won the most World Cups, and who is their all-time top scorer in the tournament?"
    print(f"QUERY: {q}\n")
    result = agentic_rag(q)
    show_chunks("Pass 1 chunks", result["chunks_pass1"])
    print(f"\n  Pass 1 answer:\n    " + result["answer_pass1"].replace("\n", "\n    "))
    print(f"\n  Reflection query: {result['reflection_query'] or '(none)'}")
    show_chunks("Pass 2 chunks (new)", result["chunks_pass2"])
    print(
        f"\n  Pass 2 (refined) answer:\n    "
        + result["answer_pass2"].replace("\n", "\n    ")
    )
