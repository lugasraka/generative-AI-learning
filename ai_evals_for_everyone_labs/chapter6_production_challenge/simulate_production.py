"""
SoleMates — Production simulator

Runs a traffic CSV (from generate_traffic.py) through the SoleMates support
bot (opencode CLI with a configurable system prompt), then applies the
policy_accuracy code metric (Ch 5) to every response.

Output:
  - per-row CSV with actual_output, policy pass/fail, latency
  - live pass-rate counter as the run progresses
  - a summary at the end with per-intent pass rates and top failure modes

The system prompt is sourced from chapter4/system_prompt.py (single source
of truth) to keep this runner in lockstep with the refset runner. Use
--prompt-version to select.

Usage:
  python simulate_production.py --traffic traffic_pilot.csv --out production_pilot_results.csv
  python simulate_production.py --traffic traffic_1000.csv --out production_results.csv --delay 0.2
  python simulate_production.py --traffic traffic_pilot.csv --out v4_pilot.csv --prompt-version v4
"""

import argparse
import csv
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
CH4_DIR = HERE.parent / "chapter4_building_reference_datasets"
CH5_DIR = HERE.parent / "chapter5_building_evaluation_metrics"
sys.path.insert(0, str(CH4_DIR))
sys.path.insert(0, str(CH5_DIR))

from metric_policy_accuracy import check as check_policy, TRIPWIRE_PATTERNS  # noqa: E402
from system_prompt import get_prompt, list_versions  # noqa: E402

DEFAULT_MODEL = "opencode-go/minimax-m3"
DEFAULT_PROMPT_VERSION = "v3.1"


