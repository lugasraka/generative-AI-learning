# Refset Regression Gate — Deploy Checklist Rule

> **Status:** Active. Implemented as `pre_commit_check.py` in this folder.
> **Owner:** PM, SoleMates.
> **Effective:** v1 of the eval report (Ch 11 §8 improvement #0).

## The rule

**Any prompt change to the SoleMates support agent must pass the 12-row reference dataset regression check (12/12 on the high-risk rows) before it is merged.**

If the check fails, the prompt change does not ship. No exceptions.

## Why this rule exists

The v3.1 prompt is the **production baseline**. The 5 high-risk rows in `sole_mates_refset.csv` (rows 3, 4, 6, 7, 8) are the canary — if any of them regresses, that's a P0. Adding a new prompt rule (like the v4 IVR-opener fix) to lift the tone bar must not accidentally break the safety floor.

This is the cheapest possible insurance against the most expensive possible mistake: shipping a tone improvement that breaks a P0 row.

## How to run the check

From this folder (`chapter4_building_reference_datasets/`):

```
python pre_commit_check.py
```

This will:
1. Load `sole_mates_refset.csv` (12 rows).
2. For each row, run the LLM with the prompt version you specified (default `v3.1`).
3. Apply the `policy_accuracy` code metric (from `chapter5_building_evaluation_metrics/`) to every response.
4. Apply a manual regression check on the 5 high-risk rows for known-bad patterns.
5. Exit 0 if all 12 rows pass policy + the high-risk manual check; exit 1 otherwise.

To test a candidate prompt version (e.g. before merging the v4 change):

```
python pre_commit_check.py --prompt-version v4
```

## What "pass" means

A row **passes** the regression gate when:

1. `policy_accuracy` returns `pass=True` (no tripwire fires on the response).
2. The response is not empty and not an error marker (`[OPENCODE ERROR ...]`, `[OPENCODE TIMEOUT ...]`, etc.).
3. The response contains substantive content (>= 20 characters of actual text).

High-risk rows get an additional manual-pattern check (see `pre_commit_check.py` for the exact patterns). For example, row 7 (medical question) must NOT contain clinical recommendation language — even if `policy_accuracy` doesn't catch it, the manual check will.

## Where the gate sits in the deploy flow

```
Edit system_prompt.py (add v4 candidate)
        |
        v
Run: python pre_commit_check.py --prompt-version v4
        |
        +---> FAIL  -> fix the prompt, do NOT merge
        |
        +---> PASS  -> open PR
                            |
                            v
                     CI re-runs the same gate
                            |
                            +---> FAIL  -> block merge
                            |
                            +---> PASS  -> merge + deploy
```

## When to bypass the gate

There is **no bypass**. The rule is "no exceptions" by design. If the prompt is genuinely stuck (e.g. a new high-risk failure mode is uncovered that the refset doesn't test for), the response is to **add a row to the refset first**, then re-run the gate. The refset is a living document on purpose.

## What this gate is NOT

- **Not a substitute for the 100-row pilot** (Ch 6). The pilot validates the metric on production-distribution traffic; the refset gate only validates that the canary didn't break.
- **Not a substitute for the LLM judge** (Ch 5/7). The judge catches tone and escalation nuance; the gate only catches policy tripwires + a few manual high-risk patterns.
- **Not a substitute for human review.** A green gate means "safe to ship"; a red gate means "do not ship." It does not mean "the response is good."

## Source

This rule was added as Ch 11 §8 improvement #0 in `sole_mates_eval_report_v1.md`. Effort estimate: <1 day. Impact: prevents tone-regression risk on the v4 prompt change and every prompt change after it.
