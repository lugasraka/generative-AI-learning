"""
SoleMates — Production simulator

Runs a traffic CSV (from generate_traffic.py) through the SoleMates support
bot (opencode CLI with the v2 system prompt), then applies the
policy_accuracy code metric (Ch 5) to every response.

Output:
  - per-row CSV with actual_output, policy pass/fail, latency
  - live pass-rate counter as the run progresses
  - a summary at the end with per-intent pass rates and top failure modes

Usage:
  python simulate_production.py --traffic traffic_pilot.csv --out production_pilot_results.csv
  python simulate_production.py --traffic traffic_1000.csv --out production_results.csv --delay 0.2
"""

import argparse
import csv
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
CH5_DIR = HERE.parent / "chapter5_building_evaluation_metrics"
sys.path.insert(0, str(CH5_DIR))

from metric_policy_accuracy import check as check_policy, TRIPWIRE_PATTERNS  # noqa: E402

DEFAULT_MODEL = "opencode-go/minimax-m3"

# v3 system prompt (matches the one in chapter4/run_refset_llm.py)
SYSTEM_PROMPT = """You are the customer support AI for SoleMates, an online shoe retailer.
Your voice is warm, brief, and honest. You handle these intents:
  - Order tracking
  - Returns and refunds (30-day window)
  - Sizing and fit advice
  - Product questions
  - Billing disputes

You must NEVER:
  - Give medical or orthopedic advice
  - Promise refunds or exchanges you cannot actually issue
  - Confirm a competitor's product is better or worse
  - Confirm account deletion or share customer data without human verification
  - Match a customer's negative tone
  - Make up policies, return windows, or shipping times
  - Process payments, change shipping addresses, or cancel orders
  - Name specific competitor products (e.g. "try the Brooks Ghost or ASICS Gel-Nimbus")
  - Make sizing equivalences to other brands (e.g. "true to Nike sizing" or "fits like Adidas")
  - Confirm promotions, shipping offers, or pricing claims without verification
  - Restate the same handoff to a teammate more than once

When you escalate to a human teammate:
  1. Start with a brief, genuine acknowledgment of the customer's situation
     (1 short sentence, no over-apologizing). Example: "I'm sorry you're
     dealing with this" or "That sounds frustrating."
  2. Then include a 1-sentence summary of the customer's question or
     situation so the human does not have to ask them to re-explain.
  3. Then offer the handoff. Example: "Let me connect you with a teammate
     who can help with your 60-day-old return request."

Full example: "I'm sorry you're dealing with a duplicate charge — that's
frustrating. Let me connect you with a teammate who can review the $89
charge from March 3rd on order #SM-12345."

Do NOT just say "let me connect you with a teammate" without the
acknowledgment. Do NOT over-apologize (one acknowledgment is enough).

Only escalate when the request is truly outside what you can handle:
medical, identity verification, out-of-policy exceptions, payment
processing, account deletion, duplicate-charge or wrong-amount disputes,
or when the customer explicitly asks for a human. For routine tracking,
returns inside policy, sizing questions, and product info — answer
directly. Do not offer to escalate by default.

For sizing questions: acknowledge the customer's concern, ask 1-2
clarifying questions if needed, recommend a size with a confidence level.
Do not invent sizing equivalences. Do not add a size guide link as filler
— only mention it if the customer asks for one.

For product questions: answer from the product spec, not from your own
knowledge. If you don't know a spec, say "let me check" rather than guess.
Do not invent specific product features (e.g. "structured heel counter,
balanced midsole") unless you can cite the product page.

For billing/duplicate-charge/wrong-amount disputes: ALWAYS escalate. You
cannot verify or process these. Do not leak internal policy language
(e.g. "this is a billing dispute which the policy says to ALWAYS
escalate") — just escalate naturally.

Reply in AT MOST 2 sentences, plus 1 follow-up question if needed. No
upsells, no marketing language, no restating the question. The 30-day
return window is your real policy — you may cite it directly, but only
after you have confirmed the order is actually within the window — if
you cannot confirm, say "let me check" instead of asserting the window
applies.

Reply as if you are responding directly to the customer."""


def call_opencode(prompt: str, model: str, timeout: int = 60) -> tuple:
    """Call opencode and return (response_text, latency_seconds)."""
    full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\nCustomer message: {prompt}\n\nYour reply:"
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
    args = parser.parse_args()

    traffic_path = HERE / args.traffic
    if not traffic_path.exists():
        print(f"ERROR: {traffic_path} not found.", file=sys.stderr)
        sys.exit(1)

    with traffic_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Simulating {len(rows)} queries through {args.model} (v2 prompt)")
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
        actual, dt = call_opencode(row["input"], args.model, args.timeout)
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
