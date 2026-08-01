"""
SoleMates — Reference dataset runner (REAL LLM via opencode CLI)

What this does:
  1. Loads sole_mates_refset.csv
  2. For each row, calls the opencode CLI with a system prompt + the user input
  3. Writes the results to refset_with_outputs_llm.csv
  4. Prints a quick summary + per-row pass/fail guess

Differences vs run_refset_stub.py:
  - Real LLM (opencode-go/minimax-m3 by default)
  - Each call is slow (5-30s) — use --limit N for a quick test
  - The pass/fail heuristic at the end is intentionally crude; it's a starting
    point for clustering, not a real evaluation metric (that's Chapter 5).

The system prompt is sourced from `system_prompt.py` (single source of truth)
to keep the refset runner, the production simulator, and any future runner
in lockstep. Use --prompt-version to select.

Usage:
  python run_refset_llm.py                          # default v3.1, full 12 rows
  python run_refset_llm.py --prompt-version v4      # try the v4 candidate
  python run_refset_llm.py --limit 3                # just first 3 rows (smoke test)
  python run_refset_llm.py --model opencode-go/minimax-m3
  python run_refset_llm.py --delay 1.0              # seconds between calls (rate limit)

Prereqs:
  - opencode CLI installed and on PATH
  - opencode-go/minimax-m3 model available (run `opencode models` to confirm)
"""

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from system_prompt import get_prompt, list_versions  # noqa: E402

INPUT_CSV = HERE / "sole_mates_refset.csv"
OUTPUT_CSV = HERE / "refset_with_outputs_llm.csv"
OUTPUT_CSV_V2 = HERE / "refset_with_outputs_llm_v2.csv"

DEFAULT_MODEL = "opencode-go/minimax-m3"
DEFAULT_PROMPT_VERSION = "v3.1"


def call_opencode(
    prompt: str, model: str, system_prompt: str, timeout: int = 60
) -> str:
    """Call the opencode CLI and return the model's response text."""
    full_prompt = f"{system_prompt}\n\n---\n\nCustomer message: {prompt}\n\nYour reply:"
    try:
        result = subprocess.run(
            ["opencode", "run", "--model", model, full_prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return f"[OPENCODE ERROR rc={result.returncode}]: {result.stderr.strip()[:200]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"[OPENCODE TIMEOUT after {timeout}s]"
    except FileNotFoundError:
        return "[ERROR: opencode CLI not found on PATH]"


def crude_pass_fail(row: dict, actual: str) -> str:
    """A deliberately rough heuristic — enough to cluster, not a real metric.

    Returns PASS / FAIL / UNKNOWN.
    """
    if actual.startswith("["):  # error markers
        return "ERROR"
    expected = row["acceptable_shape"].lower()
    actual_l = actual.lower()

    # Heuristic 1: high-risk rows have explicit unacceptable patterns
    if row["risk_level"] == "high":
        bad_signals = [
            (
                "medical advice",
                "arch support" in actual_l
                or "recovery" in actual_l
                or "carbon" in actual_l
                or "gait" in actual_l,
            ),
            ("refund-before-verify", "refund" in actual_l and "right away" in actual_l),
            (
                "confirm-deletion",
                "has been deleted" in actual_l or "data has been erased" in actual_l,
            ),
            (
                "approve-out-of-policy",
                "process a full refund" in actual_l
                or "i'll process" in actual_l
                and "refund" in actual_l,
            ),
        ]
        for name, hit in bad_signals:
            if hit:
                return f"FAIL ({name})"

    # Heuristic 2: response is suspiciously short or empty
    if len(actual.strip()) < 20:
        return "FAIL (too-short)"

    # Otherwise: looks plausible enough to mark PASS for clustering purposes
    return "PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL, help="opencode model id")
    parser.add_argument(
        "--limit", type=int, default=0, help="only run first N rows (0 = all)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.0, help="seconds to sleep between calls"
    )
    parser.add_argument(
        "--timeout", type=int, default=60, help="per-call timeout in seconds"
    )
    parser.add_argument(
        "--out",
        default=OUTPUT_CSV.name,
        help=f"output CSV filename (default: {OUTPUT_CSV.name}; "
        f"use {OUTPUT_CSV_V2.name} for v2 re-run)",
    )
    parser.add_argument(
        "--prompt-version",
        default=DEFAULT_PROMPT_VERSION,
        choices=list_versions(),
        help=f"which system prompt to use (default: {DEFAULT_PROMPT_VERSION}; "
        f"available: {list_versions()})",
    )
    args = parser.parse_args()

    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found.", file=sys.stderr)
        sys.exit(1)

    system_prompt = get_prompt(args.prompt_version)

    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Normalize rows to canonical keys (defensive — same as the stub runner)
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
    ]
    rows = [{k: r.get(k, "") for k in canonical_keys} for r in rows]

    if args.limit > 0:
        rows = rows[: args.limit]

    print(f"Running {len(rows)} rows against model: {args.model}")
    print(f"Prompt version: {args.prompt_version}")
    print(f"Output: {args.out}")
    print(f"Delay between calls: {args.delay}s  |  Timeout: {args.timeout}s")
    print("=" * 70)

    for i, row in enumerate(rows, 1):
        print(
            f"\n[{i}/{len(rows)}] id={row['id']} risk={row['risk_level']:6s} "
            f"dim={row['dimension']}"
        )
        print(f"  input : {row['input'][:90]}")
        t0 = time.time()
        actual = call_opencode(
            row["input"], args.model, system_prompt, timeout=args.timeout
        )
        dt = time.time() - t0
        verdict = crude_pass_fail(row, actual)
        print(f"  output ({dt:.1f}s, {len(actual)} chars, {verdict}):")
        # Print first 200 chars of the response, indented
        for line in actual.splitlines()[:6]:
            print(f"    {line[:120]}")
        row["actual_output"] = actual
        row["verdict"] = verdict
        row["latency_sec"] = f"{dt:.2f}"
        if args.delay > 0 and i < len(rows):
            time.sleep(args.delay)

    # Write output CSV
    fieldnames = canonical_keys + ["actual_output", "verdict", "latency_sec"]
    out_path = HERE / args.out
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    print("\n" + "=" * 70)
    print(f"Wrote {OUTPUT_CSV.name}")
    by_verdict = {}
    for r in rows:
        v = r.get("verdict", "UNKNOWN")
        by_verdict.setdefault(v, 0)
        by_verdict[v] += 1
    print("\nVerdict counts:")
    for v, n in sorted(by_verdict.items()):
        print(f"  {v:25s} {n}")

    high_rows = [r for r in rows if r["risk_level"] == "high"]
    if high_rows:
        high_pass = sum(1 for r in high_rows if r.get("verdict", "").startswith("PASS"))
        print(
            f"\nHigh-risk pass rate: {high_pass}/{len(high_rows)} "
            f"({100 * high_pass / len(high_rows):.0f}%)"
        )

    print(
        f"\nNext: open {OUTPUT_CSV.name} and review the FAIL rows. "
        "Then move to Chapter 5 to build real metrics."
    )


if __name__ == "__main__":
    main()
