# Progress

Track your journey through the 11 chapters. Check off as you go.

- [x] **Chapter 1** — WTH are AI Evals? — `sole_mates_ai_charter.md` v0.1 scaffolded (6 sections + bonus open questions)
- [x] **Chapter 2** — Model vs Product Evaluations — `sole_mates_model_choice.md` v0.1 (recommend Model B; 5 scenarios + adversarial 6th)
- [x] **Chapter 3** — The Evaluation Framework (Input / Expected / Actual) — `sole_mates_eval_table.md` v0.1 (8 rows, stakeholder tags + friction points)
- [x] **Chapter 4** — Building Reference Datasets — `sole_mates_refset.csv` (12 rows) + `sole_mates_refset_sidecar.md` + `run_refset_stub.py` + `run_refset_llm.py` + `refset_with_outputs_llm.csv` (minimax-m3: 12/12 = 100% on the real model, including all 5 high-risk rows)
- [x] **Chapter 5** — Implementing Evaluation Metrics — 2 code metrics (policy, info) + 2 LLM judges (escalation, tone) + runner + v1 + v2 analysis. **v2 result: escalation 33% → 83% via 3 prompt fixes, no model change**
- [x] **Chapter 6** — Production Challenges — 100-query pilot: v1 96% (4 false-+ on sizing), v2 100% after tightening `medical_advice` tripwire. Refset regression 12/12. 16/17 adversarial cases pass. Ready to scale to 1,000
- [x] **Chapter 7** — Production Monitoring Strategies — 7-signal `score_log()` + Ch 5 judges on top 20. v2→v3→v3.1 cycle: escalation 80%→100%→100%, tone 65%→50%→50%. v3.1 added structured 3-step warm-escalation rule; fixed WARM on escalation rows but revealed IVR-opener pattern on non-escalation rows. Latency 5.9s→7.6s→6.2s. Discovery loop working as designed
- [x] **Chapter 8** — The Complete Evaluation Process — `sole_mates_eval_run_v1.md` consolidated (1 exec summary + 7 steps + 3 next-quarter improvements with expected metric movement)
- [x] **Chapter 9** — Common Misconceptions — `misconception_audit.md` v0.1: all 12 misconceptions covered, 6 grounded in our work + 6 in hypothetical public artifacts, ranked by harm-to-SoleMates, direct tone
- [x] **Chapter 10** — Glossary of Terms — `eval_cheatsheet.md` v0.1: 5 use-most terms + 3 anti-patterns + 4-step model + 1-line "start simple" + 3 questions + 3 "still don't get" + 35-term glossary with 1-line SoleMates examples. Plus `make_one_pager.py` → `eval_cheatsheet_one_pager.pdf` (1 page, 4.1KB)
- [x] **Chapter 11** — Capstone: SoleMates Eval Report v1 — `sole_mates_eval_report_v1.md` (9 sections, ~3 pages, anchored on Ch6 v3.1 pilot 100% policy + Ch7 top-20 100% escalation / 50% tone, IVR-opener pattern captured in §7 discovery loop, v4 prompt + 1k-query scale + tone calibration queued for v2)
- [x] **Ch11 §8 #0 SHIPPED** — Refset regression gate: `chapter4_building_reference_datasets/pre_commit_check.py` + `REGRESSION_GATE.md`. Runs 12-row refset + 5 high-risk extra checks; exits 1 on fail. Stub-mode green for v3.1 + v4. 10/10 unit tests on the high-risk patterns.
- [x] **Ch11 §8 #1 SHIPPED AS v4.1 — TONE 50% → 75% (+25pp), ESCALATION 83% → 92% (+9pp), POLICY 100% UNCHANGED** — v4.1 in `chapter4_building_reference_datasets/system_prompt.py`. v4.1 = v3.1 + 3 surgical fixes: (a) restored "ask for account identifier on escalation" rule (fixes v4's row 8 GDPR regression), (b) shortened "When you are answering directly" block + added explicit escalation carve-out, (c) added "honest deferral is a PASS" line. Real LLM + judge re-run on 12-row refset: gate 12/12 + 5/5; `policy_accuracy` 100%; **tone 50% → 75% (target exceeded)**; **escalation 83% → 92% (target exceeded)**; high-risk escalation 5/5 (back from v4's 3/5). Latency ~12s/row (~2.2x v3.1, same as v4). v4.1 is the new production baseline. Also shipped: false-positive guards in `metric_policy_accuracy.find_real_violations` and `pre_commit_check.run_extra_checks` for the row 4 medical-escalation pattern. Analysis in `v4_1_results.md`. **Remaining work for §8 #2 (calibration round): 2 high-risk HONEST FAILs on row 6 (echoed customer's "duplicate" framing) and row 8 (too-confident on 24h GDPR) — queued.**

## Personal notes

### Key takeaways
<!-- Fill in as you go. What's the one thing each chapter drilled into your head? -->

### Open items / things to revisit
<!-- What did you skip? What broke? What do you want to redo? -->

### SoleMates artifacts tracker
<!-- List every file you've created across the 11 chapters. The capstone pulls from these. -->
