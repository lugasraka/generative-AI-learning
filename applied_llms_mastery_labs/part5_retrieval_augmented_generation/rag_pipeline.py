"""
Part 5 — Retrieval-Augmented Generation: RAG Pipeline

Builds a RAG pipeline from scratch: chunk documents, retrieve with BM25-style
scoring, generate answers with an LLM. Includes agentic RAG with follow-up
search queries.

Run:  python rag_pipeline.py
"""

import datetime
import math
import os
import re
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/mimo-v2.5")

# ---------- Knowledge base (Machine Learning) ----------

DOCS = [
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data and improve their performance without being explicitly programmed. It focuses on developing algorithms that can access data, learn from it, and make predictions.",
    "Supervised learning uses labeled training data to learn a mapping from inputs to outputs. Common tasks include classification (discrete labels) and regression (continuous values). Examples include spam detection, image recognition, and price prediction.",
    "Unsupervised learning finds hidden patterns in unlabeled data. Clustering groups similar data points together, while dimensionality reduction compresses features. K-means and PCA are popular unsupervised methods.",
    "Reinforcement learning trains an agent to make sequences of decisions by interacting with an environment. The agent receives rewards or penalties and learns a policy that maximizes cumulative reward. AlphaGo and robotic control use reinforcement learning.",
    "Linear regression models the relationship between a dependent variable and one or more independent variables by fitting a linear equation. It assumes a linear relationship and minimizes the sum of squared errors. It is simple, interpretable, and fast.",
    "Decision trees split data into branches using feature thresholds. They are easy to visualize and interpret but prone to overfitting. Random forests combine many decision trees to reduce overfitting and improve accuracy through bagging.",
    "Support vector machines find the optimal hyperplane that separates classes with the maximum margin. They work well in high-dimensional spaces and can use kernel tricks for non-linear boundaries. SVMs are effective for text classification and image recognition.",
    "K-nearest neighbors classifies a data point based on the majority class of its k nearest neighbors. It is a lazy learner that stores all training data and computes distances at prediction time. It works well for small datasets but is slow on large ones.",
    "Neural networks are composed of layers of interconnected nodes inspired by biological neurons. Each node applies a weighted sum and a non-linear activation function. Deep neural networks with many layers can learn complex patterns.",
    "Backpropagation is the algorithm used to train neural networks by computing gradients of the loss with respect to each weight. It uses the chain rule of calculus and gradient descent to update weights iteratively. It enabled the training of deep networks.",
    "Convolutional neural networks are specialized for grid-like data such as images. They use convolutional layers that apply filters to detect local patterns like edges and textures. CNNs achieved breakthrough performance in image classification.",
    "Recurrent neural networks process sequential data by maintaining hidden states across time steps. They are used for text, speech, and time series. LSTMs and GRUs address the vanishing gradient problem in basic RNNs.",
    "The Transformer architecture uses self-attention mechanisms to process all positions in a sequence simultaneously. It replaced RNNs for most NLP tasks and enabled models like BERT, GPT, and T5. Transformers are the foundation of modern LLMs.",
    "Overfitting occurs when a model learns noise in training data instead of the underlying pattern. It performs well on training data but poorly on unseen data. Regularization techniques like dropout, L2 penalty, and early stopping help prevent overfitting.",
    "Cross-validation splits data into k folds, trains on k-1 folds, and tests on the remaining fold. This process repeats k times to get a robust estimate of model performance. It helps detect overfitting and tune hyperparameters.",
    "Scikit-learn is the most popular Python library for traditional machine learning. It provides consistent APIs for classification, regression, clustering, and preprocessing. It includes implementations of SVMs, random forests, k-means, and many other algorithms.",
    "TensorFlow and PyTorch are the leading deep learning frameworks. TensorFlow, developed by Google, emphasizes production deployment. PyTorch, developed by Meta, is favored for research due to its dynamic computation graph and Pythonic interface.",
    "Transfer learning reuses a pre-trained model on a new task. Instead of training from scratch, you fine-tune the last layers on your specific data. This dramatically reduces training time and data requirements. BERT and GPT are commonly fine-tuned this way.",
    "Ensemble methods combine multiple models to improve performance. Bagging trains models on random subsets and averages their predictions. Boosting trains models sequentially, each correcting the previous model's errors. XGBoost and AdaBoost are popular boosting algorithms.",
    "Feature engineering transforms raw data into informative features that improve model performance. Techniques include scaling, encoding categorical variables, creating polynomial features, and extracting text features. Good features often matter more than model choice.",
]

STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "can",
    "shall",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "they",
    "them",
    "their",
    "we",
    "our",
    "you",
    "your",
    "he",
    "she",
    "not",
    "no",
    "if",
    "as",
    "so",
    "than",
    "too",
    "very",
    "also",
    "just",
    "about",
    "more",
    "most",
    "other",
    "some",
    "such",
    "only",
    "then",
    "here",
    "when",
    "where",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "many",
    "much",
    "own",
    "same",
    "into",
    "over",
    "after",
    "before",
    "between",
    "under",
    "up",
    "down",
    "out",
    "off",
    "again",
    "further",
    "once",
}

