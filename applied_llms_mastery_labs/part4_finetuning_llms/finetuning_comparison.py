"""
Part 4 — Fine-Tuning LLMs: Fine-Tuning Comparison Simulator

Simulates 3 fine-tuning methods (full, LoRA, prompt tuning) with realistic
metrics, shows side-by-side comparison, and suggests the best method for your
setup. Includes a budget optimizer and ASCII loss curve.

Run:  python finetuning_comparison.py
"""

import datetime
import math
import os
import random
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/mimo-v2.5")

# ---------- Method definitions ----------

METHODS = {
    "full_finetuning": {
        "label": "Full Fine-Tuning",
        "updates": "100%",
        "gpu_memory": "very high",
        "speed": "slow",
        "risk_of_forgetting": "high",
        "cost_per_hour": 12.0,
        "efficiency": 1.0,
        "memory_multiplier": 4.0,
        "time_multiplier": 3.0,
    },
    "lora_peft": {
        "label": "LoRA (PEFT)",
        "updates": "~1-5%",
        "gpu_memory": "moderate",
        "speed": "fast",
        "risk_of_forgetting": "low",
        "cost_per_hour": 4.0,
        "efficiency": 0.85,
        "memory_multiplier": 1.5,
        "time_multiplier": 1.0,
    },
    "prompt_tuning": {
        "label": "Prompt Tuning",
        "updates": "<1%",
        "gpu_memory": "minimal",
        "speed": "very fast",
        "risk_of_forgetting": "none",
        "cost_per_hour": 1.0,
        "efficiency": 0.65,
        "memory_multiplier": 0.3,
        "time_multiplier": 0.3,
    },
}

# ---------- Simulation ----------


