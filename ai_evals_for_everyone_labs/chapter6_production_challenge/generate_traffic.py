"""
SoleMates — Production traffic generator

Generates a realistic mix of customer queries for the SoleMates support bot.
Intent mix follows the Ch 6 plan; 90% clean + 10% messy (5 messiness types).

Usage:
  python generate_traffic.py --n 100 --out traffic_pilot.csv
  python generate_traffic.py --n 1000 --out traffic_1000.csv
  python generate_traffic.py --n 100 --seed 42 --out traffic_pilot.csv

The generator is deterministic given --seed, so re-runs produce the same
traffic. This is important: it makes the simulation reproducible, which is
required for the Ch 8 eval-run process to be repeatable.
"""

import argparse
import csv
import random
import re
from pathlib import Path

HERE = Path(__file__).parent

# Intent mix: (intent, share, [messiness types to apply if messy], template pool)
# Messiness types: typo, multi_intent, off_script, very_short, very_long
INTENT_MIX = [
    # intent                share   messiness              templates
    (
        "tracking",
        0.40,
        ["typo"],
        [
            "hey where's my order? #SM-{oid}",
            "Can you check the status of order SM-{oid}?",
            "Hi, I want to know where my package is. Order #SM-{oid}",
            "order SM-{oid} - when will it arrive?",
            "tracking for {oid} please",
        ],
    ),
    (
        "return_in_policy",
        0.20,
        ["multi_intent"],
        [
            "I want to return these shoes, they're too small. Order #SM-{oid}",
            "I'd like to return order SM-{oid} - wrong color",
            "Can I return my order? It's SM-{oid}, unworn, 10 days old",
            "Need to return shoes from order SM-{oid}, the size is off",
            "returning order SM-{oid}",
        ],
    ),
    (
        "return_out_policy",
        0.05,
        [],
        [
            "I bought these 60 days ago. They're unworn, I just opened the box. I want a refund. This is ridiculous. Order #SM-{oid}",
            "order SM-{oid} - 45 days old, never wore them, want my money back",
            "Can I still return SM-{oid}? It's been like 50 days",
            "I want to return order SM-{oid} but I'm past the 30 day window, please help",
        ],
    ),
    (
        "sizing",
        0.13,
        ["very_long"],
        [
            "I have wide feet and bunions. I've tried 3 pairs of running shoes that hurt. I'm scared to order online again. What do you recommend?",
            "I'm usually a women's 9 in Nikes — what SoleMates size should I get?",
            "How do the Trail Pro 3 fit compared to my current running shoes? I have a narrow foot",
            "I'm between sizes for the Sky Walker. Should I size up or down?",
            "I have a high arch and my heel slips. Which cushioning model would work best?",
        ],
    ),
    (
        "billing_dispute",
        0.05,
        [],
        [
            "I see TWO charges from you guys on my statement from March 3rd. One for $89 and one for $89. This is fraud. I want my money back. Order #SM-{oid}",
            "I was charged $50 for shipping but my order SM-{oid} said free shipping",
            "I think I was double-billed. Order SM-{oid}. Can you check?",
            "I want a refund for order SM-{oid} - charged me the wrong amount",
        ],
    ),
    (
        "product_question",
        0.07,
        ["off_script"],
        [
            "Are the Trail Pro 3s waterproof? Can I run a marathon in them?",
            "What's the difference between the Trail Pro 3 and the Trail Pro 2?",
            "Do the Slip-On Classics run true to size?",
            "Are any of your shoes vegan?",
            "What's the stack height on the Trail Pro 3?",
        ],
    ),
]

# Out-of-scope intents (1% — covered by very_short messiness on tracking)
OUT_OF_SCOPE_TEMPLATES = [
    (
        "medical",
        [
            "I just had ankle surgery. Can I wear these for my recovery or will it mess up my gait?",
            "I have plantar fasciitis. Are your shoes good for that?",
            "I have a Morton's neuroma. What do you recommend?",
        ],
    ),
    (
        "gdpr",
        [
            "Delete my account and all my data. I want it done in 24 hours.",
            "I want to opt out of all marketing emails. Permanently.",
            "Can you delete all my data under GDPR?",
        ],
    ),
    (
        "competitor",
        [
            "How do your shoes compare to Nike Pegasus 41?",
            "Are your shoes better than Allbirds for daily wear?",
            "Why should I buy from you instead of Adidas?",
        ],
    ),
]

# Risk levels per intent (used by the simulator for cost decisions)
INTENT_RISK = {
    "tracking": "low",
    "return_in_policy": "medium",
    "return_out_policy": "high",
    "sizing": "high",
    "billing_dispute": "high",
    "product_question": "low",
    "medical": "high",
    "gdpr": "high",
    "competitor": "low",
}

# Dimension tags per intent (mirrors Ch 4)
INTENT_DIMENSION = {
    "tracking": "policy_accuracy + information_gathering",
    "return_in_policy": "policy_accuracy + information_gathering",
    "return_out_policy": "policy_accuracy + escalation + tone",
    "sizing": "tone + information_gathering + escalation",
    "billing_dispute": "escalation + tone + information_gathering",
    "product_question": "policy_accuracy + tone",
    "medical": "escalation + policy_accuracy",
    "gdpr": "escalation + policy_accuracy",
    "competitor": "policy_accuracy + tone",
}


def gen_order_id(rng: random.Random) -> str:
    return f"{rng.randint(10000, 99999)}"


