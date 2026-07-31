"""
SoleMates — Reference dataset runner (stubbed LLM version)

What this does:
  1. Loads sole_mates_refset.csv
  2. For each row, "calls" a stubbed LLM and gets a (fake) actual_output
  3. Writes the results to refset_with_outputs.csv
  4. Prints a quick summary

This is a VIBE-CODING SCAFFOLD. The stubbed LLM is a placeholder so you can
practice the clustering step (step 4 of the Ch 4 process) without an API key.
When you're ready to use a real LLM, replace the `stub_llm` function with a
real call (e.g. via opencode or an HTTP request).

Usage:
  python run_refset_stub.py
"""

import csv
import random
from pathlib import Path

HERE = Path(__file__).parent
INPUT_CSV = HERE / "sole_mates_refset.csv"
OUTPUT_CSV = HERE / "refset_with_outputs.csv"


def stub_llm(row: dict) -> str:
    """Return a plausible-looking (but fake) response for a given input.

    The responses are intentionally varied — some good, some bad — so the
    downstream clustering step has something to work with.
    """
    risk = row["risk_level"]
    dim = row["dimension"]
    text = row["input"].lower()

    # High-risk rows: ~50% chance of a failure mode
    if risk == "high":
        failure = random.random() < 0.5
    else:
        failure = random.random() < 0.15

    if failure:
        # Pick a failure mode that matches the row's unacceptable_failure column
        failure_mode = row["unacceptable_failure"]
        first_bad = failure_mode.split("/")[0].strip().split("(")[0].strip()
        if first_bad.startswith("Any medical advice"):
            return "I'd suggest looking for shoes with extra arch support and a cushioned sole. Recovery shoes with a slight heel-toe drop are usually best after ankle surgery."
        if first_bad.startswith("Refunding before verifying"):
            return "I'm so sorry that happened! I've refunded both charges right away. You should see the money back in 3-5 business days."
        if first_bad.startswith("Approving the refund"):
            return "I completely understand — that's really frustrating. I'll process a full refund for you right now. Sorry for the inconvenience!"
        if first_bad.startswith("Confirming deletion"):
            return "Your account has been deleted and all your data has been erased. You should receive a confirmation email within a few minutes."
        if first_bad.startswith("Hallucinating a spec"):
            return "Yes, the Trail Pro 3 has a full carbon fiber plate and is our most cushioned trail shoe. It's great for marathons and ultramarathons."
        if first_bad.startswith("Just order your usual size"):
            return "Wide feet and bunions can be tricky, but our shoes run true to size. Just order your usual size and they should work great for you!"
        if first_bad.startswith("Refusing a clearly valid return"):
            return "I'm sorry, but I can't process this return without more information. Can you send me photos of the shoes first?"
        return f"[STUB FAILURE: {first_bad}]"

    # Good response — vary the style
    return row["acceptable_shape"]


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found.")
        return

    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Clean up: drop any stray None keys (caused by mismatched quote escaping in
    # the source CSV) and make sure every row has the same keys.
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
    cleaned = []
    for row in rows:
        clean = {k: row.get(k, "") for k in canonical_keys}
        cleaned.append(clean)
    rows = cleaned

    print(f"Loaded {len(rows)} rows from {INPUT_CSV.name}")

    # Add actual_output column
    for row in rows:
        row["actual_output"] = stub_llm(row)

    # Write output CSV
    fieldnames = canonical_keys + ["actual_output"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT_CSV.name}")

    # Quick summary
    by_risk = {}
    for row in rows:
        r = row["risk_level"]
        by_risk.setdefault(r, 0)
        by_risk[r] += 1
    print("\nRows by risk level:")
    for r, n in sorted(by_risk.items()):
        print(f"  {r:8s} {n}")

    print(f"\nNext: open {OUTPUT_CSV.name} and cluster the failures by dimension.")


if __name__ == "__main__":
    main()
