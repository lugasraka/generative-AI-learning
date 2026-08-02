"""
Part 12 — Neural Network Foundations: Interactive Playground

Walks through the core math behind modern LLMs: tokenization, scaled
dot-product attention, positional encoding, a simplified transformer
block, multi-head attention, and BPE tokenization. Each step prints
results as ASCII tables and optionally asks the LLM to explain what
just happened.

Run:  python nn_playground.py
      python nn_playground.py --skip-llm
      python nn_playground.py --html
"""

import argparse
import datetime
import math
import os
import random
import subprocess
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
LLM_TIMEOUT_SECONDS = 60

# ---------- LLM calling ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode and return text or a bracketed error."""
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


FALLBACK_EXPLANATIONS: dict[str, str] = {
    "tokenization": (
        "Tokenization splits raw text into smaller units (words or "
        "characters) that the model can process numerically."
    ),
    "attention": (
        "Scaled dot-product attention computes how much each token "
        "should 'look at' every other token, then aggregates values "
        "proportional to those weights."
    ),
    "positional_encoding": (
        "Positional encoding injects order information into token "
        "embeddings using sine/cosine waves at different frequencies."
    ),
    "transformer_block": (
        "A transformer block runs self-attention, adds a residual "
        "connection with layer norm, then passes through a feed-forward "
        "network with another residual + norm."
    ),
    "multi_head": (
        "Multi-head attention splits Q, K, V into parallel heads, runs "
        "attention independently on each, and concatenates the results."
    ),
    "bpe": (
        "BPE iteratively merges the most frequent token pairs, building "
        "a vocabulary from characters up to common subwords."
    ),
}


def llm_explain(online: bool, step_name: str, math_summary: str) -> str:
    """Ask the LLM to explain a step in two sentences."""
    if not online:
        return FALLBACK_EXPLANATIONS.get(step_name, "Step completed.")
    prompt = (
        f"Explain what just happened in the '{step_name}' step in exactly "
        f"2 simple sentences for someone learning neural networks.\n"
        f"Math summary: {math_summary}"
    )
    response = ask_llm(prompt)
    if response.startswith("["):
        return FALLBACK_EXPLANATIONS.get(step_name, "Step completed.")
    return response


# ---------- Display helpers ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def ascii_matrix(matrix: list[list[float]], name: str, precision: int = 3) -> None:
    """Print a matrix as an ASCII table."""
    print(f"\n  {name}:")
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    col_widths = [
        max(8, max(len(f"{matrix[r][c]:.{precision}f}") for r in range(n_rows)) + 1)
        for c in range(n_cols)
    ]
    header = "  " + "".join(f"{'c' + str(c):>{w}}" for c, w in enumerate(col_widths))
    print(header)
    print("  " + "-" * (sum(col_widths) + n_cols))
    for r in range(n_rows):
        row_str = "  " + "".join(
            f"{matrix[r][c]:>{col_widths[c]}.{precision}f}" for c in range(n_cols)
        )
        print(row_str)


def ascii_heatmap(matrix: list[list[float]], name: str) -> None:
    """Print a matrix with block-bar heatmap."""
    print(f"\n  {name} (heatmap):")
    blocks = " .:-=+*#%@"
    for r, row in enumerate(matrix):
        bar = ""
        for val in row:
            idx = min(len(blocks) - 1, int(val * (len(blocks) - 1)))
            bar += f" {blocks[idx]:>2}"
        print(f"  row {r}: {bar}")


# ---------- 1. Tokenization ----------

SAMPLE_SENTENCES: list[str] = [
    "The quick brown fox jumps over the lazy dog",
    "Transformers replaced recurrence with self-attention",
    "Attention is all you need",
]


def word_tokenize(text: str) -> list[str]:
    """Split text on whitespace into words."""
    return text.split()


def char_tokenize(text: str) -> list[str]:
    """Split text into individual characters."""
    return list(text)


def vocab_size(tokens: list[str]) -> int:
    """Return the number of unique tokens."""
    return len(set(tokens))