def simulate_training(method_key: str, params: dict) -> dict:
    """Run a mock training simulation and return metrics."""
    m = METHODS[method_key]
    dataset_size = params["dataset_size"]
    model_size = params["model_size"]
    epochs = params["epochs"]
    lr = params["learning_rate"]

    # Loss curve
    initial_loss = 2.5 + random.uniform(-0.2, 0.2)
    data_factor = math.log1p(dataset_size) / 100
    losses = []
    for e in range(1, epochs + 1):
        base = initial_loss * math.exp(-lr * e * data_factor * m["efficiency"])
        noise = random.uniform(-0.05, 0.05)
        loss = max(0.1, base + noise)
        losses.append(round(loss, 4))

    # Training time (seconds)
    base_time = model_size * dataset_size * epochs * m["time_multiplier"] * 0.002
    training_seconds = max(5, base_time)
    if training_seconds < 60:
        time_str = f"{training_seconds:.1f}s"
    elif training_seconds < 3600:
        time_str = f"{training_seconds / 60:.1f}min"
    else:
        time_str = f"{training_seconds / 3600:.1f}h"

    # GPU memory (GB)
    gpu_gb = model_size * m["memory_multiplier"]
    gpu_str = f"{gpu_gb:.1f}GB"

    # Final accuracy
    data_factor_acc = min(1.0, dataset_size / 5000)
    epoch_factor_acc = min(1.0, epochs / 10)
    lr_factor = min(1.0, lr / 0.001)
    final_acc = (
        0.5
        + 0.35 * data_factor_acc * m["efficiency"]
        + 0.1 * epoch_factor_acc
        + 0.05 * lr_factor
    )
    final_acc = min(0.98, final_acc + random.uniform(-0.02, 0.02))
    final_acc = round(final_acc, 3)

    # Cost estimate
    cost = (training_seconds / 3600) * m["cost_per_hour"]
    cost_str = f"${cost:.2f}"

    return {
        "method": m["label"],
        "method_key": method_key,
        "final_loss": losses[-1],
        "final_accuracy": final_acc,
        "training_time": time_str,
        "training_seconds": training_seconds,
        "gpu_memory": gpu_str,
        "gpu_gb": gpu_gb,
        "cost": cost,
        "cost_str": cost_str,
        "losses": losses,
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


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_comparison_table(results: list[dict]) -> None:
    banner("SIDE-BY-SIDE COMPARISON")
    print(
        f"\n  {'Method':<22} {'Loss':>8} {'Accuracy':>10} {'Time':>8} {'GPU':>8} {'Cost':>10}"
    )
    print("  " + "-" * 76)
    for r in results:
        print(
            f"  {r['method']:<22} {r['final_loss']:>8.4f} {r['final_accuracy']:>9.1%} "
            f"{r['training_time']:>8} {r['gpu_memory']:>8} {r['cost_str']:>10}"
        )


def print_loss_curve(losses: list[float], method_name: str) -> None:
    """Print an ASCII horizontal bar chart of the loss curve."""
    if not losses:
        return
    max_loss = max(losses)
    bar_width = 40
    print(f"\n  {method_name}:")
    for i, loss in enumerate(losses, 1):
        filled = round(loss / max_loss * bar_width)
        bar = "#" * filled + "." * (bar_width - filled)
        print(f"    Epoch {i:>2}: [{bar}] {loss:.4f}")


def print_verdict(results: list[dict], params: dict) -> None:
    """Determine the best method for the user's parameters."""
    dataset = params["dataset_size"]
    model_b = params["model_size"]

    # Rule-based verdict
    if model_b >= 50 and dataset >= 5000:
        winner = "full_finetuning"
        reason = (
            "Massive model + large dataset — full fine-tuning maximizes performance."
        )
    elif dataset <= 200:
        winner = "prompt_tuning"
        reason = "Small dataset — prompt tuning avoids overfitting and is cheapest."
    elif model_b >= 20 and params["epochs"] >= 5:
        winner = "full_finetuning"
        reason = (
            "Large model with enough epochs — full fine-tuning gets the best results."
        )
    elif params.get("budget") and params["budget"] < 10:
        winner = "prompt_tuning"
        reason = "Tight budget — prompt tuning is the most cost-effective option."
    else:
        winner = "lora_peft"
        reason = "LoRA gives the best balance of performance, speed, and cost for most setups."

    winner_result = next(r for r in results if r["method_key"] == winner)

    banner("VERDICT")
    print(f"\n  Best method: {METHODS[winner]['label']}")
    print(f"  Reason: {reason}")
    print(
        f"  Accuracy: {winner_result['final_accuracy']:.1%} | Cost: {winner_result['cost_str']}"
    )


def llm_recommendation(results: list[dict]) -> str:
    """Send comparison to LLM and get a recommendation."""
    summary_lines = []
    for r in results:
        summary_lines.append(
            f"- {r['method']}: loss={r['final_loss']:.4f}, "
            f"accuracy={r['final_accuracy']:.1%}, "
            f"time={r['training_time']}, cost={r['cost_str']}"
        )
    summary = "\n".join(summary_lines)

    prompt = (
        f"Given these fine-tuning comparison results:\n{summary}\n\n"
        f"Which fine-tuning method would you recommend and why? Answer in 2 sentences."
    )
    return ask_llm(prompt)


# ---------- Budget optimizer ----------


def budget_optimizer(budget: float, params: dict) -> None:
    """Show max resources affordable per method within a dollar budget."""
    banner(f"BUDGET OPTIMIZER (${budget:.0f} budget)")

    print(
        f"\n  {'Method':<22} {'Max Model':>10} {'Max Dataset':>12} {'Max Epochs':>11}"
    )
    print("  " + "-" * 65)

    for key, m in METHODS.items():
        # Hours we can afford
        hours = budget / m["cost_per_hour"]
        seconds = hours * 3600

        # Solve for max model_size given dataset and epochs
        # time = model * dataset * epochs * multiplier * 0.002
        max_model = seconds / (
            params["dataset_size"] * params["epochs"] * m["time_multiplier"] * 0.002
        )
        max_model = max(1, min(200, max_model))

        # Solve for max dataset given model and epochs
        max_dataset = seconds / (
            params["model_size"] * params["epochs"] * m["time_multiplier"] * 0.002
        )
        max_dataset = max(10, min(50000, max_dataset))

        # Solve for max epochs given model and dataset
        max_epochs = seconds / (
            params["model_size"] * params["dataset_size"] * m["time_multiplier"] * 0.002
        )
        max_epochs = max(1, min(50, max_epochs))

        print(
            f"  {m['label']:<22} {max_model:>8.0f}B {max_dataset:>10.0f} ex "
            f"{max_epochs:>9.0f} ep"
        )


# ---------- ASCII loss curve (all methods) ----------


def print_all_loss_curves(results: list[dict]) -> None:
    """Print loss curves for all methods side by side."""
    banner("LOSS CURVES")
    max_loss = max(r["final_loss"] for r in results) * 2
    bar_width = 35

    # Find max epochs across all results
    max_epochs = max(len(r["losses"]) for r in results)

    for epoch_idx in range(max_epochs):
        print(f"\n  Epoch {epoch_idx + 1}:")
        for r in results:
            if epoch_idx < len(r["losses"]):
                loss = r["losses"][epoch_idx]
                filled = round(loss / max_loss * bar_width)
                bar = "#" * filled + "." * (bar_width - filled)
                print(f"    {r['method']:<22} [{bar}] {loss:.4f}")
            else:
                print(f"    {r['method']:<22} [{'.' * bar_width}] ---")


# ---------- Save results ----------


def save_results(
    results: list[dict],
    params: dict,
    verdict_method: str,
    verdict_reason: str,
    llm_text: str,
    budget_text: str | None,
) -> str:
    """Write results to part4_results.md."""
    lines: list[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("# Part 4 — Fine-Tuning Comparison Results\n")
    lines.append(f"> **Model:** `{MODEL}`  ")
    lines.append(f"> **Date:** {now}\n")

    # Parameters
    lines.append("## Parameters\n")
    lines.append(f"- Dataset size: {params['dataset_size']:,} examples")
    lines.append(f"- Model size: {params['model_size']}B parameters")
    lines.append(f"- Epochs: {params['epochs']}")
    lines.append(f"- Learning rate: {params['learning_rate']}")
    lines.append("")

    # Comparison table
    lines.append("## Comparison Table\n")
    lines.append("| Method | Loss | Accuracy | Time | GPU | Cost |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for r in results:
        lines.append(
            f"| {r['method']} | {r['final_loss']:.4f} | {r['final_accuracy']:.1%} | "
            f"{r['training_time']} | {r['gpu_memory']} | {r['cost_str']} |"
        )
    lines.append("")

    # Loss curves
    lines.append("## Loss Curves\n")
    max_loss = max(r["final_loss"] for r in results) * 2
    bar_width = 35
    max_epochs = max(len(r["losses"]) for r in results)
    for epoch_idx in range(max_epochs):
        lines.append(f"### Epoch {epoch_idx + 1}\n")
        lines.append("```")
        for r in results:
            if epoch_idx < len(r["losses"]):
                loss = r["losses"][epoch_idx]
                filled = round(loss / max_loss * bar_width)
                bar = "#" * filled + "." * (bar_width - filled)
                lines.append(f"{r['method']:<22} [{bar}] {loss:.4f}")
            else:
                lines.append(f"{r['method']:<22} [{'.' * bar_width}] ---")
        lines.append("```\n")

    # Verdict
    lines.append("## Verdict\n")
    lines.append(f"- **Best method:** {METHODS[verdict_method]['label']}")
    lines.append(f"- **Reason:** {verdict_reason}")
    winner_r = next(r for r in results if r["method_key"] == verdict_method)
    lines.append(
        f"- **Accuracy:** {winner_r['final_accuracy']:.1%} | "
        f"**Cost:** {winner_r['cost_str']}"
    )
    lines.append("")

    # LLM recommendation
    lines.append("## LLM Recommendation\n")
    lines.append(f"> {llm_text}\n")

    # Budget
    if budget_text:
        lines.append(budget_text)

    content = "\n".join(lines)
    path = os.path.join(os.path.dirname(__file__), "part4_results.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------- User input ----------


def get_params() -> tuple[dict, str]:
    """Prompt user for parameters and method choice."""
    print("\n  Configure your fine-tuning simulation:\n")

    try:
        ds = input("  Dataset size (number of examples) [1000]: ").strip()
        dataset_size = int(ds) if ds else 1000
    except (ValueError, EOFError):
        dataset_size = 1000

    try:
        ms = input("  Model size (billions of parameters) [7]: ").strip()
        model_size = int(ms) if ms else 7
    except (ValueError, EOFError):
        model_size = 7

    try:
        ep = input("  Number of training epochs [3]: ").strip()
        epochs = int(ep) if ep else 3
    except (ValueError, EOFError):
        epochs = 3

    try:
        lr_str = input("  Learning rate [0.0001]: ").strip()
        learning_rate = float(lr_str) if lr_str else 0.0001
    except (ValueError, EOFError):
        learning_rate = 0.0001

    print("\n  Which method to simulate?")
    print("    1. full   — Full fine-tuning")
    print("    2. lora   — LoRA (PEFT)")
    print("    3. prompt — Prompt tuning")
    print("    4. all    — Compare all 3")
    try:
        choice = input("  Enter 1-4 [4]: ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "4"

    method_map = {"1": "full", "2": "lora", "3": "prompt", "4": "all"}
    method = method_map.get(choice, "all")

    return {
        "dataset_size": dataset_size,
        "model_size": model_size,
        "epochs": epochs,
        "learning_rate": learning_rate,
    }, method


# ---------- Main ----------


def main() -> None:
    print(f"Model: {MODEL}")
    banner("FINE-TUNING COMPARISON SIMULATOR")
    print("\n  Simulate 3 fine-tuning methods with realistic metrics.\n")
    for key, m in METHODS.items():
        print(
            f"    {m['label']:<22} updates={m['updates']:<6} gpu={m['gpu_memory']:<10} speed={m['speed']}"
        )

    params, method_choice = get_params()

    print(
        f"\n  Dataset: {params['dataset_size']:,} | Model: {params['model_size']}B | "
        f"Epochs: {params['epochs']} | LR: {params['learning_rate']}"
    )

    # Run simulations
    if method_choice == "all":
        method_keys = list(METHODS.keys())
    elif method_choice == "full":
        method_keys = ["full_finetuning"]
    elif method_choice == "lora":
        method_keys = ["lora_peft"]
    else:
        method_keys = ["prompt_tuning"]

    results = []
    total = len(method_keys)
    for i, key in enumerate(method_keys, 1):
        pct = i / total * 100
        bar_filled = round(pct / 5)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(
            f"  [{i}/{total}] {bar} {pct:.0f}%  Simulating {METHODS[key]['label']}..."
        )
        r = simulate_training(key, params)
        results.append(r)

    # Comparison table
    if len(results) > 1:
        print_comparison_table(results)
        print_all_loss_curves(results)

    # Verdict
    # Rule-based verdict
    dataset = params["dataset_size"]
    model_b = params["model_size"]
    if model_b >= 50 and dataset >= 5000:
        verdict_key = "full_finetuning"
        verdict_reason = (
            "Massive model + large dataset — full fine-tuning maximizes performance."
        )
    elif dataset <= 200:
        verdict_key = "prompt_tuning"
        verdict_reason = (
            "Small dataset — prompt tuning avoids overfitting and is cheapest."
        )
    elif model_b >= 20 and params["epochs"] >= 5:
        verdict_key = "full_finetuning"
        verdict_reason = (
            "Large model with enough epochs — full fine-tuning gets the best results."
        )
    else:
        verdict_key = "lora_peft"
        verdict_reason = "LoRA gives the best balance of performance, speed, and cost for most setups."

    print_verdict(results, params)

    # Single method loss curve
    if len(results) == 1:
        banner("LOSS CURVE")
        print_loss_curve(results[0]["losses"], results[0]["method"])

    # LLM recommendation
    banner("LLM RECOMMENDATION")
    print("  Asking the model for a recommendation...")
    llm_text = llm_recommendation(results)
    print(f"\n  {llm_text}")

    # Budget optimizer
    print()
    try:
        budget_str = input(
            "  Enter a dollar budget to optimize (or press Enter to skip) $: "
        ).strip()
        budget = float(budget_str) if budget_str else 0
    except (ValueError, EOFError):
        budget = 0

    budget_text = None
    if budget > 0:
        budget_optimizer(budget, params)
        # Capture budget output for results
        budget_lines = [
            f"\n## Budget Optimizer (${budget:.0f} budget)\n",
            f"{'Method':<22} {'Max Model':>10} {'Max Dataset':>12} {'Max Epochs':>11}",
            f"{'---':<22} {'---':>10} {'---':>12} {'---':>11}",
        ]
        for key, m in METHODS.items():
            hours = budget / m["cost_per_hour"]
            seconds = hours * 3600
            max_model = seconds / (
                params["dataset_size"] * params["epochs"] * m["time_multiplier"] * 0.002
            )
            max_model = max(1, min(200, max_model))
            max_dataset = seconds / (
                params["model_size"] * params["epochs"] * m["time_multiplier"] * 0.002
            )
            max_dataset = max(10, min(50000, max_dataset))
            max_epochs = seconds / (
                params["model_size"]
                * params["dataset_size"]
                * m["time_multiplier"]
                * 0.002
            )
            max_epochs = max(1, min(50, max_epochs))
            budget_lines.append(
                f"{m['label']:<22} {max_model:>8.0f}B {max_dataset:>10.0f} ex {max_epochs:>9.0f} ep"
            )
        budget_text = "\n".join(budget_lines)

    # Save results
    results_path = save_results(
        results, params, verdict_key, verdict_reason, llm_text, budget_text
    )
    print(f"\n  Results saved to: {results_path}")

    banner("DONE — Part 4 complete. Next: Part 5 (Retrieval-Augmented Generation)")


if __name__ == "__main__":
    main()
