"""
SoleMates — Metric Runner

Applies all 4 metrics to the LLM-generated outputs and produces:
  - per-row pass/fail for each metric
  - an overall pass rate
  - a code-vs-judge agreement report (the Ch 5 bonus)

Metrics:
  1. policy_accuracy        (code)   metric_policy_accuracy.py
  2. information_gathering  (code)   metric_information_gathering.py
  3. escalation             (LLM)    metric_llm_judge_escalation.md
  4. tone                   (LLM)    metric_llm_judge_tone.md

Usage:
  python metric_runner.py                             # full 12 rows, code only
  python metric_runner.py --with-judges               # also run LLM judges (~3-5 min)
  python metric_runner.py --with-judges --limit 3     # smoke test judges
  python metric_runner.py --model opencode-go/minimax-m3
"""

import argparse
import csv
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from metric_policy_accuracy import check as check_policy  # noqa: E402
from metric_information_gathering import check as check_info  # noqa: E402

LLM_INPUT_CSV = (
    HERE.parent / "chapter4_building_reference_datasets" / "refset_with_outputs_llm.csv"
)
LLM_INPUT_CSV_V2 = (
    HERE.parent
    / "chapter4_building_reference_datasets"
    / "refset_with_outputs_llm_v2.csv"
)
OUTPUT_CSV = HERE / "metric_results.csv"
OUTPUT_CSV_V2 = HERE / "metric_results_v2.csv"
AGREEMENT_CSV = HERE / "metric_agreement.csv"
AGREEMENT_CSV_V2 = HERE / "metric_agreement_v2.csv"

DEFAULT_MODEL = "opencode-go/minimax-m3"

ESCALATION_PROMPT = """You are an evaluation judge for SoleMates, a customer support AI.
Score a single (customer_message, bot_response) pair on the "escalation_accuracy" dimension.

Rules (use these to decide):
- SHOULD_ESCALATE = yes if: customer is angry AND issue is outside bot authority,
  OR customer asks for a human, OR customer mentions lawyer/sue/chargeback/fraud,
  OR request requires human-only authority (account deletion, payment, address change).
- SHOULD_ESCALATE = no if: routine tracking/return/sizing/product question the bot can handle.
- DID_ESCALATE = yes if the bot offers to connect with a teammate / human / agent.
- NOT ACCEPTABLE if: should-escalate-but-didn't, or shouldn't-escalate-but-did,
  or did-escalate-without-attaching-context.

Reply in EXACTLY this format (one field per line, no other text):

SHOULD_ESCALATE: yes|no
DID_ESCALATE: yes|no
CONTEXT_ATTACHED: yes|no
VERDICT: ACCEPTABLE|NOT_ACCEPTABLE
REASON: <one short sentence>

Customer message: {input}
Bot response: {actual_output}
"""

TONE_PROMPT = """You are an evaluation judge for SoleMates, a customer support AI.
Score a single (customer_message, bot_response) pair on the "tone" dimension.

Score each sub-dimension as PASS or FAIL:
- WARM: acknowledges the customer genuinely, not saccharine, not an IVR menu
- BRIEF: as short as possible, as long as necessary, no upsells, no repetition
- HONEST: says "I don't know" when true, doesn't invent policies/times/specs
- CALM: stays professional, doesn't mirror customer anger, doesn't over-apologize
- NON_JUDGMENTAL: treats customer with respect, doesn't ask them to re-explain

OVERALL = PASS only if ALL FIVE sub-dimensions are PASS.

Reply in EXACTLY this format (one field per line, no other text):

WARM: PASS|FAIL
BRIEF: PASS|FAIL
HONEST: PASS|FAIL
CALM: PASS|FAIL
NON_JUDGMENTAL: PASS|FAIL
OVERALL: PASS|FAIL
REASON: <one short sentence>

Customer message: {input}
Bot response: {actual_output}
"""


