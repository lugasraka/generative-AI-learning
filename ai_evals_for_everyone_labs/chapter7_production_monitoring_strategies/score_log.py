"""
SoleMates — Log filter for production monitoring

score_log(row) returns (score: int 0-100, breakdown: dict) for one production
log row. The score tells the human review queue "how interesting is this row?"

The function combines 7 signals (6 explicit + 1 priority baseline) into a
single 0-100 score. Each signal fires independently and adds a weighted
contribution. The score is normalized so the max possible is ~100, even
though some rows could in theory hit all signals.

Signals (per the Ch 7 plan):

  Explicit signals (visible in the message text or metadata):
    competitor_mention  +30  - user comparing to a competitor brand
    legal_keywords      +40  - "lawyer", "sue", "chargeback", "fraud"
    medical_keywords    +25  - "surgery", "plantar", "doctor", etc.
    refund_amount       +25  - refund > $100

  Implicit signals (behavioral / metadata):
    sentiment           +20  - frustrated/angry keywords
    message_length      +15  - very long messages (>= 200 chars)
    retry_count         +25  - retried 2+ times

  Priority baseline (intent-based floor):
    billing             +30
    return_out_policy   +20
    everything else     +10

Usage:
  from score_log import score_log
  score, breakdown = score_log(row)
  # score is 0-100; breakdown is {signal: contribution, ...}

Threshold guidance:
  >= 60:  "must review" — top of the human queue
  30-59: "should review" — second tier
  <  30: "low priority" — sample 5% for spot-checks
"""

import re
from typing import Tuple

# Explicit signal patterns
COMPETITOR_PATTERN = re.compile(
    r"\b(nike|adidas|new balance|pegasus|ultraboost|fresh foam|reebok|puma|asics|birkenstock|crocs|vans|converse)\b",
    flags=re.IGNORECASE,
)
LEGAL_PATTERN = re.compile(
    r"\b(lawyer|lawyers|attorney|sue|suing|lawsuit|chargeback|small claims|legal action|fraud|fraudulent)\b",
    flags=re.IGNORECASE,
)
MEDICAL_PATTERN = re.compile(
    r"\b(surgery|surgical|plantar fasciitis|fasciitis|neuroma|orthopedic|orthotic|bunion|"
    r"podiatrist|physical therapy|pt|rehab|rehabilitation|post-?op|arthritis|tendon|tendonitis|"
    r"doctor|physician|chronic pain)\b",
    flags=re.IGNORECASE,
)
SENTIMENT_PATTERN = re.compile(
    r"\b(furious|ridiculous|terrible|awful|horrible|unacceptable|outrageous|disgusted|"
    r"frustrated|infuriated|livid|appalled|disappointed|angry|upset)\b",
    flags=re.IGNORECASE,
)

# Intent-based priority baseline
INTENT_PRIORITY = {
    "billing_dispute": 30,
    "return_out_policy": 20,
    "return_in_policy": 15,
    "sizing": 15,
    "tracking": 5,
    "product_question": 5,
    "medical": 25,
    "gdpr": 25,
    "competitor": 20,
}

# Weights for each signal
WEIGHTS = {
    "competitor_mention": 30,
    "legal_keywords": 40,
    "medical_keywords": 25,
    "refund_amount_high": 25,
    "sentiment": 20,
    "message_length": 15,
    "retry_count": 25,
    "priority_baseline": None,  # variable
}

# Normalize raw sum to 0-100. Max possible raw ~ 220 (all signals + priority).
MAX_RAW = 220


def score_log(row: dict) -> Tuple[int, dict]:
    """Score a single log row. Returns (normalized_score, breakdown_dict)."""
    text = (row.get("input") or "") + " " + (row.get("actual_output") or "")
    text_l = text.lower()

    breakdown = {}
    raw = 0

    # Explicit signals
    if COMPETITOR_PATTERN.search(text_l):
        breakdown["competitor_mention"] = WEIGHTS["competitor_mention"]
        raw += WEIGHTS["competitor_mention"]
    if LEGAL_PATTERN.search(text_l):
        breakdown["legal_keywords"] = WEIGHTS["legal_keywords"]
        raw += WEIGHTS["legal_keywords"]
    if MEDICAL_PATTERN.search(text_l):
        breakdown["medical_keywords"] = WEIGHTS["medical_keywords"]
        raw += WEIGHTS["medical_keywords"]
    try:
        refund = int(row.get("refund_amount_requested") or 0)
    except (ValueError, TypeError):
        refund = 0
    if refund >= 100:
        breakdown["refund_amount_high"] = WEIGHTS["refund_amount_high"]
        raw += WEIGHTS["refund_amount_high"]
    if SENTIMENT_PATTERN.search(text_l):
        breakdown["sentiment"] = WEIGHTS["sentiment"]
        raw += WEIGHTS["sentiment"]

    # Implicit signals
    if len(text) >= 200:
        breakdown["message_length"] = WEIGHTS["message_length"]
        raw += WEIGHTS["message_length"]
    try:
        retries = int(row.get("retry_count") or 0)
    except (ValueError, TypeError):
        retries = 0
    if retries >= 2:
        breakdown["retry_count"] = WEIGHTS["retry_count"]
        raw += WEIGHTS["retry_count"]

    # Priority baseline (intent-based floor)
    intent = row.get("intent", "")
    priority = INTENT_PRIORITY.get(intent, 10)
    breakdown["priority_baseline"] = priority
    raw += priority

    # Normalize to 0-100
    score = min(100, round(100 * raw / MAX_RAW))
    return score, breakdown


def review_tier(score: int) -> str:
    """Bucket a score into a review priority."""
    if score >= 60:
        return "must_review"
    if score >= 30:
        return "should_review"
    return "low_priority"


if __name__ == "__main__":
    # Quick self-test
    samples = [
        {
            "intent": "tracking",
            "input": "where's my order?",
            "actual_output": "It's on the way.",
            "retry_count": 0,
            "session_length_sec": 30,
            "refund_amount_requested": 0,
        },
        {
            "intent": "billing_dispute",
            "input": "I want my money back, this is fraud, I'll call my lawyer!",
            "actual_output": "Let me connect you with a teammate.",
            "retry_count": 3,
            "session_length_sec": 400,
            "refund_amount_requested": 250,
        },
        {
            "intent": "sizing",
            "input": "I have wide feet and bunions, what do you recommend?",
            "actual_output": "Try our extra-wide options.",
            "retry_count": 2,
            "session_length_sec": 300,
            "refund_amount_requested": 0,
        },
    ]
    print("Self-test:\n")
    for s in samples:
        score, breakdown = score_log(s)
        tier = review_tier(score)
        print(f"score={score:3d}  tier={tier:12s}  signals={list(breakdown.keys())}")