def apply_typo(text: str, rng: random.Random) -> str:
    """Drop or swap 1-2 random characters in 1-2 random words."""
    words = text.split()
    if not words:
        return text
    for _ in range(rng.randint(1, 2)):
        idx = rng.randint(0, len(words) - 1)
        w = words[idx]
        if len(w) <= 3:
            continue
        op = rng.choice(["drop", "swap", "dup"])
        if op == "drop":
            pos = rng.randint(1, len(w) - 2)
            w = w[:pos] + w[pos + 1 :]
        elif op == "swap":
            pos = rng.randint(0, len(w) - 2)
            w = w[:pos] + w[pos + 1] + w[pos] + w[pos + 2 :]
        else:  # dup
            pos = rng.randint(0, len(w) - 1)
            w = w[:pos] + w[pos] + w[pos:]
        words[idx] = w
    return " ".join(words)


def apply_multi_intent(text: str, rng: random.Random) -> str:
    """Append a second ask from a different intent."""
    followups = [
        " also, do you have a discount code?",
        " and what about my other order SM-99999?",
        " also can you tell me where my package is?",
        " oh and I want to change the size before you ship",
    ]
    return text + rng.choice(followups)


def apply_off_script(text: str, rng: random.Random) -> str:
    """Add an off-script ask (something the bot shouldn't help with)."""
    additions = [
        " also, can you write me a poem about my shoes?",
        " btw what's your favorite color?",
        " also tell me a joke",
        " do you have a loyalty program?",
    ]
    return text + rng.choice(additions)


def apply_very_short(text: str, rng: random.Random) -> str:
    """Truncate to a 1-3 word fragment (simulating terse / typed-on-mobile)."""
    short = rng.choice(["help", "order??", "shoes broke", "refund?", "wrong item"])
    return short


def apply_very_long(text: str, rng: random.Random) -> str:
    """Add lots of context to a sizing question."""
    padding = " " + " ".join(
        [
            "I've been a customer for 5 years and I love your shoes but I keep having",
            "fit issues with the toebox being too narrow and the heel slipping when I walk",
            "long distances, my podiatrist recommended something with a wider forefoot but",
            "I also need arch support because I have flat feet and the arch support in your",
            "current models feels too aggressive after a full day of standing at work.",
        ]
    )
    return text + padding


MESSY_FNS = {
    "typo": apply_typo,
    "multi_intent": apply_multi_intent,
    "off_script": apply_off_script,
    "very_short": apply_very_short,
    "very_long": apply_very_long,
}


def gen_out_of_scope(rng: random.Random) -> tuple:
    """Pick a random out-of-scope intent + template."""
    intent, templates = rng.choice(OUT_OF_SCOPE_TEMPLATES)
    return intent, rng.choice(templates)


def generate(n: int, seed: int = 42) -> list:
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        # Decide intent from the weighted mix (excluding out-of-scope; we add those via very_short)
        intents = [t for t in INTENT_MIX]
        weights = [t[1] for t in INTENT_MIX]
        intent_name, _, allowed_messy, templates = rng.choices(
            intents, weights=weights, k=1
        )[0]

        # 10% chance of messiness
        is_messy = rng.random() < 0.10
        messy_type = ""
        if is_messy and allowed_messy:
            messy_type = rng.choice(allowed_messy)
        elif is_messy and not allowed_messy:
            # Force messiness by picking from a generic type
            messy_type = rng.choice(
                ["typo", "multi_intent", "off_script", "very_short", "very_long"]
            )

        # Special case: very_short on tracking produces an out-of-scope medical/GDPR/competitor query
        if messy_type == "very_short" and intent_name == "tracking":
            oos_intent, oos_text = gen_out_of_scope(rng)
            text = apply_very_short(oos_text, rng)
            final_intent = oos_intent
        else:
            text = rng.choice(templates)
            if "{oid}" in text:
                text = text.replace("{oid}", gen_order_id(rng))
            if messy_type:
                text = MESSY_FNS[messy_type](text, rng)
            final_intent = intent_name

        rows.append(
            {
                "id": str(i + 1),
                "intent": final_intent,
                "messy_type": messy_type,
                "risk_level": INTENT_RISK.get(final_intent, "low"),
                "dimension": INTENT_DIMENSION.get(final_intent, "unknown"),
                "input": text,
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n", type=int, required=True, help="number of queries to generate"
    )
    parser.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    parser.add_argument("--out", required=True, help="output CSV filename")
    args = parser.parse_args()

    rows = generate(args.n, args.seed)
    out_path = HERE / args.out
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Summary
    by_intent = {}
    by_messy = {}
    by_risk = {}
    for r in rows:
        by_intent[r["intent"]] = by_intent.get(r["intent"], 0) + 1
        if r["messy_type"]:
            by_messy[r["messy_type"]] = by_messy.get(r["messy_type"], 0) + 1
        by_risk[r["risk_level"]] = by_risk.get(r["risk_level"], 0) + 1

    print(f"Generated {len(rows)} queries -> {out_path.name}")
    print(f"\nIntent distribution:")
    for k, v in sorted(by_intent.items(), key=lambda x: -x[1]):
        print(f"  {k:20s} {v:3d}  ({100 * v / len(rows):.0f}%)")
    print(f"\nMessy type distribution (10% target):")
    total_messy = sum(by_messy.values())
    for k, v in sorted(by_messy.items(), key=lambda x: -x[1]):
        print(f"  {k:20s} {v:3d}  ({100 * v / len(rows):.0f}%)")
    print(
        f"  total messy:         {total_messy:3d}  ({100 * total_messy / len(rows):.0f}%)"
    )
    print(f"\nRisk level distribution:")
    for k in ["low", "medium", "high"]:
        v = by_risk.get(k, 0)
        print(f"  {k:8s} {v:3d}  ({100 * v / len(rows):.0f}%)")


if __name__ == "__main__":
    main()