def call_opencode(
    prompt: str, model: str, system_prompt: str, timeout: int = 60
) -> tuple:
    """Call opencode and return (response_text, latency_seconds)."""
    full_prompt = f"{system_prompt}\n\n---\n\nCustomer message: {prompt}\n\nYour reply:"
    t0 = time.time()
    try:
        result = subprocess.run(
            ["opencode", "run", "--model", model, full_prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        dt = time.time() - t0
        if result.returncode != 0:
            return (
                f"[OPENCODE ERROR rc={result.returncode}]: {result.stderr.strip()[:200]}",
                dt,
            )
        return result.stdout.strip(), dt
    except subprocess.TimeoutExpired:
        return f"[OPENCODE TIMEOUT after {timeout}s]", time.time() - t0
    except FileNotFoundError:
        return "[ERROR: opencode CLI not found on PATH]", time.time() - t0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traffic", required=True, help="input traffic CSV")
    parser.add_argument("--out", required=True, help="output results CSV")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument(
        "--prompt-version",
        default=DEFAULT_PROMPT_VERSION,
        choices=list_versions(),
        help=f"which system prompt to use (default: {DEFAULT_PROMPT_VERSION}; "
        f"available: {list_versions()})",
    )
    args = parser.parse_args()

    traffic_path = HERE / args.traffic
    if not traffic_path.exists():
        print(f"ERROR: {traffic_path} not found.", file=sys.stderr)
        sys.exit(1)

    with traffic_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    system_prompt = get_prompt(args.prompt_version)

    print(
        f"Simulating {len(rows)} queries through {args.model} ({args.prompt_version} prompt)"
    )
    print(f"Output: {args.out}")
    print("=" * 70)

    out_path = HERE / args.out
    fieldnames = list(rows[0].keys()) + [
        "actual_output",
        "policy_pass",
        "policy_violations",
        "policy_reason",
        "latency_sec",
    ]
    out_f = out_path.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    writer.writeheader()

    pass_count = 0
    fail_count = 0
    error_count = 0
    latencies = []
    failures_by_intent = Counter()
    failures_by_violation = Counter()
    wall_start = time.time()

    for i, row in enumerate(rows, 1):
        # Show a one-line progress indicator
        print(
            f"\r[{i}/{len(rows)}] {row['intent']:18s} messy={row['messy_type'] or '-':12s} ",
            end="",
            flush=True,
        )
        actual, dt = call_opencode(
            row["input"], args.model, system_prompt, args.timeout
        )
        latencies.append(dt)

        # Apply policy metric
        pol = check_policy(row, actual)
        passed = pol["pass"]
        if passed:
            pass_count += 1
        else:
            fail_count += 1
            failures_by_intent[row["intent"]] += 1
            for cat, _ in pol["violations"]:
                failures_by_violation[cat] += 1

        if actual.startswith("["):
            error_count += 1

        # Write row
        row["actual_output"] = actual
        row["policy_pass"] = passed
        row["policy_violations"] = "; ".join(f"{c}={m}" for c, m in pol["violations"])
        row["policy_reason"] = pol["reason"]
        row["latency_sec"] = f"{dt:.2f}"
        writer.writerow(row)
        out_f.flush()

        if args.delay > 0 and i < len(rows):
            time.sleep(args.delay)

    out_f.close()
    wall_total = time.time() - wall_start

    # Live line completion
    print()

    # Summary
    print("=" * 70)
    print(
        f"Done. {len(rows)} queries in {wall_total:.0f}s ({wall_total / len(rows):.1f}s/query)"
    )
    print()
    print(
        f"Policy pass rate:  {pass_count}/{len(rows)} = {100 * pass_count / len(rows):.1f}%"
    )
    print(f"  PASS:  {pass_count}")
    print(f"  FAIL:  {fail_count}")
    print(f"  ERROR: {error_count}  (opencode/timeout/network issues)")
    if latencies:
        latencies_sorted = sorted(latencies)
        p50 = latencies_sorted[len(latencies_sorted) // 2]
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        print(
            f"\nLatency: p50={p50:.1f}s  p95={p95:.1f}s  mean={sum(latencies) / len(latencies):.1f}s"
        )

    # Pass rate by intent
    by_intent = {}
    for row in rows:
        # re-read from the results file? simpler: track in memory
        pass

    # Re-read the output to compute per-intent stats
    with out_path.open(newline="", encoding="utf-8") as f:
        results = list(csv.DictReader(f))
    by_intent_pass = {}
    by_intent_total = {}
    by_messy_pass = {}
    by_messy_total = {}
    by_risk_pass = {}
    by_risk_total = {}
    for r in results:
        i = r["intent"]
        m = r["messy_type"] or "clean"
        risk = r["risk_level"]
        by_intent_total[i] = by_intent_total.get(i, 0) + 1
        by_messy_total[m] = by_messy_total.get(m, 0) + 1
        by_risk_total[risk] = by_risk_total.get(risk, 0) + 1
        if r["policy_pass"] == "True":
            by_intent_pass[i] = by_intent_pass.get(i, 0) + 1
            by_messy_pass[m] = by_messy_pass.get(m, 0) + 1
            by_risk_pass[risk] = by_risk_pass.get(risk, 0) + 1

    print("\nPass rate by intent:")
    for intent in sorted(by_intent_total, key=lambda x: -by_intent_total[x]):
        t = by_intent_total[intent]
        p = by_intent_pass.get(intent, 0)
        print(f"  {intent:20s} {p}/{t} = {100 * p / t:.0f}%")

    print("\nPass rate by messiness:")
    for m in ["clean", "typo", "multi_intent", "off_script", "very_short", "very_long"]:
        t = by_messy_total.get(m, 0)
        if t == 0:
            continue
        p = by_messy_pass.get(m, 0)
        print(f"  {m:15s} {p}/{t} = {100 * p / t:.0f}%")

    print("\nPass rate by risk level:")
    for risk in ["low", "medium", "high"]:
        t = by_risk_total.get(risk, 0)
        if t == 0:
            continue
        p = by_risk_pass.get(risk, 0)
        print(f"  {risk:8s} {p}/{t} = {100 * p / t:.0f}%")

    if failures_by_violation:
        print("\nTop violation categories:")
        for cat, n in failures_by_violation.most_common():
            print(f"  {cat:25s} {n}")

    print(f"\nWrote {out_path.name}")
    print(
        f"Next: open {out_path.name} and review the FAIL rows. Then scale to 1,000 or move to Ch 7."
    )


if __name__ == "__main__":
    main()
