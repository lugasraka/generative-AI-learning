"""
SoleMates — Extend the Ch 6 pilot CSV with 6 synthetic production metadata fields.

This simulates the kind of metadata a real production system would have on
each conversation: retry counts, session length, customer tier, etc.

Why this is "synthetic":
  We don't have real production logs yet. The pilot data has intent, risk,
  input, and output — but no operational metadata. To demonstrate a real
  log-filtering strategy (Ch 7), we need signals like "user retried 3 times"
  and "session ran 8 minutes." We synthesize these from the row's risk_level
  and intent, deterministically, so results are reproducible.

Seeding logic:
  retry_count:        high-risk rows skew higher (mean ~1.5); low ~0.3
  session_length_sec: sizing/billing skew long; tracking skews short
  customer_tier:      weighted random (30% new, 55% regular, 15% vip)
  refund_amount:      set for return/billing intents; 0 for others
  device_type:        weighted random (65% mobile, 35% desktop)
  first_time_customer: 25% true, biased by risk_level

Usage:
  python extend_pilot_metadata.py
"""

import argparse
import csv
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
PILOT_CSV = (
    HERE.parent / "chapter6_production_challenge" / "production_pilot_results_v2.csv"
)
OUTPUT_CSV = HERE / "pilot_with_metadata.csv"


def seed_retry(rng: random.Random, risk: str, messy: str) -> int:
    """High-risk + messy = more retries. Range 0-4."""
    base = {"low": 0.3, "medium": 0.8, "high": 1.5}.get(risk, 0.5)
    if messy:
        base += 0.7
    return min(4, max(0, int(round(rng.random() * 2 + base - 0.5))))


def seed_session_length(rng: random.Random, intent: str) -> int:
    """Sizing/billing tend to run long; tracking is quick."""
    base = {
        "tracking": 45,
        "return_in_policy": 90,
        "return_out_policy": 180,
        "sizing": 240,
        "billing_dispute": 300,
        "product_question": 60,
        "medical": 120,
        "gdpr": 60,
        "competitor": 90,
    }.get(intent, 90)
    return base + rng.randint(-30, 90)


def seed_customer_tier(rng: random.Random) -> str:
    return rng.choices(["new", "regular", "vip"], weights=[30, 55, 15], k=1)[0]


def seed_refund_amount(rng: random.Random, intent: str) -> int:
    if intent in ("return_in_policy", "return_out_policy"):
        return rng.randint(40, 200)
    if intent == "billing_dispute":
        return rng.randint(50, 300)
    return 0


def seed_device(rng: random.Random) -> str:
    return rng.choices(["mobile", "desktop"], weights=[65, 35], k=1)[0]


def seed_first_time(rng: random.Random, risk: str) -> bool:
    base = 0.25
    if risk == "high":
        base += 0.15
    return rng.random() < base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not PILOT_CSV.exists():
        print(f"ERROR: {PILOT_CSV} not found.", file=sys.stderr)
        sys.exit(1)

    with PILOT_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rng = random.Random(args.seed)

    for row in rows:
        row["retry_count"] = seed_retry(rng, row["risk_level"], row["messy_type"])
        row["session_length_sec"] = seed_session_length(rng, row["intent"])
        row["customer_tier"] = seed_customer_tier(rng)
        row["refund_amount_requested"] = seed_refund_amount(rng, row["intent"])
        row["device_type"] = seed_device(rng)
        row["first_time_customer"] = seed_first_time(rng, row["risk_level"])

    fieldnames = list(rows[0].keys())
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Quick distribution
    print(f"Extended {len(rows)} rows -> {OUTPUT_CSV.name}")
    by_tier = {}
    by_device = {}
    first_time = 0
    retries = []
    for r in rows:
        by_tier[r["customer_tier"]] = by_tier.get(r["customer_tier"], 0) + 1
        by_device[r["device_type"]] = by_device.get(r["device_type"], 0) + 1
        if r["first_time_customer"] in ("True", True):
            first_time += 1
        retries.append(int(r["retry_count"]))
    print(f"\nCustomer tier: {by_tier}")
    print(f"Device: {by_device}")
    print(
        f"First-time customers: {first_time}/{len(rows)} ({100 * first_time / len(rows):.0f}%)"
    )
    print(
        f"Retries: mean={sum(retries) / len(retries):.1f}  "
        f"max={max(retries)}  rows-with-retries={sum(1 for r in retries if r > 0)}"
    )


if __name__ == "__main__":
    main()
