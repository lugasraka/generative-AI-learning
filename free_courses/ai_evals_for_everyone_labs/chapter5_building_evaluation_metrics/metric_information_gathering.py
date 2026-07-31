"""
SoleMates — Code-based metric: information_gathering

What this checks:
  For each (row, actual_output) pair, did the bot ask for the right
  clarifying information *before* trying to resolve the issue?

Why this is code-based (and not just an LLM judge):
  Most "good" SoleMates responses follow a known pattern:
    1. Acknowledge
    2. Ask for missing info (order #, email, photos, etc.)
    3. Then resolve or escalate

  The set of "things we should ask for" is small, finite, and
  tied to the intent. We can check for it with pattern matching.

Limitations:
  - Doesn't catch *how* the bot asked (tone is a separate metric).
  - Doesn't catch *unnecessary* questions (over-asking). For that, you'd
    want an LLM judge.
  - Some intents don't need info-gathering (e.g. row 1 — order # was
    already provided). The metric returns "n/a" for those.

Usage:
  from metric_information_gathering import check
  result = check(row, actual_output)
"""

import re

# Per-intent: list of (pattern, label) for the things we expect the bot
# to ask for if the input is missing them. Order matters — the metric
# returns the FIRST one that fires.
INTENT_INFO_NEEDS = {
    # If we don't have an order # in the input, the bot should ask for one
    "order_tracking": [
        (r"\border\s*#?\s*(number|id)\b", "order_id"),
        (r"\b(confirm|provide).{0,30}\bemail\b", "email"),
    ],
    # Returns: if not given, ask for order # and reason
    "returns": [
        (r"\border\s*#?\s*(number|id)\b", "order_id"),
        (r"\b(why|reason|wrong|defect|damage)\b", "return_reason"),
    ],
    # Sizing: ask for foot length, prior brand, or use case
    "sizing": [
        (r"\b(foot length|measure|measurement|in cm|in inches)\b", "foot_length"),
        (r"\b(usual|normal|typically wear|prior brand|nike|adidas)\b", "prior_brand"),
        (
            r"\b(use case|what (do you|will you) (use|wear)|running|walking|hiking)\b",
            "use_case",
        ),
    ],
    # Product questions: usually no info needed
    "product_question": [],
    # Billing: ask for last 4 of card or order #
    "billing_dispute": [
        (r"\b(last 4|last four|card ending)\b", "card_last4"),
        (r"\border\s*#?\s*(number|id)\b", "order_id"),
    ],
}

# Map Ch 4 dimensions to the intent. Keeps the metric aligned with the refset.
DIMENSION_TO_INTENT = {
    "policy_accuracy": "policy_check",  # not info-gathering
    "information_gathering": "sizing",  # placeholder
    "escalation": "escalation_only",
    "tone": "tone_check",
    "policy_accuracy + information_gathering": "returns",
    "policy_accuracy + escalation + tone": "returns",
    "tone + information_gathering + escalation": "sizing",
    "policy_accuracy + tone": "product_question",
    "escalation + tone + information_gathering": "billing_dispute",
    "escalation + policy_accuracy": "escalation_only",
    "tone + escalation + policy_accuracy": "returns",
}


def get_intent(row: dict) -> str:
    """Best-effort mapping from refset row -> intent bucket."""
    dim = row.get("dimension", "")
    return DIMENSION_TO_INTENT.get(dim, "unknown")


def input_has_order_id(text: str) -> bool:
    return bool(re.search(r"#?SM-\d{4,}", text, flags=re.IGNORECASE))


def check(row: dict, actual: str) -> dict:
    """Return {pass, missing_info, reason, intent} for one (row, response)."""
    if not actual or actual.startswith("["):
        return {
            "pass": False,
            "missing_info": ["empty_response"],
            "reason": f"empty or error: {actual[:60]}",
            "intent": get_intent(row),
        }

    intent = get_intent(row)
    needs = INTENT_INFO_NEEDS.get(intent, [])
    actual_l = actual.lower()

    # If intent has no info-gathering requirement, this dimension is N/A.
    if not needs:
        return {
            "pass": True,
            "missing_info": [],
            "reason": f"intent '{intent}' has no info-gathering requirement",
            "intent": intent,
        }

    # Find which info-asks the bot made
    asked_for = []
    for pat, label in needs:
        if re.search(pat, actual_l, flags=re.IGNORECASE):
            asked_for.append(label)

    # Heuristic: if input already has an order # and the bot did NOT ask
    # for it again, that's still PASS for that info-need.
    had_order_id = input_has_order_id(row.get("input", ""))
    if (
        had_order_id
        and "order_id" in [n for _, n in needs]
        and "order_id" not in asked_for
    ):
        asked_for.append("order_id")  # already known from input

    required = [n for _, n in needs]
    missing = [n for n in required if n not in asked_for]

    if missing:
        return {
            "pass": False,
            "missing_info": missing,
            "reason": f"missing info-asks: {', '.join(missing)}",
            "intent": intent,
        }
    return {
        "pass": True,
        "missing_info": [],
        "reason": f"asked for {', '.join(asked_for) or 'nothing required'}",
        "intent": intent,
    }


if __name__ == "__main__":
    # Quick self-test
    samples = [
        (
            {
                "dimension": "policy_accuracy + information_gathering",
                "input": "hey where's my order?",
            },
            "Could you share your order number so I can look it up?",
        ),
        (
            {
                "dimension": "policy_accuracy + information_gathering",
                "input": "hey where's my order?",
            },
            "Your order is in transit.",
        ),  # didn't ask
        (
            {
                "dimension": "tone + information_gathering + escalation",
                "input": "I have wide feet and bunions",
            },
            "What's your foot length and what brand do you usually wear?",
        ),  # both
        (
            {
                "dimension": "policy_accuracy + tone",
                "input": "Are the Trail Pro 3s waterproof?",
            },
            "Yes, they're water-resistant.",
        ),  # no info needed
    ]
    for row, s in samples:
        r = check(row, s)
        marker = "OK " if r["pass"] else "FAIL"
        print(f"[{marker}] {r['intent']:20s} {r['reason']}")
