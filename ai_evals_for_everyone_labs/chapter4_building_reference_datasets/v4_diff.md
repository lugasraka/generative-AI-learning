# v3.1 → v4 — Prompt Change Record

> **Source:** Ch 7 v3.1 results analysis (`v3_1_results_analysis.md` §"v3.1 → v4")
> **Promoted by:** Ch 11 §8 improvement #1 in `sole_mates_eval_report_v1.md`
> **Status:** v4 prompt defined. Not yet run end-to-end. Pending gate run + LLM judge re-evaluation.
> **Files touched:**
> - `chapter4_building_reference_datasets/system_prompt.py` (new shared module)
> - `chapter4_building_reference_datasets/run_refset_llm.py` (now uses shared module + `--prompt-version`)
> - `chapter6_production_challenge/simulate_production.py` (now uses shared module + `--prompt-version`)

---

## What changed (the diff)

v4 = v3.1 + **one new section** at the end of the system prompt, immediately before the closing "Reply as if you are responding directly to the customer." line.

### Added block (v4 only)

```
When you are answering directly (not escalating):
  - Open by acknowledging the SPECIFIC question the customer asked.
    Do NOT open with a generic "I'd love to help", "I can help with that",
    or "That's outside the window" — those read as IVR scripts.
  - Lead with the answer in sentence 1. The customer came for information;
    give it to them first, then offer the follow-up question.
  - Good example: "Great question about the Trail Pro 3's waterproofing —
    the spec sheet says water-resistant up to 5mm of rain, not fully
    waterproof. Want me to send the full spec?"
  - Bad example: "I'd love to help! The Trail Pro 3 is..." (greeting-first
    reads as saccharine and IVR-like.)
```

### Why this change

The v3.1 prompt introduced a structured 3-step warm-escalation template (acknowledge → summarize → handoff) to fix the cold-IVR escalations flagged in v3. The fix worked exactly where it was supposed to — escalation rows passed. But it surfaced a regression: on **non-escalation rows** (the 80% of traffic that doesn't escalate), the bot's default openers ("I'd love to help", "I can help with that", "That's outside...") now read as IVR/saccharine instead of warm.

The LLM judge flagged this on 3 rows of the v3.1 top-20 sample:

| id | v3.1 WARM reason (judge) |
|---|---|
| 28 | "Opens with a blunt 'That's outside...' which feels curt and IVR-like" |
| 37 | "'I'd love to help' is saccharine and the response deflects a simple product question rather than engaging warmly" |
| 94 | "The generic 'I can help with that' opener is IVR-like" |

The new v4 block addresses the same three rows by forbidding the generic openers and requiring the answer to lead.

---

## What did NOT change

- All v2/v3 rules are preserved verbatim:
  - 1-sentence context on escalation.
  - No over-escalation.
  - Brevity cap (2 sentences + 1 follow-up).
  - No competitor product names.
  - No sizing equivalences.
  - For billing disputes, ALWAYS escalate.
  - 30-day return window is the real policy.
- All v3.1 polish is preserved:
  - Structured 3-step warm-escalation (acknowledge → summarize → handoff).
  - "Do not over-apologize" caveat.
  - Do not add size-guide-link as filler.
  - Do not invent "30-day window" when the order can't be confirmed.
- The `Reply as if you are responding directly to the customer.` closer is preserved (now the closer to the v4 block).

---

## Expected metric movement

| Metric | v3.1 | v4 (predicted) | Notes |
|---|---|---|---|
| policy_accuracy (top 20) | 100% | 100% | The new block only affects opener style; no policy tripwires should fire. |
| escalation LLM judge (top 20) | 20/20 = 100% | 20/20 = 100% | The new block explicitly only applies to non-escalation rows. |
| tone LLM judge (top 20) | 10/20 = 50% | **~13/20 = 65%** | The 3 known WARM failures (id=28, 37, 94) should clear. Other failures (5 HONEST, 4 BRIEF, 1 NON_JUDGMENTAL) are not addressed by this change and remain. |

**The +15pp on tone is a prediction**, not a measurement. It needs to be re-validated by:
1. Re-running the 100-row pilot with `--prompt-version v4`.
2. Re-running the top-20 LLM judge on the v4 outputs.
3. Confirming the 3 WARM failures flipped to PASS and no new failures appeared.

---

## Risk: what could go wrong with v4

1. **The new rule may make responses feel too "pressured" to lead with the answer.** On sizing-with-empathy rows (row 4), leading with the size recommendation before the empathy could read as cold. The example in the rule is a product question (Trail Pro 3 waterproofing), not a sizing/empathy row. May need a carve-out: "For sizing questions that involve customer anxiety, lead with empathy, then the answer."
2. **The new rule may regress the warm-escalation rows.** v3.1 fixed the WARM issues on escalation rows; the new block says nothing about escalations, so the v3.1 escalation rules still apply. But the *position* of the new block in the prompt (before the "Reply as if you are responding directly" line) means it comes *after* the escalation block, which should be fine — the escalation block is unchanged. Still, this needs to be tested.
3. **The new rule may interact badly with the existing 2-sentence cap.** If the bot is forced to acknowledge the question + give the answer in 2 sentences, the response may end up curt on the rows that previously got 3 sentences (1 ack + 1 answer + 1 follow-up). The example in the rule shows 2 sentences (ack + answer) + 1 follow-up question, which is the same 3-utterance budget as v3.1, so this should be fine.

---

## How to validate v4

### Step 1 — Run the regression gate (5 min)
```
cd chapter4_building_reference_datasets
python pre_commit_check.py --prompt-version v4
```
Expected: 12/12 + 5/5 high-risk PASS. If any row fails, **do not proceed** — fix the prompt and re-run.

### Step 2 — Re-run the refset (5-10 min)
```
python run_refset_llm.py --prompt-version v4 --out refset_with_outputs_llm_v4.csv
```
Compare the v4 outputs to `refset_with_outputs_llm_v2.csv` (the v2/v3.1 baseline). Look for:
- New failures (any row that was PASS in v2 but FAIL in v4 is a regression).
- High-risk rows (3, 4, 6, 7, 8) must remain PASS.

### Step 3 — Re-run the 100-query pilot (10 min)
```
cd chapter6_production_challenge
python simulate_production.py --traffic traffic_pilot.csv --out production_pilot_results_v4.csv --prompt-version v4
```
Expected: 100/100 on `policy_accuracy` (same as v3.1). If it drops, investigate.

### Step 4 — Re-run the LLM judge on the top-20 (longer)
Re-apply the Ch 5 `escalation` + `tone` LLM judges to the v4 top-20 (re-using the Ch 7 `score_log` to pick the top 20). Expected: tone 50% → 65%, escalation 100% unchanged.

### Step 5 — Decision
- If gate PASS + refset clean + pilot 100% + tone 60%+: **promote v4 to production** (this becomes the new v3.1 for the next quarter's report).
- If gate PASS but tone didn't move: investigate which rows still fail; the rule may need sharpening.
- If gate FAIL on any row: revert to v3.1 and document the failure.

---

## Open questions for v5

If v4 ships successfully, the next discovery loop items are:
- Address the 5 persistent HONEST failures (Ch 9 calibration round, Ch 11 §8 improvement #2).
- Build the `handoff_completeness` metric for the sizing-retry divergence (Ch 11 §8 improvement #4).
- Scale to 1,000 queries to confirm the v4 baseline (Ch 11 §8 improvement #3).