def run_tokenization(online: bool) -> None:
    banner("1. TOKENIZATION")
    print("\n  Word tokenization splits on whitespace.")
    print("  Character tokenization splits every character.\n")
    print(f"  {'Sentence':<48} {'Word Vocab':>10} {'Char Vocab':>11}")
    print("  " + "-" * 71)
    for sentence in SAMPLE_SENTENCES:
        w_tokens = word_tokenize(sentence)
        c_tokens = char_tokenize(sentence)
        print(f"  {sentence:<48} {vocab_size(w_tokens):>10} {vocab_size(c_tokens):>11}")
    print("\n  Word tokens for sentence 1:")
    print(f"    {word_tokenize(SAMPLE_SENTENCES[0])}")
    print("  Char tokens for sentence 1:")
    print(f"    {char_tokenize(SAMPLE_SENTENCES[0])[:20]}...")
    math_summary = f"Vocab sizes: {[vocab_size(word_tokenize(s)) for s in SAMPLE_SENTENCES]} (word), {[vocab_size(char_tokenize(s)) for s in SAMPLE_SENTENCES]} (char)"
    print(f"\n  {llm_explain(online, 'tokenization', math_summary)}")


# ---------- 2. Attention ----------


def softmax(row: list[float]) -> list[float]:
    """Compute softmax for a single row."""
    max_val = max(row)
    exp_vals = [math.exp(x - max_val) for x in row]
    total = sum(exp_vals)
    return [v / total for v in exp_vals]


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Matrix multiply a (m x n) by b (n x p) -> (m x p)."""
    m = len(a)
    n = len(a[0])
    p = len(b[0])
    result: list[list[float]] = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += a[i][k] * b[k][j]
    return result


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    """Transpose a matrix."""
    return [list(row) for row in zip(*matrix)]


def run_attention(online: bool) -> tuple[list[list[float]], list[list[float]]]:
    banner("2. SCALED DOT-PRODUCT ATTENTION")
    print("\n  Formula: Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V\n")

    Q = [
        [0.80, 0.10, 0.90],
        [0.10, 0.95, 0.20],
        [0.50, 0.50, 0.50],
        [0.90, 0.20, 0.80],
    ]
    K = [
        [0.60, 0.30, 0.70],
        [0.20, 0.85, 0.15],
        [0.70, 0.10, 0.90],
        [0.30, 0.60, 0.50],
    ]
    V = [
        [0.10, 0.80],
        [0.90, 0.20],
        [0.40, 0.60],
        [0.70, 0.30],
    ]

    ascii_matrix(Q, "Q (Query)")
    ascii_matrix(K, "K (Key)")
    ascii_matrix(V, "V (Value)")

    d_k = len(Q[0])
    scale = 1.0 / math.sqrt(d_k)
    K_T = transpose(K)
    scores = [[0.0] * len(K_T[0]) for _ in range(len(Q))]
    for i in range(len(Q)):
        for j in range(len(K_T[0])):
            for p_idx in range(d_k):
                scores[i][j] += Q[i][p_idx] * K_T[p_idx][j]
            scores[i][j] *= scale
    ascii_matrix(scores, "Raw scores (Q @ K^T / sqrt(d_k))")

    weights = [softmax(row) for row in scores]
    ascii_matrix(weights, "Attention weights (softmax)")
    ascii_heatmap(weights, "Attention weights")

    output = matmul(weights, V)
    ascii_matrix(output, "Output (weights @ V)")

    math_summary = f"4x3 Q,K,V matrices, d_k=3, scale={scale:.4f}, output 4x2"
    print(f"\n  {llm_explain(online, 'attention', math_summary)}")
    return weights, output


# ---------- 3. Positional Encoding ----------


def positional_encoding(position: int, d_model: int) -> list[float]:
    """Compute sine/cosine positional encoding."""
    pe: list[float] = []
    for i in range(d_model):
        angle = position / (10000 ** (2 * (i // 2) / d_model))
        if i % 2 == 0:
            pe.append(math.sin(angle))
        else:
            pe.append(math.cos(angle))
    return pe


def run_positional_encoding(online: bool) -> list[list[float]]:
    banner("3. POSITIONAL ENCODING")
    print("\n  Formula: PE(pos,2i) = sin(pos/10000^(2i/d_model))")
    print("           PE(pos,2i+1) = cos(pos/10000^(2i/d_model))\n")

    positions = 8
    d_model = 4
    pe_matrix = [positional_encoding(pos, d_model) for pos in range(positions)]
    ascii_matrix(
        pe_matrix, f"PE matrix ({positions} positions x d_model={d_model})", precision=4
    )

    print("\n  Visualization (+ = positive, - = negative, . = near zero):")
    for pos in range(positions):
        row_viz = "  "
        for val in pe_matrix[pos]:
            if val > 0.3:
                row_viz += " +++ "
            elif val > 0.05:
                row_viz += "  +  "
            elif val > -0.05:
                row_viz += "  .  "
            elif val > -0.3:
                row_viz += "  -  "
            else:
                row_viz += " --- "
        print(f"  pos {pos}: {row_viz}")

    math_summary = f"{positions} positions, d_model={d_model}, values in [-1, 1]"
    print(f"\n  {llm_explain(online, 'positional_encoding', math_summary)}")
    return pe_matrix


# ---------- 4. Transformer Block ----------


def relu_matrix(matrix: list[list[float]]) -> list[list[float]]:
    """Apply ReLU element-wise."""
    return [[max(0.0, v) for v in row] for row in matrix]


def layer_norm(matrix: list[list[float]], eps: float = 1e-5) -> list[list[float]]:
    """Apply layer normalization per row."""
    result: list[list[float]] = []
    for row in matrix:
        mean = sum(row) / len(row)
        variance = sum((x - mean) ** 2 for x in row) / len(row)
        std = math.sqrt(variance + eps)
        result.append([(x - mean) / std for x in row])
    return result


def add_matrices(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Element-wise addition."""
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def linear_layer(matrix: list[list[float]], w: list[list[float]]) -> list[list[float]]:
    """Simple linear transformation: matrix @ W."""
    return matmul(matrix, w)


