"""
SoleMates — Log filter demo

Scores the 100 Ch 6 pilot rows using score_log.py, then:
  1. Sorts by score (highest first)
  2. Prints the top 20 (the "must review" queue)
  3. Prints the score distribution
  4. Sanity-checks against the policy metric: are the top-scored rows
     different from the rows the policy metric would catch?
  5. Finds signal-metric divergence: rows the log filter flags as
     "must review" that the policy metric says are PASS. These are
     your blind spots.

Output:
  - pilot_scored.csv: per-row score + breakdown (input to Ch 8)
  - printed report to stdout

Usage:
  python score_demo.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from ai_evals_for_everyone_labs.chapter7_production_monitoring_strategies.score_log import score_log, review_tier  # noqa: E402

INPUT_CSV = HERE / "pilot_with_metadata.csv"
OUTPUT_CSV = HERE / "pilot_scored.csv"
TOP_N = 20


def main():
    if not INPUT_CSV.exists():
        print(
            f"ERROR: {INPUT_CSV} not found. Run extend_pilot_metadata.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Scoring {len(rows)} rows with score_log...")
    print("=" * 70)

    scored = []
    for row in rows:
        score, breakdown = score_log(row)
        row["score"] = score
        row["tier"] = review_tier(score)
        row["signals_fired"] = ",".join(
            sorted(k for k in breakdown if k != "priority_baseline")
        )
        scored.append((score, row))

    # Sort by score desc, then by risk for stability
    scored.sort(key=lambda x: (-x[0], x[1]["risk_level"]))

    # Write scored CSV
    fieldnames = list(rows[0].keys()) + ["score", "tier", "signals_fired"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for _, row in scored:
            w.writerow(row)
    print(f"Wrote {OUTPUT_CSV.name}")

    # Distribution
    by_tier = Counter(r["tier"] for _, r in scored)
    by_intent = Counter(r["intent"] for _, r in scored)
    scores = [s for s, _ in scored]
    print(f"\nScore distribution:")
    print(
        f"  min={min(scores)}  p50={scores[len(scores) // 2]}  "
        f"p90={scores[int(len(scores) * 0.9)]}  max={max(scores)}"
    )
    print(f"\nTier distribution:")
    for tier in ["must_review", "should_review", "low_priority"]:
        n = by_tier.get(tier, 0)
        print(f"  {tier:15s} {n:3d}  ({100 * n / len(scored):.0f}%)")

    # Top N
    print(f"\n{'=' * 70}")
    print(f"Top {TOP_N} by score (the human review queue):")
    print(f"{'=' * 70}")
    print(
        f"{'id':>4s} {'score':>5s} {'tier':14s} {'intent':18s} {'risk':6s} {'signals_fired'}"
    )
    for score, row in scored[:TOP_N]:
        sigs = row["signals_fired"] or "(priority only)"
        if len(sigs) > 50:
            sigs = sigs[:47] + "..."
        print(
            f"{row['id']:>4s} {score:>5d} {row['tier']:14s} {row['intent']:18s} "
            f"{row['risk_level']:6s} {sigs}"
        )

    # Intent distribution in top N
    print(f"\nTop-{TOP_N} intent distribution:")
    top_intents = Counter(r["intent"] for _, r in scored[:TOP_N])
    for intent, n in top_intents.most_common():
        print(f"  {intent:20s} {n}")

    # Sanity check: does the log filter catch what the policy metric catches?
    print(f"\n{'=' * 70}")
    print(f"SANITY CHECK: log filter vs policy metric")
    print(f"{'=' * 70}")
    policy_fails = [r for _, r in scored if r["policy_pass"] == "False"]
    print(f"Policy metric FAILs: {len(policy_fails)}")
    if policy_fails:
        for r in policy_fails:
            # find its score
            for s, sr in scored:
                if sr["id"] == r["id"]:
                    print(
                        f"  id={r['id']} intent={r['intent']:18s} "
                        f"log_filter_score={s}  signals={r['signals_fired'] or '(priority)'}"
                    )
                    break
    else:
        print(f"  (none — all 100 rows passed the policy metric after Ch 6 fix)")

    # Signal-metric divergence: top-20 by log filter, but policy metric says PASS
    print(f"\n{'=' * 70}")
    print(f"SIGNAL-METRIC DIVERGENCE (the blind spots)")
    print(f"{'=' * 70}")
    top20_ids = {r["id"] for _, r in scored[:TOP_N]}
    top20_policy_pass = [r for _, r in scored[:TOP_N] if r["policy_pass"] == "True"]
    print(f"Top {TOP_N} by log filter: {TOP_N} rows")
    print(f"  policy says PASS on: {len(top20_policy_pass)} of them")
    print(f"  policy says FAIL on: {TOP_N - len(top20_policy_pass)} of them")
    if top20_policy_pass:
        print(
            f"\n  Rows that the LOG FILTER flags as 'must review' but the POLICY METRIC says PASS:"
        )
        print(f"  (these are your potential blind spots — review manually)")
        print()
        for r in top20_policy_pass:
            print(
                f"    id={r['id']:>3s} score={r['score']:>3d} intent={r['intent']:18s} "
                f"signals={r['signals_fired'] or '(priority)'}"
            )
            print(f"      in: {(r.get('input') or '')[:90]}")

    # Inverse: rows the policy metric would fail that the log filter underweights
    # (none in this pilot, but useful framework)


if __name__ == "__main__":
    main()
