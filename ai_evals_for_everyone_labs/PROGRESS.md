# Progress

Track your journey through the 11 chapters. Check off as you go.

- [x] **Chapter 1** — WTH are AI Evals? — `sole_mates_ai_charter.md` v0.1 scaffolded (6 sections + bonus open questions)
- [x] **Chapter 2** — Model vs Product Evaluations — `sole_mates_model_choice.md` v0.1 (recommend Model B; 5 scenarios + adversarial 6th)
- [x] **Chapter 3** — The Evaluation Framework (Input / Expected / Actual) — `sole_mates_eval_table.md` v0.1 (8 rows, stakeholder tags + friction points)
- [x] **Chapter 4** — Building Reference Datasets — `sole_mates_refset.csv` (12 rows) + `sole_mates_refset_sidecar.md` + `run_refset_stub.py` + `run_refset_llm.py` + `refset_with_outputs_llm.csv` (minimax-m3: 12/12 = 100% on the real model, including all 5 high-risk rows)
- [x] **Chapter 5** — Implementing Evaluation Metrics — 2 code metrics (policy, info) + 2 LLM judges (escalation, tone) + runner + v1 + v2 analysis. **v2 result: escalation 33% → 83% via 3 prompt fixes, no model change**
- [x] **Chapter 6** — Production Challenges — 100-query pilot: v1 96% (4 false-+ on sizing), v2 100% after tightening `medical_advice` tripwire. Refset regression 12/12. 16/17 adversarial cases pass. Ready to scale to 1,000
- [x] **Chapter 7** — Production Monitoring Strategies — 7-signal `score_log()` + Ch 5 judges on top 20. v2→v3→v3.1 cycle: escalation 80%→100%→100%, tone 65%→50%→50%. v3.1 added structured 3-step warm-escalation rule; fixed WARM on escalation rows but revealed IVR-opener pattern on non-escalation rows. Latency 5.9s→7.6s→6.2s. Discovery loop working as designed
- [ ] **Chapter 8** — The Complete Evaluation Process
- [ ] **Chapter 9** — Common Misconceptions
- [ ] **Chapter 10** — Glossary of Terms
- [ ] **Chapter 11** — Capstone: SoleMates Eval Report v1

## Personal notes

### Key takeaways
<!-- Fill in as you go. What's the one thing each chapter drilled into your head? -->

### Open items / things to revisit
<!-- What did you skip? What broke? What do you want to redo? -->

### SoleMates artifacts tracker
<!-- List every file you've created across the 11 chapters. The capstone pulls from these. -->