def run_transformer_block(online: bool) -> None:
    banner("4. SIMPLE TRANSFORMER BLOCK")
    print("\n  Architecture: Input -> Self-Attention -> Add&Norm -> FFN -> Add&Norm\n")

    embeddings = [
        [0.20, 0.80, 0.10, 0.50],
        [0.60, 0.30, 0.70, 0.40],
        [0.10, 0.90, 0.30, 0.20],
        [0.70, 0.10, 0.60, 0.80],
    ]
    ascii_matrix(embeddings, "Input embeddings (4 tokens x 4 dims)")

    print("\n  --- Self-Attention ---")
    d_k = len(embeddings[0])
    scale = 1.0 / math.sqrt(d_k)
    K_T = transpose(embeddings)
    scores = [[0.0] * len(K_T[0]) for _ in range(len(embeddings))]
    for i in range(len(embeddings)):
        for j in range(len(K_T[0])):
            for p_idx in range(d_k):
                scores[i][j] += embeddings[i][p_idx] * K_T[p_idx][j]
            scores[i][j] *= scale
    weights = [softmax(row) for row in scores]
    attn_output = matmul(weights, embeddings)
    ascii_matrix(attn_output, "Self-attention output")

    print("\n  --- Residual Connection + Layer Norm ---")
    after_residual = add_matrices(embeddings, attn_output)
    after_norm = layer_norm(after_residual)
    ascii_matrix(after_norm, "After residual + layer norm")

    print("\n  --- Feed-Forward Network ---")
    d_model = 4
    d_ff = 8
    random.seed(42)
    w1 = [[random.gauss(0, 0.5) for _ in range(d_ff)] for _ in range(d_model)]
    w2 = [[random.gauss(0, 0.5) for _ in range(d_model)] for _ in range(d_ff)]
    ff_hidden = relu_matrix(linear_layer(after_norm, w1))
    ascii_matrix(ff_hidden, "FFN hidden (ReLU)")
    ff_output = linear_layer(ff_hidden, w2)
    ascii_matrix(ff_output, "FFN output")

    print("\n  --- Final Residual + Layer Norm ---")
    final_residual = add_matrices(after_norm, ff_output)
    final_output = layer_norm(final_residual)
    ascii_matrix(final_output, "Transformer block output")

    print("\n  Input vs Output:")
    print(f"  {'Token':>6}  {'Input[0:3]':<24}  {'Output[0:3]':<24}")
    print("  " + "-" * 58)
    for i in range(len(embeddings)):
        inp = " ".join(f"{v:.3f}" for v in embeddings[i][:3])
        out = " ".join(f"{v:.3f}" for v in final_output[i][:3])
        print(f"  {i:>6}  [{inp}]  [{out}]")

    math_summary = (
        "4x4 embeddings, self-attention, residual+norm, 4->8->4 FFN with ReLU"
    )
    print(f"\n  {llm_explain(online, 'transformer_block', math_summary)}")


# ---------- 5. Multi-Head Attention ----------


