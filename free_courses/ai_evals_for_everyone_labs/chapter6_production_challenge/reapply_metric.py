"""
Re-apply the (possibly updated) policy_accuracy code metric to an existing
production results CSV. Use this when you've fixed the metric and want to
re-score the same LLM outputs without paying for another LLM run.

Usage:
  python reapply_metric.py --in production_pilot_results.csv --out production_pilot_results_v2.csv
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
CH5_DIR = HERE.parent / "chapter5_building_evaluation_metrics"
sys.path.insert(0, str(CH5_DIR))

from metric_policy_accuracy import check as check_policy  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True, help="input results CSV")
    parser.add_argument("--out", required=True, help="output results CSV")
    args = parser.parse_args()

    in_path = HERE / args.inp
    out_path = HERE / args.out
    if not in_path.exists():
        print(f"ERROR: {in_path} not found.", file=sys.stderr)
        sys.exit(1)

    with in_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Re-applying policy_accuracy metric to {len(rows)} rows")
    print(f"  in : {in_path.name}")
    print(f"  out: {out_path.name}")
    print("=" * 70)

    pass_count = 0
    fail_count = 0
    failures_by_intent = Counter()
    failures_by_violation = Counter()

    for row in rows:
        # Reconstruct the row dict the metric expects (it reads row['input'], row['risk_level'], etc.)
        # The actual_output is what we re-evaluate.
        actual = row.get("actual_output", "")
        pol = check_policy(row, actual)
        if pol["pass"]:
            pass_count += 1
            row["policy_pass"] = True
        else:
            fail_count += 1
            row["policy_pass"] = False
            failures_by_intent[row["intent"]] += 1
            for cat, _ in pol["violations"]:
                failures_by_violation[cat] += 1
        row["policy_violations"] = "; ".join(f"{c}={m}" for c, m in pol["violations"])
        row["policy_reason"] = pol["reason"]

    # Write out
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(
        f"\nRe-scored pass rate: {pass_count}/{len(rows)} = {100 * pass_count / len(rows):.1f}%"
    )
    print(f"  PASS: {pass_count}")
    print(f"  FAIL: {fail_count}")
    if failures_by_violation:
        print("\nFailure categories:")
        for cat, n in failures_by_violation.most_common():
            print(f"  {cat:25s} {n}")
    print(f"\nWrote {out_path.name}")


if __name__ == "__main__":
    main()
