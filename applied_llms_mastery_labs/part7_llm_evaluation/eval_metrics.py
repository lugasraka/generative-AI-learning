"""
Part 7 — LLM Evaluation: Metrics Calculator and Judge Comparison

Evaluates generated answers against reference answers and source context with
small, dependency-free metrics. It can also compare those metrics with scores
from an optional LLM judge invoked through the opencode CLI.

Run:  python eval_metrics.py
      python eval_metrics.py --skip-llm
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")

Sample = tuple[str, str, str, str]

SAMPLE_LABELS = [
    "correct",
    "correct",
    "correct",
    "partial",
    "partial",
    "partial",
    "incorrect",
    "incorrect",
    "refusal",
    "refusal",
]

TEST_SAMPLES: list[Sample] = [
    (
        "What is the capital of France?",
        "France is a country in Western Europe. Its capital city is Paris, which "
        "is known for the Eiffel Tower.",
        "The capital of France is Paris.",
        "Paris is the capital of France.",
    ),
    (
        "Who created the Python programming language?",
        "Python was created by Guido van Rossum and first released in 1991. "
        "It is known for readable syntax.",
        "Guido van Rossum created Python.",
        "Guido van Rossum created Python, which was first released in 1991.",
    ),
    (
        "What does photosynthesis produce?",
        "Photosynthesis is the process in which plants use sunlight, water, and "
        "carbon dioxide to make glucose and release oxygen.",
        "Photosynthesis makes glucose and releases oxygen.",
        "Photosynthesis uses sunlight, water, and carbon dioxide to make glucose "
        "and release oxygen.",
    ),
    (
        "What is the atmosphere of Mars mostly made of?",
        "Mars has a very thin atmosphere made mostly of carbon dioxide. It also "
        "contains small amounts of nitrogen and argon.",
        "Mars's atmosphere is mostly carbon dioxide, with small amounts of "
        "nitrogen and argon.",
        "Mars has a thin atmosphere made mostly of carbon dioxide and nitrogen. "
        "Its sky is bright blue like Earth's.",
    ),
    (
        "What does HTTP status code 404 mean?",
        "An HTTP 404 status code means that the requested resource could not be "
        "found on the server.",
        "HTTP 404 means the requested resource was not found.",
        "HTTP 404 means the requested resource was not found, usually because "
        "the URL is wrong.",
    ),
    (
        "What was Ada Lovelace known for?",
        "Ada Lovelace wrote notes describing an algorithm for Charles Babbage's "
        "Analytical Engine. She is often considered the first computer programmer.",
        "Ada Lovelace is often considered the first computer programmer.",
        "Ada Lovelace wrote an algorithm for Babbage's Analytical Engine and is "
        "often called the first computer programmer. She built the machine herself.",
    ),
    (
        "Which mountain is the highest above sea level?",
        "Mount Everest is the highest mountain above sea level, at about 8,849 "
        "meters. K2 is the second-highest mountain.",
        "Mount Everest is the highest mountain above sea level.",
        "K2 is the highest mountain above sea level.",
    ),
    (
        "What does HTTP status code 404 mean?",
        "An HTTP 404 status code means that the requested resource could not be "
        "found on the server.",
        "It means the requested resource was not found.",
        "HTTP 404 means the server had an internal error while processing the request.",
    ),
    (
        "Which planet is known as the Red Planet?",
        "Mars is known as the Red Planet because iron minerals in its soil give "
        "the surface a reddish appearance.",
        "Mars is known as the Red Planet.",
        "I don't know.",
    ),
    (
        "What is the largest ocean on Earth?",
        "The Pacific Ocean is the largest and deepest ocean on Earth. It covers "
        "more area than the Atlantic, Indian, Southern, and Arctic oceans.",
        "The Pacific Ocean is the largest ocean on Earth.",
        "I don't know the answer to that question.",
    ),
]


def normalized_text(text: str) -> str:
    """Lowercase text and keep only word-like tokens."""
    return " ".join(re.findall(r"\w+", text.lower()))


def tokens(text: str) -> list[str]:
    """Return normalized whitespace-style tokens for metric calculations."""
    return normalized_text(text).split()


def exact_match(pred: str, ref: str) -> float:
    """Return 1.0 when prediction and reference match after normalization."""
    return float(normalized_text(pred) == normalized_text(ref))


def token_overlap_f1(pred: str, ref: str) -> float:
    """Calculate token-level precision, recall, and F1 using token counts."""
    pred_tokens = tokens(pred)
    ref_tokens = tokens(ref)
    if not pred_tokens or not ref_tokens:
        return float(not pred_tokens and not ref_tokens)

    pred_counts = {token: pred_tokens.count(token) for token in set(pred_tokens)}
    ref_counts = {token: ref_tokens.count(token) for token in set(ref_tokens)}
    overlap = sum(
        min(count, ref_counts.get(token, 0)) for token, count in pred_counts.items()
    )
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _lcs_length(left: list[str], right: list[str]) -> int:
    """Return the length of the longest common subsequence."""
    previous = [0] * (len(right) + 1)
    for left_token in left:
        current = [0]
        for index, right_token in enumerate(right, 1):
            if left_token == right_token:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def rouge_l(pred: str, ref: str) -> float:
    """Calculate the LCS F1-style ROUGE-L score over normalized tokens."""
    pred_tokens = tokens(pred)
    ref_tokens = tokens(ref)
    if not pred_tokens or not ref_tokens:
        return float(not pred_tokens and not ref_tokens)
    lcs = _lcs_length(pred_tokens, ref_tokens)
    precision = lcs / len(pred_tokens)
    recall = lcs / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def brevity_ratio(pred: str, ref: str) -> float:
    """Return the shorter-to-longer character length ratio."""
    longest = max(len(pred), len(ref))
    if longest == 0:
        return 1.0
    return min(len(pred), len(ref)) / longest


ENTITY_STOPWORDS = {
    "A",
    "An",
    "As",
    "For",
    "I",
    "In",
    "It",
    "No",
    "On",
    "The",
    "This",
    "What",
    "Which",
    "Who",
}


def named_entities(text: str) -> list[str]:
    """Find capitalized words as a lightweight named-entity heuristic."""
    words = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    return [word.lower() for word in words if word not in ENTITY_STOPWORDS]


def faithfulness(answer: str, source: str) -> float:
    """Return the fraction of answer entities that also occur in the source."""
    answer_entities = named_entities(answer)
    if not answer_entities:
        return 1.0
    source_entities = set(named_entities(source))
    supported = sum(entity in source_entities for entity in answer_entities)
    return supported / len(answer_entities)


def relevance(answer: str, question: str) -> float:
    """Return the fraction of normalized question words present in the answer."""
    question_tokens = set(tokens(question))
    if not question_tokens:
        return 1.0
    answer_tokens = set(tokens(answer))
    return len(question_tokens & answer_tokens) / len(question_tokens)


def context_precision(retrieved_docs: list[str], relevant_docs: list[str]) -> float:
    """Return the fraction of retrieved documents that are relevant."""
    if not retrieved_docs:
        return 0.0
    relevant = {normalized_text(document) for document in relevant_docs}
    retrieved_relevant = sum(
        normalized_text(document) in relevant for document in retrieved_docs
    )
    return retrieved_relevant / len(retrieved_docs)


def context_recall(retrieved_docs: list[str], relevant_docs: list[str]) -> float:
    """Return the fraction of relevant documents that were retrieved."""
    if not relevant_docs:
        return 1.0
    retrieved = {normalized_text(document) for document in retrieved_docs}
    found = sum(normalized_text(document) in retrieved for document in relevant_docs)
    return found / len(relevant_docs)


def evaluate_sample(sample: Sample) -> dict[str, float | str]:
    """Calculate all six answer metrics for one sample."""
    question, source, reference, generated = sample
    return {
        "question": question,
        "exact_match": exact_match(generated, reference),
        "token_f1": token_overlap_f1(generated, reference),
        "rouge_l": rouge_l(generated, reference),
        "brevity": brevity_ratio(generated, reference),
        "faithfulness": faithfulness(generated, source),
        "relevance": relevance(generated, question),
    }


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode and return text or a bracketed error."""
    try:
        result = subprocess.run(
            ["opencode", "run", "-m", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as error:
        return f"[opencode error] {error}"
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


JUDGE_PROMPT = """Rate this answer from 1 to 5 on both dimensions below.
- Faithfulness: does it stick to facts supported by the source context?
- Relevance: does it directly address the question?

Return only JSON in this exact shape:
{{"faithfulness": N, "relevance": N, "reasoning": "..."}}

Question: {question}
Source context: {source}
Reference answer: {reference}
Generated answer: {generated}
"""


def parse_judge_response(raw: str) -> dict[str, int | str] | None:
    """Extract and validate a judge JSON object from a model response."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    try:
        faithfulness_score = int(parsed["faithfulness"])
        relevance_score = int(parsed["relevance"])
    except (KeyError, TypeError, ValueError):
        return None
    if not 1 <= faithfulness_score <= 5 or not 1 <= relevance_score <= 5:
        return None
    return {
        "faithfulness": faithfulness_score,
        "relevance": relevance_score,
        "reasoning": str(parsed.get("reasoning", "")),
    }


def judge_samples(indices: list[int]) -> dict[int, dict[str, int | str]]:
    """Ask the LLM to judge selected samples and keep valid JSON responses."""
    judgments: dict[int, dict[str, int | str]] = {}
    for index in indices:
        question, source, reference, generated = TEST_SAMPLES[index]
        prompt = JUDGE_PROMPT.format(
            question=question,
            source=source,
            reference=reference,
            generated=generated,
        )
        raw = ask_llm(prompt)
        parsed = parse_judge_response(raw)
        if parsed is not None:
            judgments[index] = parsed
    return judgments


def _rank_values(values: list[float]) -> list[float]:
    """Return one-based average ranks, including ties."""
    indexed = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(indexed):
        end = position + 1
        while end < len(indexed) and indexed[end][1] == indexed[position][1]:
            end += 1
        rank = (position + 1 + end) / 2
        for item in indexed[position:end]:
            ranks[item[0]] = rank
        position = end
    return ranks


def rank_correlation(left: list[float], right: list[float]) -> float | None:
    """Calculate Spearman rank correlation without external dependencies."""
    if len(left) != len(right) or len(left) < 2:
        return None
    left_ranks = _rank_values(left)
    right_ranks = _rank_values(right)
    left_mean = sum(left_ranks) / len(left_ranks)
    right_mean = sum(right_ranks) / len(right_ranks)
    numerator = sum(
        (left_rank - left_mean) * (right_rank - right_mean)
        for left_rank, right_rank in zip(left_ranks, right_ranks)
    )
    left_variance = sum((rank - left_mean) ** 2 for rank in left_ranks)
    right_variance = sum((rank - right_mean) ** 2 for rank in right_ranks)
    denominator = (left_variance * right_variance) ** 0.5
    if denominator == 0:
        return 0.0
    return numerator / denominator


def format_score(value: float | int | str | None) -> str:
    """Format a metric or judge score for a compact table."""
    if value is None:
        return "--"
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f"{value}/5"
    return f"{value:.2f}"


def print_results(
    results: list[dict[str, float | str]],
    judgments: dict[int, dict[str, int | str]],
) -> None:
    """Print the complete metric and judge table."""
    print("\nRESULTS TABLE")
    header = "#  Type       Exact  TokF1  R-L    Brief  Faith  Rel    JudgeF JudgeR"
    print(header)
    print("-" * len(header))
    for index, result in enumerate(results):
        judgment = judgments.get(index, {})
        judge_f = judgment.get("faithfulness")
        judge_r = judgment.get("relevance")
        print(
            f"{index + 1:<3}{SAMPLE_LABELS[index]:<11}"
            f"{format_score(result['exact_match']):<7}"
            f"{format_score(result['token_f1']):<7}"
            f"{format_score(result['rouge_l']):<7}"
            f"{format_score(result['brevity']):<7}"
            f"{format_score(result['faithfulness']):<7}"
            f"{format_score(result['relevance']):<7}"
            f"{format_score(judge_f):<8}{format_score(judge_r)}"
        )


def correlation_summary(
    results: list[dict[str, float | str]],
    judgments: dict[int, dict[str, int | str]],
) -> list[dict[str, float | str | None]]:
    """Calculate metric correlations with judge faithfulness and relevance."""
    metric_names = [
        "exact_match",
        "token_f1",
        "rouge_l",
        "brevity",
        "faithfulness",
        "relevance",
    ]
    indices = sorted(judgments)
    summary: list[dict[str, float | str | None]] = []
    for metric in metric_names:
        metric_values = [float(results[index][metric]) for index in indices]
        judge_faithfulness = [
            float(judgments[index]["faithfulness"]) for index in indices
        ]
        judge_relevance = [float(judgments[index]["relevance"]) for index in indices]
        summary.append(
            {
                "metric": metric,
                "faithfulness": rank_correlation(metric_values, judge_faithfulness),
                "relevance": rank_correlation(metric_values, judge_relevance),
            }
        )
    return summary


def print_correlation_summary(
    summary: list[dict[str, float | str | None]],
) -> None:
    """Print rank correlations with both LLM judge dimensions."""
    print("\nCORRELATION SUMMARY (Spearman rank correlation)")
    print(f"{'Metric':<16} {'Judge faithfulness':>19} {'Judge relevance':>16}")
    print("-" * 54)
    for row in summary:
        faithfulness_score = row["faithfulness"]
        relevance_score = row["relevance"]
        faithfulness_text = (
            "--" if faithfulness_score is None else f"{faithfulness_score:+.2f}"
        )
        relevance_text = "--" if relevance_score is None else f"{relevance_score:+.2f}"
        print(f"{row['metric']:<16} {faithfulness_text:>19} {relevance_text:>16}")


def review_alerts(results: list[dict[str, float | str]]) -> list[int]:
    """Return one-based sample numbers below the review thresholds."""
    return [
        index + 1
        for index, result in enumerate(results)
        if float(result["faithfulness"]) < 0.5 or float(result["relevance"]) < 0.3
    ]


def save_results(
    results: list[dict[str, float | str]],
    judgments: dict[int, dict[str, int | str]],
    correlations: list[dict[str, float | str | None]],
    alerts: list[int],
    path: str,
) -> None:
    """Write the evaluation run to a Markdown artifact."""
    lines = [
        "# Part 7 — LLM Evaluation Results",
        "",
        f"> **Model:** `{MODEL}`  ",
        f"> **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Metric Results",
        "",
        "| # | Type | Exact | Token F1 | ROUGE-L | Brevity | Faithfulness | Relevance | Judge F | Judge R |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for index, result in enumerate(results):
        judgment = judgments.get(index, {})
        lines.append(
            f"| {index + 1} | {SAMPLE_LABELS[index]} | "
            f"{format_score(result['exact_match'])} | {format_score(result['token_f1'])} | "
            f"{format_score(result['rouge_l'])} | {format_score(result['brevity'])} | "
            f"{format_score(result['faithfulness'])} | {format_score(result['relevance'])} | "
            f"{format_score(judgment.get('faithfulness'))} | "
            f"{format_score(judgment.get('relevance'))} |"
        )

    lines.extend(
        [
            "",
            "## Correlation Summary",
            "",
            "| Metric | Judge faithfulness | Judge relevance |",
            "|---|---:|---:|",
        ]
    )
    for row in correlations:
        faithfulness_score = row["faithfulness"]
        relevance_score = row["relevance"]
        faithfulness_text = (
            "--" if faithfulness_score is None else f"{faithfulness_score:+.2f}"
        )
        relevance_text = "--" if relevance_score is None else f"{relevance_score:+.2f}"
        lines.append(f"| {row['metric']} | {faithfulness_text} | {relevance_text} |")

    lines.extend(["", "## Needs Review", ""])
    if alerts:
        lines.extend(
            f"- Sample {index}: faithfulness or relevance is below threshold."
            for index in alerts
        )
    else:
        lines.append("- No samples crossed the review thresholds.")

    lines.extend(
        [
            "",
            "## Metric Notes",
            "",
            "- Faithfulness uses capitalized-word entity overlap as a transparent heuristic.",
            "- Relevance is the fraction of unique question words found in the answer.",
            "- Correlations are exploratory because the LLM judge scores only three samples.",
        ]
    )
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main() -> None:
    """Run the offline metrics and optional LLM judge comparison."""
    parser = argparse.ArgumentParser(description="Part 7 LLM evaluation metrics lab")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="skip opencode judge calls and run entirely offline",
    )
    args = parser.parse_args()

    print(f"Model: {MODEL}")
    print(f"Evaluating {len(TEST_SAMPLES)} samples with six metrics...")
    results = [evaluate_sample(sample) for sample in TEST_SAMPLES]

    judge_indices = [0, 4, 6]
    judgments: dict[int, dict[str, int | str]] = {}
    if args.skip_llm:
        print("LLM judge: skipped")
    else:
        print(
            f"LLM judge: evaluating samples {[index + 1 for index in judge_indices]}..."
        )
        judgments = judge_samples(judge_indices)
        print(f"LLM judge: {len(judgments)}/{len(judge_indices)} valid responses")

    print_results(results, judgments)
    correlations = correlation_summary(results, judgments) if judgments else []
    if correlations:
        print_correlation_summary(correlations)
    else:
        print("\nCORRELATION SUMMARY: unavailable (no valid LLM judge scores)")

    alerts = review_alerts(results)
    print("\nNEEDS REVIEW")
    if alerts:
        print("  " + ", ".join(f"sample {index}" for index in alerts))
    else:
        print("  No samples crossed the thresholds.")

    results_path = os.path.join(os.path.dirname(__file__), "part7_results.md")
    save_results(results, judgments, correlations, alerts, results_path)
    print(f"\nResults saved to: {results_path}")
    print("DONE — Part 7 evaluation complete. Next: Part 8 (Building LLM Apps)")


if __name__ == "__main__":
    main()