def run_multi_head_attention(online: bool) -> None:
    banner("5. MULTI-HEAD ATTENTION (BONUS)")
    print("\n  Split Q, K, V into 2 heads, run attention on each, concatenate.\n")

    n_heads = 2
    d_model = 4
    d_k = d_model // n_heads

    Q = [
        [0.80, 0.10, 0.90, 0.30],
        [0.10, 0.95, 0.20, 0.60],
        [0.50, 0.50, 0.50, 0.40],
        [0.90, 0.20, 0.80, 0.15],
    ]
    K = [
        [0.60, 0.30, 0.70, 0.50],
        [0.20, 0.85, 0.15, 0.70],
        [0.70, 0.10, 0.90, 0.30],
        [0.30, 0.60, 0.50, 0.80],
    ]
    V = [
        [0.10, 0.80, 0.40, 0.30],
        [0.90, 0.20, 0.60, 0.10],
        [0.40, 0.60, 0.20, 0.70],
        [0.70, 0.30, 0.50, 0.50],
    ]

    head_outputs: list[list[float]] = []
    for h in range(n_heads):
        start = h * d_k
        end = start + d_k
        q_h = [row[start:end] for row in Q]
        k_h = [row[start:end] for row in K]
        v_h = [row[start:end] for row in V]

        print(
            f"  Head {h + 1}: Q[:,{start}:{end}], K[:,{start}:{end}], V[:,{start}:{end}]"
        )
        ascii_matrix(q_h, f"  Q head {h + 1}")

        scale = 1.0 / math.sqrt(d_k)
        k_h_t = transpose(k_h)
        scores = [[0.0] * len(k_h_t[0]) for _ in range(len(q_h))]
        for i in range(len(q_h)):
            for j in range(len(k_h_t[0])):
                for p_idx in range(d_k):
                    scores[i][j] += q_h[i][p_idx] * k_h_t[p_idx][j]
                scores[i][j] *= scale
        weights = [softmax(row) for row in scores]
        out_h = matmul(weights, v_h)
        ascii_matrix(weights, f"  Weights head {h + 1}")
        print(f"  Output head {h + 1}:")
        ascii_matrix(out_h, f"  Out head {h + 1}")

        for row in out_h:
            head_outputs.append(row)

    concat: list[list[float]] = []
    for i in range(len(Q)):
        row = []
        for h in range(n_heads):
            start = h * d_k
            row.extend(head_outputs[i * n_heads + h][start : start + d_k])
        concat.append(row)

    random.seed(99)
    w_proj = [[random.gauss(0, 0.5) for _ in range(d_model)] for _ in range(d_model)]
    projected = matmul(concat, w_proj)

    ascii_matrix(concat, "Concatenated heads")
    ascii_matrix(projected, "Projected output")

    math_summary = (
        f"2 heads, d_k={d_k}, concat dim={d_model}, projected back to d_model={d_model}"
    )
    print(f"\n  {llm_explain(online, 'multi_head', math_summary)}")


# ---------- 6. BPE Tokenization ----------


def run_bpe(online: bool) -> None:
    banner("6. BYTE-PAIR ENCODING (BONUS)")
    corpus = [
        "low",
        "low",
        "low",
        "low",
        "lowest",
        "newer",
        "newer",
        "wider",
        "wider",
        "wider",
    ]
    print(f"\n  Corpus ({len(corpus)} words): {corpus}\n")

    tokens_list = [list(word) + ["</w>"] for word in corpus]
    merges = 5

    for merge_step in range(merges):
        pairs: dict[tuple[str, str], int] = {}
        for tokens in tokens_list:
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                pairs[pair] = pairs.get(pair, 0) + 1
        if not pairs:
            break
        best_pair = max(pairs, key=lambda k: pairs[k])
        best_count = pairs[best_pair]
        merged_token = best_pair[0] + best_pair[1]

        new_tokens_list: list[list[str]] = []
        for tokens in tokens_list:
            new_tokens: list[str] = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == best_pair:
                    new_tokens.append(merged_token)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            new_tokens_list.append(new_tokens)
        tokens_list = new_tokens_list

        print(
            f"  Merge {merge_step + 1}: '{best_pair[0]}' + '{best_pair[1]}' -> '{merged_token}' (count={best_count})"
        )
        print(
            f"    Vocabulary: {sorted({tok for tokens in tokens_list for tok in tokens})}"
        )
        sample = [tokens_list[i] for i in range(min(3, len(tokens_list)))]
        print(f"    Sample: {sample}\n")

    final_vocab = sorted({tok for tokens in tokens_list for tok in tokens})
    print(f"  Final vocabulary ({len(final_vocab)} tokens): {final_vocab}")
    print(f"  Example: '{corpus[0]}' -> {tokens_list[0]}")
    print(f"  Example: '{corpus[5]}' -> {tokens_list[5]}")

    math_summary = f"10 words, {merges} merges, final vocab size {len(final_vocab)}"
    print(f"\n  {llm_explain(online, 'bpe', math_summary)}")