def call_judge(prompt: str, model: str, timeout: int = 90) -> str:
    """Call opencode CLI as the LLM judge."""
    try:
        result = subprocess.run(
            ["opencode", "run", "--model", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return (
                f"[JUDGE ERROR rc={result.returncode}]: {result.stderr.strip()[:200]}"
            )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[JUDGE TIMEOUT]"
    except FileNotFoundError:
        return "[ERROR: opencode CLI not found]"


def parse_escalation(text: str) -> dict:
    out = {"raw": text, "verdict": "UNKNOWN", "reason": ""}
    m = re.search(r"VERDICT:\s*(ACCEPTABLE|NOT_ACCEPTABLE)", text, re.IGNORECASE)
    if m:
        out["verdict"] = m.group(1).upper()
    m = re.search(r"REASON:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["reason"] = m.group(1).strip()[:200]
    return out


def parse_tone(text: str) -> dict:
    out = {"raw": text, "subdims": {}, "verdict": "UNKNOWN", "reason": ""}
    for dim in ["WARM", "BRIEF", "HONEST", "CALM", "NON_JUDGMENTAL"]:
        m = re.search(rf"{dim}:\s*(PASS|FAIL)", text, re.IGNORECASE)
        if m:
            out["subdims"][dim] = m.group(1).upper()
    m = re.search(r"OVERALL:\s*(PASS|FAIL)", text, re.IGNORECASE)
    if m:
        out["verdict"] = m.group(1).upper()
    m = re.search(r"REASON:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["reason"] = m.group(1).strip()[:200]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-judges", action="store_true", help="also run the LLM judges (slower)"
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument(
        "--input",
        default=LLM_INPUT_CSV.name,
        help=f"input CSV filename in chapter4 (default: {LLM_INPUT_CSV.name}; "
        f"use {LLM_INPUT_CSV_V2.name} for v2)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="output CSV filename in chapter5 (default: metric_results.csv "
        "or metric_results_v2.csv, mirroring input name)",
    )
    args = parser.parse_args()

    if not LLM_INPUT_CSV.exists():
        print(
            f"ERROR: {LLM_INPUT_CSV} not found. Run chapter 4 LLM runner first.",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = LLM_INPUT_CSV.parent / args.input
    if not input_path.exists():
        print(f"ERROR: {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    canonical_keys = [
        "id",
        "input",
        "context",
        "expected_behavior",
        "acceptable_shape",
        "unacceptable_failure",
        "risk_level",
        "dimension",
        "stakeholders",
        "actual_output",
        "verdict",
        "latency_sec",
    ]
    rows = [{k: r.get(k, "") for k in canonical_keys} for r in rows]
    if args.limit > 0:
        rows = rows[: args.limit]

    print(f"Running metric suite on {len(rows)} rows")
    if args.with_judges:
        print(f"  including LLM judges via {args.model} (~3-5 min)")
    print("=" * 70)

    results = []
    for i, row in enumerate(rows, 1):
        actual = row["actual_output"]
        print(f"\n[{i}/{len(rows)}] id={row['id']} risk={row['risk_level']:6s}")

        # 1) policy_accuracy (code)
        pol = check_policy(row, actual)
        print(f"  policy   : {'PASS' if pol['pass'] else 'FAIL'}  {pol['reason']}")

        # 2) information_gathering (code)
        info = check_info(row, actual)
        print(f"  info     : {'PASS' if info['pass'] else 'FAIL'}  {info['reason']}")

        # 3) escalation (LLM judge)
        esc = {"verdict": "SKIPPED", "reason": ""}
        if args.with_judges:
            t0 = time.time()
            raw = call_judge(
                ESCALATION_PROMPT.format(input=row["input"], actual_output=actual),
                args.model,
                args.timeout,
            )
            esc = parse_escalation(raw)
            esc["latency_sec"] = f"{time.time() - t0:.1f}"
            print(
                f"  esc judge: {esc['verdict']:14s} ({esc['latency_sec']}s)  {esc['reason']}"
            )

        # 4) tone (LLM judge)
        tone = {"verdict": "SKIPPED", "subdims": {}, "reason": ""}
        if args.with_judges:
            t0 = time.time()
            raw = call_judge(
                TONE_PROMPT.format(input=row["input"], actual_output=actual),
                args.model,
                args.timeout,
            )
            tone = parse_tone(raw)
            tone["latency_sec"] = f"{time.time() - t0:.1f}"
            print(
                f"  tone     : {tone['verdict']:14s} ({tone['latency_sec']}s)  "
                f"sub={tone['subdims']}  {tone['reason']}"
            )

        results.append(
            {
                "id": row["id"],
                "risk_level": row["risk_level"],
                "input": row["input"][:80],
                "policy_pass": pol["pass"],
                "policy_reason": pol["reason"],
                "info_pass": info["pass"],
                "info_reason": info["reason"],
                "escalation_verdict": esc["verdict"],
                "escalation_reason": esc.get("reason", ""),
                "tone_verdict": tone["verdict"],
                "tone_subdims": str(tone.get("subdims", {})),
                "tone_reason": tone.get("reason", ""),
            }
        )

    # Write per-row results
    fieldnames = list(results[0].keys())
    out_name = args.out
    if out_name is None:
        out_name = (
            "metric_results_v2.csv" if "v2" in args.input else "metric_results.csv"
        )
    out_path = HERE / out_name
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    print(f"\nWrote {out_name}")

    # Summary
    n = len(results)
    pol_pass = sum(1 for r in results if r["policy_pass"])
    info_pass = sum(1 for r in results if r["info_pass"])
    print(f"\nCode metric pass rates:")
    print(f"  policy_accuracy:        {pol_pass}/{n} = {100 * pol_pass / n:.0f}%")
    print(f"  information_gathering:  {info_pass}/{n} = {100 * info_pass / n:.0f}%")

    if args.with_judges:
        esc_pass = sum(1 for r in results if r["escalation_verdict"] == "ACCEPTABLE")
        tone_pass = sum(1 for r in results if r["tone_verdict"] == "PASS")
        print(f"\nLLM judge pass rates:")
        print(f"  escalation:             {esc_pass}/{n} = {100 * esc_pass / n:.0f}%")
        print(f"  tone:                   {tone_pass}/{n} = {100 * tone_pass / n:.0f}%")

        # High-risk breakdown
        high = [r for r in results if r["risk_level"] == "high"]
        if high:
            print(f"\nHigh-risk rows ({len(high)}):")
            for r in high:
                line = f"  id={r['id']}"
                for k in [
                    "policy_pass",
                    "info_pass",
                    "escalation_verdict",
                    "tone_verdict",
                ]:
                    v = "PASS" if r[k] is True else ("FAIL" if r[k] is False else r[k])
                    line += f"  {k[:8]}={v}"
                print(line)

        # Code vs judge agreement
        print(f"\nCode-vs-judge agreement (Bonus #3):")
        agreement = compute_agreement(results)
        agreement_name = (
            "metric_agreement_v2.csv" if "v2" in args.input else "metric_agreement.csv"
        )
        agreement_path = HERE / agreement_name
        with agreement_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(agreement[0].keys()))
            w.writeheader()
            w.writerows(agreement)
        print(f"  Wrote {agreement_name}")
        for row in agreement:
            print(
                f"  {row['comparison']:30s}  agree={row['agree_count']}/{row['total']}  "
                f"({100 * row['agree_count'] / row['total']:.0f}%)"
            )


def compute_agreement(results):
    """Compare code metrics to LLM judges on the rows that have both."""
    rows_with_judges = [r for r in results if r["escalation_verdict"] != "SKIPPED"]
    total = len(rows_with_judges)
    if total == 0:
        return []

    # escalation truth = policy_accuracy (code) merged with info_gathering
    # tone truth = information_gathering
    # This is a rough proxy; the real truth is human labels.
    comparisons = []

    # policy (code) vs tone (judge)
    agree = sum(
        1
        for r in rows_with_judges
        if (r["policy_pass"] is True) == (r["tone_verdict"] == "PASS")
    )
    comparisons.append(
        {
            "comparison": "policy (code) vs tone (judge)",
            "agree_count": agree,
            "total": total,
        }
    )

    # info (code) vs tone (judge)
    agree = sum(
        1
        for r in rows_with_judges
        if (r["info_pass"] is True) == (r["tone_verdict"] == "PASS")
    )
    comparisons.append(
        {
            "comparison": "info (code) vs tone (judge)",
            "agree_count": agree,
            "total": total,
        }
    )

    # escalation judge is a separate dimension; no direct code comparison
    # but we can compare the two judges to each other
    agree = sum(
        1
        for r in rows_with_judges
        if (r["escalation_verdict"] == "ACCEPTABLE") == (r["tone_verdict"] == "PASS")
    )
    comparisons.append(
        {
            "comparison": "escalation vs tone (judge-judge)",
            "agree_count": agree,
            "total": total,
        }
    )

    return comparisons


if __name__ == "__main__":
    main()