# ---------- Chunker ----------


def tokenize(text: str) -> list[str]:
    """Lowercase and split text into word tokens."""
    return re.findall(r"[a-z]+", text.lower())


def chunk(docs: list[str], window: int = 2) -> list[dict]:
    """Split documents into overlapping sentence windows."""
    chunks = []
    chunk_id = 0
    for doc_idx, doc in enumerate(docs):
        sentences = re.split(r"(?<=[.!?])\s+", doc.strip())
        for sent_idx in range(len(sentences)):
            start = max(0, sent_idx - window + 1)
            end = sent_idx + 1
            chunk_text = " ".join(sentences[start:end])
            keywords = set(tokenize(chunk_text)) - STOPWORDS
            chunks.append(
                {
                    "id": f"d{doc_idx}s{sent_idx}",
                    "text": chunk_text,
                    "doc_index": doc_idx,
                    "keywords": keywords,
                }
            )
            chunk_id += 1
    return chunks


# ---------- Retriever ----------


def retrieve(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    """BM25-style keyword retrieval."""
    k1 = 1.5
    query_tokens = set(tokenize(query)) - STOPWORDS
    scored = []
    for c in chunks:
        tf_map: dict[str, int] = {}
        for word in tokenize(c["text"]):
            if word in query_tokens:
                tf_map[word] = tf_map.get(word, 0) + 1
        score = sum(1.0 / (k1 + tf) for tf in tf_map.values())
        if score > 0:
            scored.append({**c, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ---------- Generator ----------

RAG_PROMPT_TEMPLATE = (
    "Answer using ONLY the context below. If the answer is not in the context, "
    'say "I don\'t have enough information."\n\n'
    "CONTEXT:\n{context}\n\n"
    "QUESTION: {question}\n\n"
    "ANSWER:"
)


def generate(query: str, chunks: list[dict]) -> str:
    """Generate an answer using retrieved chunks via opencode CLI."""
    context = "\n\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=query)
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Agentic RAG ----------

FOLLOWUP_PROMPT = (
    "Given this question and answer, what follow-up search query would help "
    "verify or refine the answer? If no follow-up is needed, reply exactly "
    'with "NONE". Otherwise, reply with just the search query.\n\n'
    "QUESTION: {question}\n"
    "ANSWER: {answer}\n\n"
    "Follow-up query:"
)


def agentic_rag(
    query: str, chunks: list[dict], first_answer: str
) -> tuple[str, list[dict], str]:
    """Ask the LLM for a follow-up query, retrieve again, and refine."""
    followup_prompt = FOLLOWUP_PROMPT.format(question=query, answer=first_answer)
    followup_query = subprocess.run(
        ["opencode", "run", "-m", MODEL, followup_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if followup_query.returncode != 0:
        return first_answer, chunks, "NONE"

    followup_text = followup_query.stdout.strip().strip('"').strip("'")

    if followup_text.upper() == "NONE" or len(followup_text) < 5:
        return first_answer, chunks, "NONE"

    # Second retrieval pass
    followup_chunks = retrieve(followup_text, chunks, top_k=3)
    all_chunks = chunks + followup_chunks

    # Deduplicate by ID
    seen = set()
    unique_chunks = []
    for c in all_chunks:
        if c["id"] not in seen:
            seen.add(c["id"])
            unique_chunks.append(c)

    # Generate refined answer
    context = "\n\n".join(f"[{c['id']}] {c['text']}" for c in unique_chunks)
    refined_prompt = (
        "Answer using ONLY the context below. If the answer is not in the context, "
        'say "I don\'t have enough information."\n\n'
        f"CONTEXT:\n{context}\n\n"
        f"ORIGINAL QUESTION: {query}\n"
        f"FOLLOW-UP SEARCH: {followup_text}\n\n"
        "REFINED ANSWER:"
    )
    refined = subprocess.run(
        ["opencode", "run", "-m", MODEL, refined_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if refined.returncode != 0:
        return first_answer, chunks, followup_text

    return refined.stdout.strip(), unique_chunks, followup_text


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_retrieval(query: str, results: list[dict]) -> None:
    """Print retrieval results for a query."""
    print(f'\n  Query: "{query}"')
    print(f"  Top {len(results)} chunks:")
    for i, r in enumerate(results, 1):
        preview = r["text"][:90].replace("\n", " ")
        print(f"    {i}. [{r['id']}] (score={r['score']:.3f}) {preview}...")


# ---------- Save results ----------


def save_results(
    queries_results: list[dict],
    index_stats: dict,
    agentic_results: list[dict],
) -> str:
    """Write results to part5_results.md."""
    lines: list[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("# Part 5 — RAG Pipeline Results\n")
    lines.append(f"> **Model:** `{MODEL}`  ")
    lines.append(f"> **Date:** {now}\n")

    # Index stats
    lines.append("## Index Stats\n")
    lines.append(f"- Documents: {index_stats['num_docs']}")
    lines.append(f"- Total chunks: {index_stats['num_chunks']}")
    lines.append(f"- Chunking: overlapping sentence windows (window=2)")
    lines.append(f"- Retrieval: BM25-style keyword scoring (k1=1.5)")
    lines.append("")

    # Query results
    lines.append("## Query Results\n")
    for qr in queries_results:
        lines.append(f'### Query: "{qr["query"]}"\n')
        lines.append("**Retrieved chunks:**\n")
        for i, c in enumerate(qr["chunks"], 1):
            lines.append(
                f"{i}. `[{c['id']}]` (score={c['score']:.3f}) — {c['text'][:120]}..."
            )
        lines.append(f"\n**Answer:** {qr['answer']}\n")

    # Agentic RAG
    if agentic_results:
        lines.append("## Agentic RAG (Follow-up Search)\n")
        for ar in agentic_results:
            lines.append(f'### Query: "{ar["query"]}"\n')
            lines.append(f"- **First answer:** {ar['first_answer'][:200]}...")
            if ar["followup_query"] != "NONE":
                lines.append(f"- **Follow-up query:** {ar['followup_query']}")
                lines.append(f"- **Refined answer:** {ar['refined_answer'][:200]}...")
                lines.append(f"- **Additional chunks used:** {len(ar['all_chunks'])}")
            else:
                lines.append("- **Follow-up:** NONE (no refinement needed)")
            lines.append("")

    content = "\n".join(lines)
    path = os.path.join(os.path.dirname(__file__), "part5_results.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------- Test queries ----------

TEST_QUERIES = [
    {
        "query": "What year was machine learning invented?",
        "expected": "in docs",
        "description": "Clearly in docs",
    },
    {
        "query": "How do convolutional neural networks work?",
        "expected": "in docs",
        "description": "Clearly in docs",
    },
    {
        "query": "How does random forest compare to gradient boosting?",
        "expected": "partially covered",
        "description": "Partially covered",
    },
    {
        "query": "What is the capital of France?",
        "expected": "out of scope",
        "description": "Out of scope",
    },
]


# ---------- Main ----------


def main() -> None:
    print(f"Model: {MODEL}")
    banner("RAG PIPELINE FROM SCRATCH")
    print(f"\n  Knowledge base: {len(DOCS)} documents about Machine Learning")

    # Build index
    print("\n  Building index...")
    all_chunks = chunk(DOCS, window=2)
    print(f"  Indexed: {len(DOCS)} docs → {len(all_chunks)} chunks")

    index_stats = {"num_docs": len(DOCS), "num_chunks": len(all_chunks)}

    # Test queries
    banner("TESTING 4 QUERIES")
    queries_results = []
    agentic_results = []

    for i, q in enumerate(TEST_QUERIES, 1):
        pct = i / len(TEST_QUERIES) * 100
        bar_filled = round(pct / 5)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(f"\n  [{i}/{len(TEST_QUERIES)}] {bar} {pct:.0f}%  {q['description']}")

        # Retrieve
        results = retrieve(q["query"], all_chunks, top_k=3)
        print_retrieval(q["query"], results)

        # Generate
        print("\n  Generating answer...")
        answer = generate(q["query"], results)
        print(f"  Answer: {answer}")

        queries_results.append(
            {
                "query": q["query"],
                "chunks": results,
                "answer": answer,
            }
        )

    # Agentic RAG on first 2 queries
    banner("AGENTIC RAG (Follow-up Search)")
    print("  Running agentic RAG on queries 1-2...\n")

    for i, qr in enumerate(queries_results[:2], 1):
        print(f'  [{i}/2] Query: "{qr["query"][:50]}..."')
        refined_answer, all_chunks_used, followup_q = agentic_rag(
            qr["query"], qr["chunks"], qr["answer"]
        )
        print(f"    Follow-up query: {followup_q}")
        if followup_q != "NONE":
            print(f"    Refined answer: {refined_answer[:120]}...")
        else:
            print("    No refinement needed")
        print()

        agentic_results.append(
            {
                "query": qr["query"],
                "first_answer": qr["answer"],
                "followup_query": followup_q,
                "refined_answer": refined_answer,
                "all_chunks": all_chunks_used,
            }
        )

    # Save results
    results_path = save_results(queries_results, index_stats, agentic_results)
    print(f"\n  Results saved to: {results_path}")

    banner("DONE — Part 5 complete. Next: Part 6 (Tools for LLM Apps)")


if __name__ == "__main__":
    main()