# ---------- Summary ----------


def print_summary() -> None:
    banner("EVOLUTION OF LANGUAGE MODEL ARCHITECTURES")
    steps = [
        (
            "RNN",
            "Processes sequences step-by-step with a hidden state. Struggles with long-range dependencies.",
        ),
        (
            "LSTM",
            "Adds a memory cell and 3 gates (input, forget, output) to retain information over longer sequences.",
        ),
        (
            "Seq2Seq",
            "Encoder-decoder architecture for variable-length I/O. Bottleneck: compresses everything into one vector.",
        ),
        (
            "Attention",
            "Decoder looks at ALL encoder states, learning which input parts to focus on per output token.",
        ),
        (
            "Transformer",
            "Replaces recurrence entirely with self-attention. Every token attends to every other token in parallel.",
        ),
        (
            "BERT",
            "Bidirectional encoder. Sees left + right context. Uses masked language modeling for pre-training.",
        ),
        (
            "GPT",
            "Autoregressive decoder. Sees only left context. Uses next-token prediction. Scales to billions of params.",
        ),
        (
            "T5",
            "Encoder-decoder that frames every NLP task as text-to-text. A unified framework.",
        ),
    ]
    print()
    for i, (name, desc) in enumerate(steps):
        arrow = " --> " if i < len(steps) - 1 else "     "
        print(f"  {name:<12}{arrow}{desc}")
    print()


# ---------- Main ----------


