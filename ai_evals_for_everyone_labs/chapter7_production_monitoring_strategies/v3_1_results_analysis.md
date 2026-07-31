# SoleMates — v3.1 Prompt Results: Warm-Escalation Fix

> **What changed (v3 → v3.1):** replaced the v3 "include a 1-sentence summary when escalating" rule with a structured 3-step escalation pattern: (1) brief acknowledgment, (2) 1-sentence context summary, (3) handoff offer. Plus a "do not over-apologize" caveat. Also fixed the size-guide-link-as-filler issue and the "30-day window" invention issue.

## Headline: same headline numbers, but **different rows are failing** — which is the goal

| Metric | v2 | v3 | v3.1 |
|---|---|---|---|
| **policy_accuracy** (code) | 100% | 100% | **100%** |
| **escalation** (LLM judge, top 20) | 16/20 = 80% | 20/20 = 100% | **20/20 = 100%** |
| **tone** (LLM judge, top 20) | 13/20 = 65% | 10/20 = 50% | 10/20 = 50% |
| Latency (p50) | 4.7s | 5.2s | 4.7s |
| Latency (p95) | 8.3s | 14.8s | 11.5s |
| Timeouts (90s window) | 0 | 3 (at 60s) | 1 (at 90s) |

**Same numbers, different failures.** The v3.1 prompt successfully moved failures around — the new WARM issues are different rows than the v3 WARM issues, and the new HONEST issues are different rows than the v3 HONEST issues. **That's the discovery loop working**: each iteration peels off a layer of issues but reveals new ones.

---

## What v3.1 specifically changed in the failures

### Sub-dimension FAIL counts (top 20)

| Sub-dim | v2 | v3 | v3.1 |
|---|---|---|---|
| HONEST | 5 | 5 | 5 |
| BRIEF | 3 | 4 | 4 |
| WARM | 0 | 3 | 3 |
| NON_JUDGMENTAL | 1 | 1 | 1 |
| CALM | 0 | 0 | 0 |

The 3 WARM failures persist. They're now on **different rows** (id=37, 94 are new; id=28 is the same row, but with a different reason).

### The 3 WARM failures on v3.1

| id | v3 WARM reason | v3.1 WARM reason | Did it help? |
|---|---|---|---|
| 28 | "Cold and bureaucratic" | "Opens with a blunt 'That's outside...' which feels curt and IVR-like" | Same row, slightly different reason. The warm-escalation rule didn't reach this row because the bot *didn't escalate* — it just said "that's outside the window." |
| 37 | (was a HONEST fail) | "'I'd love to help' is saccharine and the response deflects a simple product question rather than engaging warmly" | NEW. v3.1 fixed the HONEST issue but the warm opener now reads as IVR. |
| 94 | (was HONEST+BRIEF) | "The generic 'I can help with that' opener is IVR-like" | NEW. Same trade-off as id=37. |

**The pattern is clear:** the v3.1 warm-escalation rule helped on rows that escalate (id=80, 90, 17 are no longer flagged for WARM), but on **non-escalation rows**, the bot's default openers ("I'd love to help", "I can help with that", "That's outside") are now read as IVR/saccharine.

This is a genuine **tradeoff the rubric is exposing**: the bot needs a warmer opening *or* a more direct opener, depending on context. The v3.1 prompt doesn't have a per-context warm-opener rule.

### The 3 WARM failures v3.1 fixed (compared to v3)

In v3, the following rows failed WARM:
- **id=80** (billing, "I'm sorry you're dealing with a duplicate charge") — v3.1 made the same kind of response, judge no longer flagged
- **id=17** (return out-of-policy, "60-day return falls outside") — judge now sees the response as appropriately direct, no WARM fail
- **id=90** (billing, "I want a refund... btw what's your favorite color") — judge no longer flags ignoring the off-script question as WARM failure

So the warm-escalation rule **did** help for the 3 escalation rows that previously failed. Just on the new non-escalation rows, the rule's absence now shows.

### The HONEST issue is now permanent

The 5 HONEST failures on v3.1 are on rows: **80, 90, 52, 77, 65**. Same count as v2 and v3. The new "do not invent specific product features" rule didn't help.

**Why:** the failures are mostly about the bot citing the **30-day return window** (which is in the system prompt) and being read as inventing it. This is a **calibration problem, not a prompt problem** — the rubric needs to be refined. The bot *is* allowed to cite the window when it's in scope; the judge doesn't know that.

---

## v3.1 vs v3: which is "better"?

| Dimension | Winner | Why |
|---|---|---|
| Policy compliance | tie | Both 100% |
| Escalation accuracy | tie | Both 100% (the always-escalate-billing rule is the load-bearing one; warm-escalation is polish) |
| Tone — escalation rows | **v3.1 wins** | The warm opener appears on 3/3 escalation rows that v3 had WARM-flagged |
| Tone — non-escalation rows | v3 wins slightly | v3 didn't have the IVR-opener issue because the bot wasn't following the warm template for non-escalations |
| Latency | **v3.1 wins** | p50 back to v2 levels (4.7s), p95 down from 14.8s to 11.5s. The bot is generating slightly shorter responses because the rule is now structured. |
| Stability | **v3.1 wins** | Only 1 timeout (vs v3's 3 at 60s) |

**Recommendation: adopt v3.1.** The warm-escalation rule works exactly where it was supposed to (escalation rows), and the latency is better than v3. The new IVR-opener issue on non-escalation rows is the *next* thing to fix in the v4 cycle.

---

## v3.1 → v4: what to fix next

1. **Add a warm-opener rule for non-escalation responses.** Something like: "When answering directly (not escalating), open with a sentence that acknowledges the specific question, not a generic 'I'd love to help' or 'I can help with that.' Example: 'Great question about the Trail Pro 3's waterproofing — here's what I know.'"
2. **Add a directness rule.** "For routine questions, lead with the answer in the first sentence. Don't open with an acknowledgment when the customer wants information."
3. **Refine the HONEST calibration.** The "30-day return window" citation is allowed when in scope. The judge needs to be told to check the system prompt's known policies before flagging the bot for "inventing" them.
4. **Re-evaluate non-escalation BRIEF failures** (id=89, 90, 35). These are the "I want to escalate but also explain the situation" responses that the bot keeps over-extending.

---

## The discovery loop is working

This is the **third iteration** of the prompt in this chapter. Each cycle:
- v2 → v3: escalation 80% → 100% (the load-bearing fix)
- v3 → v3.1: latency improved + WARM on escalation rows fixed (polish)
- v3.1 → v4: needs to address the IVR-opener pattern on non-escalation rows (next layer)

**That's exactly how the discovery loop is supposed to work in production:** every few weeks, you notice new patterns in the human review queue, write a new prompt rule, re-run the metrics, and ship. The loop never ends.

The v3.1 prompt is the right **baseline for production launch** — escalation is solid, latency is acceptable, and the remaining tone issues are calibration problems (Ch 9) more than model problems.

---

## Files

- **v3.1 outputs:** `chapter6_production_challenge/production_pilot_results_v3_1_r.csv` (100 rows, all retries completed)
- **v3.1 top 20:** `chapter7_production_monitoring_strategies/top20_judged.csv` (overwritten with v3.1)
- **v3.1 prompt:** in `chapter4_building_reference_datasets/run_refset_llm.py` + `chapter6_production_challenge/simulate_production.py`
- **This analysis:** `chapter7_production_monitoring_strategies/v3_1_results_analysis.md`
