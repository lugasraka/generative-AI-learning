"""
SoleMates — Ch 5 LLM judges on the top-20 from Ch 7

Takes the 20 highest-scoring rows from pilot_scored.csv and runs both
Ch 5 LLM judges (escalation + tone) on each. Produces a single report
showing:
  - The log filter's signal breakdown
  - The policy metric's verdict
  - The escalation judge's verdict
  - The tone judge's verdict (with sub-dimensions)
  - Any signal-metric divergence cases

This is the "what would a full Ch 5 + Ch 7 picture look like" view.

Usage:
  python run_judges_on_top20.py
  python run_judges_on_top20.py --top 10        # just top 10 (faster)
  python run_judges_on_top20.py --model opencode-go/minimax-m3
"""

import argparse
import csv
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
CH5_DIR = HERE.parent / "chapter5_building_evaluation_metrics"
sys.path.insert(0, str(CH5_DIR))
sys.path.insert(0, str(HERE))

from ai_evals_for_everyone_labs.chapter7_production_monitoring_strategies.score_log import score_log  # noqa: E402

INPUT_CSV = HERE / "pilot_scored.csv"
OUTPUT_CSV = HERE / "top20_judged.csv"

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
    out = {"verdict": "UNKNOWN", "should": "?", "did": "?", "ctx": "?", "reason": ""}
    for field, key in [
        ("SHOULD_ESCALATE", "should"),
        ("DID_ESCALATE", "did"),
        ("CONTEXT_ATTACHED", "ctx"),
    ]:
        m = re.search(rf"{field}:\s*(yes|no)", text, re.IGNORECASE)
        if m:
            out[key] = m.group(1).lower()
    m = re.search(r"VERDICT:\s*(ACCEPTABLE|NOT_ACCEPTABLE)", text, re.IGNORECASE)
    if m:
        out["verdict"] = m.group(1).upper()
    m = re.search(r"REASON:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["reason"] = m.group(1).strip()[:200]
    return out


def parse_tone(text: str) -> dict:
    out = {"subdims": {}, "verdict": "UNKNOWN", "reason": ""}
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
        "--top", type=int, default=20, help="how many top rows to judge"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()

    if not INPUT_CSV.exists():
        print(
            f"ERROR: {INPUT_CSV} not found. Run score_demo.py first.", file=sys.stderr
        )
        sys.exit(1)

    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Already sorted by score desc from score_demo
    top = rows[: args.top]
    print(f"Running Ch 5 LLM judges (escalation + tone) on top {len(top)} rows")
    print(f"  model: {args.model}")
    print(f"  2 judge calls per row = {2 * len(top)} total calls")
    print(f"  expected time: ~{2 * len(top) * 7 // 60} min")
    print("=" * 70)

    results = []
    for i, row in enumerate(top, 1):
        print(
            f"\n[{i}/{len(top)}] id={row['id']} score={int(row['score']):3d} "
            f"intent={row['intent']:18s} signals={row['signals_fired'] or '(priority)'}"
        )
        actual = row.get("actual_output", "")

        # Escalation judge
        t0 = time.time()
        esc_raw = call_judge(
            ESCALATION_PROMPT.format(input=row["input"], actual_output=actual),
            args.model,
            args.timeout,
        )
        esc = parse_escalation(esc_raw)
        esc["latency"] = f"{time.time() - t0:.1f}"
        print(
            f"  esc  : {esc['verdict']:14s} should={esc['should']:3s} "
            f"did={esc['did']:3s} ctx={esc['ctx']:3s} ({esc['latency']}s) "
            f"{esc['reason'][:80]}"
        )

        # Tone judge
        t0 = time.time()
        tone_raw = call_judge(
            TONE_PROMPT.format(input=row["input"], actual_output=actual),
            args.model,
            args.timeout,
        )
        tone = parse_tone(tone_raw)
        tone["latency"] = f"{time.time() - t0:.1f}"
        fails = [k for k, v in tone["subdims"].items() if v == "FAIL"]
        fail_str = f"fails={fails}" if fails else "all-PASS"
        print(
            f"  tone : {tone['verdict']:14s} {fail_str:40s} ({tone['latency']}s) "
            f"{tone['reason'][:80]}"
        )

        results.append(
            {
                **row,
                "esc_verdict": esc["verdict"],
                "esc_should": esc["should"],
                "esc_did": esc["did"],
                "esc_ctx": esc["ctx"],
                "esc_reason": esc["reason"],
                "tone_verdict": tone["verdict"],
                "tone_fails": ",".join(fails),
                "tone_reason": tone["reason"],
            }
        )

    # Write
    fieldnames = list(results[0].keys())
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    print(f"\nWrote {OUTPUT_CSV.name}")

    # Summary
    n = len(results)
    esc_acc = sum(1 for r in results if r["esc_verdict"] == "ACCEPTABLE")
    tone_pass = sum(1 for r in results if r["tone_verdict"] == "PASS")
    print(f"\nSummary on top {n}:")
    print(f"  escalation ACCEPTABLE: {esc_acc}/{n} = {100 * esc_acc / n:.0f}%")
    print(f"  tone PASS:             {tone_pass}/{n} = {100 * tone_pass / n:.0f}%")

    # Tone sub-dimension breakdown
    sub_counter = Counter()
    for r in results:
        for dim, verdict in [
            ("WARM", "PASS"),
            ("BRIEF", "PASS"),
            ("HONEST", "PASS"),
            ("CALM", "PASS"),
            ("NON_JUDGMENTAL", "PASS"),
        ]:
            # reparse subdims from tone_fails... actually we didn't store subdims individually
            pass
    # Just count from the per-row reason instead
    print("\nTone sub-dim FAIL counts (from the per-row runs):")
    fail_counter = Counter()
    for r in results:
        for f in r["tone_fails"].split(","):
            f = f.strip()
            if f:
                fail_counter[f] += 1
    for dim, n in fail_counter.most_common():
        print(f"  {dim:20s} {n}")

    # Signal-metric divergence: rows where judges say FAIL but log filter just says "interesting"
    print("\n" + "=" * 70)
    print("SIGNAL-METRIC DIVERGENCE (the full picture):")
    print("=" * 70)
    esc_fails = [r for r in results if r["esc_verdict"] != "ACCEPTABLE"]
    tone_fails = [r for r in results if r["tone_verdict"] != "PASS"]
    print(f"\nEscalation NOT_ACCEPTABLE: {len(esc_fails)} rows")
    for r in esc_fails:
        print(f"  id={r['id']:>3s} score={r['score']:>3d} {r['esc_reason'][:90]}")
    print(f"\nTone FAIL: {len(tone_fails)} rows")
    for r in tone_fails:
        fails = r["tone_fails"] or "(all-PASS reason captured elsewhere)"
        print(
            f"  id={r['id']:>3s} score={r['score']:>3d} fails={fails:30s} {r['tone_reason'][:80]}"
        )

    # What would the policy metric have caught? Already known: 0/20 (per Ch 7)
    pol_pass = sum(1 for r in results if r["policy_pass"] == "True")
    print(f"\nFor reference:")
    print(f"  policy metric PASS:    {pol_pass}/{n} (per Ch 6 fix)")
    print(f"  log filter flagged:    {n}/{n} (this is the top 20 by design)")


if __name__ == "__main__":
    main()