def main() -> None:
    parser = argparse.ArgumentParser(description="Part 12 NN Foundations Playground")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="skip opencode calls and use local explanations",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="generate a self-contained interactive HTML playground",
    )
    args = parser.parse_args()
    online = not args.skip_llm

    print(f"Model: {MODEL}")
    print(f"LLM calls: {'enabled' if online else 'skipped'}")

    run_tokenization(online)
    run_attention(online)
    run_positional_encoding(online)
    run_transformer_block(online)
    run_multi_head_attention(online)
    run_bpe(online)
    print_summary()

    results_path = os.path.join(os.path.dirname(__file__), "part12_results.md")
    lines = [
        "# Part 12 — Neural Network Foundations Results",
        "",
        f"> **Model:** `{MODEL}`  ",
        f"> **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Tokenization",
        "",
        f"- Word vocab sizes: {[vocab_size(word_tokenize(s)) for s in SAMPLE_SENTENCES]}",
        f"- Char vocab sizes: {[vocab_size(char_tokenize(s)) for s in SAMPLE_SENTENCES]}",
        "",
        "## Attention",
        "",
        "- 4 tokens, d_k=3, Q/K/V hardcoded",
        "- Softmax normalization + weighted sum over values",
        "",
        "## Positional Encoding",
        "",
        "- 8 positions, d_model=4, sine/cosine waves",
        "",
        "## Transformer Block",
        "",
        "- Self-attention -> residual + layer norm -> FFN -> residual + layer norm",
        "",
        "## Multi-Head Attention",
        "",
        "- 2 heads, d_k=2, concatenated and projected back to d_model=4",
        "",
        "## BPE",
        "",
        "- 10-word corpus, 5 merge iterations",
        "",
        "## Architecture Evolution",
        "",
        "RNN -> LSTM -> Seq2Seq -> Attention -> Transformer -> BERT -> GPT -> T5 -> Modern LLMs",
        "",
        "## Takeaway",
        "",
        "Every modern LLM is built from these foundational blocks: tokenization "
        "converts text to tokens, attention lets tokens talk to each other, "
        "positional encoding adds order, and transformer layers stack these "
        "operations to learn deep language patterns.",
    ]
    with open(results_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    print(f"Results saved to: {results_path}")

    if args.html:
        page = build_html()
        html_path = os.path.join(os.path.dirname(__file__), "nn_playground.html")
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(page)
        print(f"HTML playground written to: {html_path}")

    print("DONE — Part 12 complete. Course finished! 🎉")


# ---------- HTML ----------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Neural Network Playground</title>
<style>
:root{--blue:#3b82f6;--green:#22c55e;--purple:#8b5cf6;--amber:#f59e0b;--red:#ef4444;--text:#1e293b;--muted:#64748b;--border:#e2e8f0;--bg:#f1f5f9;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--text);background:var(--bg);line-height:1.6}
.container{max-width:1040px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.8rem;margin-bottom:4px}
.subtitle{color:var(--muted);font-size:0.95rem;margin-bottom:22px}
h2{font-size:1.25rem;margin:28px 0 12px}
h3{font-size:1rem;margin-bottom:8px}

.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:16px}
.card h3{color:var(--blue)}
.input-row{display:flex;gap:12px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.input-row input[type=text]{flex:1;min-width:200px;padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-size:0.95rem}
.input-row input[type=range]{width:120px}
.input-row label{font-size:0.85rem;font-weight:600;min-width:60px}
.input-row button{background:var(--blue);color:#fff;border:none;border-radius:6px;padding:8px 18px;font-size:0.9rem;cursor:pointer}
.input-row button:hover{background:#2563eb}
.token-display{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.token{display:inline-block;padding:3px 8px;border-radius:4px;font-size:0.82rem;font-family:monospace}
.token.word{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe}
.token.char{background:#f0fdf4;color:#166534;border:1px solid #bbf7d0}

table.matrix{border-collapse:collapse;font-size:0.82rem;font-family:monospace;margin:8px 0}
table.matrix th{background:#f8fafc;padding:6px 10px;border:1px solid var(--border);font-weight:600}
table.matrix td{padding:5px 10px;border:1px solid var(--border);text-align:right}
table.matrix td.pos{background:#f0fdf4}
table.matrix td.neg{background:#fef2f2}
table.matrix td.zero{background:#f8fafc}

.heatmap-table{border-collapse:collapse;font-size:0.8rem;font-family:monospace;margin:8px 0}
.heatmap-table td{padding:4px 6px;border:1px solid var(--border);text-align:center;width:32px;height:28px}

.timeline-row{display:flex;align-items:flex-start;gap:16px;margin-bottom:14px}
.timeline-dot{width:12px;height:12px;border-radius:50%;background:var(--blue);margin-top:6px;flex-shrink:0}
.timeline-dot.active{background:var(--green);transform:scale(1.3)}
.timeline-text h4{font-size:0.95rem;margin-bottom:2px}
.timeline-text p{font-size:0.85rem;color:var(--muted)}

.explain-box{background:#f0f9ff;border-left:3px solid var(--blue);padding:10px 14px;border-radius:0 6px 6px 0;font-size:0.88rem;margin-top:12px}

svg text{font-family:monospace}

.play-btn{background:var(--green);color:#fff;border:none;border-radius:6px;padding:8px 20px;font-size:0.9rem;cursor:pointer}
.play-btn:hover{background:#16a34a}
.step-indicator{font-size:0.85rem;color:var(--muted);margin-left:12px}
</style>
</head>
<body>
<div class="container">
<h1>Neural Network Playground</h1>
<p class="subtitle">Walk through the math that powers modern LLMs. Edit inputs and watch the computations update live.</p>

<div class="card" id="tokenize-card">
<h3>1. Tokenization</h3>
<div class="input-row"><label>Text:</label><input type="text" id="token-input" value="The quick brown fox jumps over the lazy dog"></div>
<div id="token-results"></div>
</div>

<div class="card" id="attention-card">
<h3>2. Scaled Dot-Product Attention</h3>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px">Click cells to edit Q values. K and V are fixed. Output updates live.</p>
<div style="overflow-x:auto" id="attention-matrices"></div>
<div class="explain-box" id="attention-explain">Adjust values to see attention weights change.</div>
</div>

<div class="card" id="pe-card">
<h3>3. Positional Encoding</h3>
<div class="input-row">
<label>Position:</label><input type="range" id="pe-pos" min="0" max="15" value="0">
<span id="pe-pos-val">0</span>
<label>d_model:</label><input type="range" id="pe-dim" min="2" max="16" value="8" step="2">
<span id="pe-dim-val">8</span>
</div>
<div id="pe-results"></div>
</div>

<div class="card" id="arch-card">
<h3>Architecture Evolution</h3>
<div id="arch-timeline"></div>
</div>
</div>

<script>
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

/* ---------- Tokenization ---------- */
function runTokenize(){
  const text=document.getElementById('token-input').value;
  const words=text.split(/\\s+/).filter(Boolean);
  const chars=text.split('');
  const wVocab=[...new Set(words)].length;
  const cVocab=[...new Set(chars)].length;
  let h='<p style="font-size:0.88rem"><strong>Words</strong> ('+words.length+' tokens, vocab='+wVocab+'): </p><div class="token-display">';
  words.forEach(w=>{h+='<span class="token word">'+esc(w)+'</span>';});
  h+='</div><p style="font-size:0.88rem;margin-top:10px"><strong>Characters</strong> ('+chars.length+' tokens, vocab='+cVocab+'): </p><div class="token-display">';
  const show=chars.slice(0,60);
  show.forEach(c=>{h+='<span class="token char">'+esc(c===' '?'&nbsp;':c)+'</span>';});
  if(chars.length>60) h+='<span class="token char">...</span>';
  h+='</div>';
  document.getElementById('token-results').innerHTML=h;
}

/* ---------- Attention ---------- */
let Q=[[0.80,0.10,0.90],[0.10,0.95,0.20],[0.50,0.50,0.50],[0.90,0.20,0.80]];
const K=[[0.60,0.30,0.70],[0.20,0.85,0.15],[0.70,0.10,0.90],[0.30,0.60,0.50]];
const V=[[0.10,0.80],[0.90,0.20],[0.40,0.60],[0.70,0.30]];

function softmax(arr){const mx=Math.max(...arr);const ex=arr.map(x=>Math.exp(x-mx));const s=ex.reduce((a,b)=>a+b);return ex.map(x=>x/s);}
function transpose(m){return m[0].map((_,i)=>m.map(r=>r[i]));}
function matmul(a,b){const m=a.length,n=a[0].length,p=b[0].length;const r=Array.from({length:m},()=>Array(p).fill(0));for(let i=0;i<m;i++)for(let j=0;j<p;j++)for(let k=0;k<n;k++)r[i][j]+=a[i][k]*b[k][j];return r;}

function matToHTML(matrix,name,editable,cls){
  let h='<table class="'+(cls||'matrix')+'"><tr><th>'+esc(name)+'</th>';
  for(let j=0;j<matrix[0].length;j++) h+='<th>c'+j+'</th>';
  h+='</tr>';
  for(let i=0;i<matrix.length;i++){
    h+='<tr><th>r'+i+'</th>';
    for(let j=0;j<matrix[0].length;j++){
      const v=matrix[i][j];
      const valStr=v.toFixed(3);
      if(editable){
        h+='<td><input type="text" value="'+valStr+'" style="width:60px;text-align:right;border:none;font-family:monospace;font-size:0.82rem" data-r="'+i+'" data-c="'+j+'" onchange="updateQ(this)"></td>';
      } else {
        const cls2=v>0.05?'pos':(v<-0.05?'neg':'zero');
        h+='<td class="'+cls2+'">'+valStr+'</td>';
      }
    }
    h+='</tr>';
  }
  h+='</table>';
  return h;
}

function heatCell(val){
  const blocks=['.','-','=','+','*','#','%','@'];
  const idx=Math.min(blocks.length-1,Math.floor(val*(blocks.length-1)));
  const bg=`hsl(220,70%,${90-val*60}%)`;
  return '<td style="background:'+bg+';text-align:center;font-family:monospace">'+val.toFixed(2)+'</td>';
}

function updateQ(el){
  const r=+el.dataset.r,c=+el.dataset.c;
  Q[r][c]=parseFloat(el.value)||0;
  runAttention();
}

function runAttention(){
  const dk=Q[0].length,scale=1/Math.sqrt(dk);
  const KT=transpose(K);
  const scores=Q.map(q=>KT[0].map((_,j)=>{let s=0;for(let p=0;p<dk;p++)s+=q[p]*KT[p][j];return s*scale;}));
  const weights=scores.map(row=>softmax(row));
  const output=matmul(weights,V);

  let h=matToHTML(Q,'Q (editable)',true);
  h+='<br>'+matToHTML(K,'K (fixed)',false);
  h+='<br>'+matToHTML(V,'V (fixed)',false);
  h+='<br>'+matToHTML(scores,'Scores',false);
  h+='<br><p style="font-weight:600;margin:4px 0">Attention weights:</p>';
  h+='<table class="heatmap-table"><tr><th></th><th>c0</th><th>c1</th><th>c2</th><th>c3</th></tr>';
  for(let i=0;i<weights.length;i++){
    h+='<tr><th>r'+i+'</th>';
    for(let j=0;j<weights[i].length;j++) h+=heatCell(weights[i][j]);
    h+='</tr>';
  }
  h+='</table>';
  h+='<br>'+matToHTML(output,'Output',false);
  document.getElementById('attention-matrices').innerHTML=h;
  const maxW=Math.max(...weights.flat());
  const maxIdx=weights.flat().indexOf(maxW);
  const r=Math.floor(maxIdx/4),c=maxIdx%4;
  document.getElementById('attention-explain').innerHTML='Token '+r+' attends most to token '+c+' (weight='+maxW.toFixed(3)+'). The output blends V values according to these attention weights.';
}

/* ---------- Positional Encoding ---------- */
function pe(pos,d){
  const out=[];
  for(let i=0;i<d;i++){
    const angle=pos/Math.pow(10000,2*Math.floor(i/2)/d);
    out.push(i%2===0?Math.sin(angle):Math.cos(angle));
  }
  return out;
}
function runPE(){
  const pos=+document.getElementById('pe-pos').value;
  const dim=+document.getElementById('pe-dim').value;
  document.getElementById('pe-pos-val').textContent=pos;
  document.getElementById('pe-dim-val').textContent=dim;
  const vec=pe(pos,dim);
  let h='<table class="matrix"><tr><th>dim</th>';
  for(let i=0;i<dim;i++) h+='<th>'+i+'</th>';
  h+='</tr><tr><th>PE('+pos+')</th>';
  for(let i=0;i<dim;i++){
    const v=vec[i];
    const cls=v>0.05?'pos':(v<-0.05?'neg':'zero');
    h+='<td class="'+cls+'">'+v.toFixed(4)+'</td>';
  }
  h+='</tr></table>';
  h+='<div style="margin-top:8px;font-family:monospace;font-size:0.9rem">';
  for(let i=0;i<dim;i++){
    const v=vec[i];
    const bar=Math.abs(v)*20;
    const sym=i%2===0?'sin':'cos ';
    const col=v>=0?'var(--blue)':'var(--red)';
    h+='<div style="display:flex;align-items:center;gap:8px;margin:2px 0"><span style="width:60px;font-size:0.8rem">'+sym+'('+i+')</span><span style="display:inline-block;height:14px;width:'+bar+'px;background:'+col+';border-radius:3px"></span><span style="font-size:0.8rem">'+v.toFixed(4)+'</span></div>';
  }
  h+='</div>';
  document.getElementById('pe-results').innerHTML=h;
}

/* ---------- Architecture Timeline ---------- */
const ARCH=[
  {name:'RNN',desc:'Processes sequences step-by-step with a hidden state. Struggles with long-range dependencies.',color:'var(--red)'},
  {name:'LSTM',desc:'Adds a memory cell and 3 gates to retain information over longer sequences.',color:'var(--amber)'},
  {name:'Seq2Seq',desc:'Encoder-decoder for variable-length I/O. Bottleneck: compresses into one vector.',color:'var(--purple)'},
  {name:'Attention',desc:'Decoder looks at ALL encoder states, learning which input parts to focus on.',color:'var(--blue)'},
  {name:'Transformer',desc:'Self-attention replaces recurrence. Every token attends to every other token in parallel.',color:'var(--green)'},
  {name:'BERT',desc:'Bidirectional encoder. Sees left + right context via masked language modeling.',color:'var(--blue)'},
  {name:'GPT',desc:'Autoregressive decoder. Next-token prediction. Scales to billions of parameters.',color:'var(--green)'},
  {name:'T5',desc:'Encoder-decoder that frames every NLP task as text-to-text.',color:'var(--purple)'},
  {name:'Modern LLMs',desc:'LLaMA, ChatGPT — built on Transformer decoders with RLHF, longer context, multimodal.',color:'var(--amber)'},
];
function renderTimeline(){
  let h='';
  ARCH.forEach((a,i)=>{
    h+='<div class="timeline-row"><div class="timeline-dot" style="background:'+a.color+'"></div><div class="timeline-text"><h4>'+a.name+'</h4><p>'+a.desc+'</p></div></div>';
    if(i<ARCH.length-1) h+='<div style="margin-left:5px;width:2px;height:8px;background:var(--border)"></div>';
  });
  document.getElementById('arch-timeline').innerHTML=h;
}

/* ---------- Init ---------- */
function init(){
  document.getElementById('token-input').addEventListener('input',runTokenize);
  document.getElementById('pe-pos').addEventListener('input',runPE);
  document.getElementById('pe-dim').addEventListener('input',runPE);
  runTokenize();runAttention();runPE();renderTimeline();
}
window.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>
"""


def build_html() -> str:
    return HTML_TEMPLATE


if __name__ == "__main__":
    main()
