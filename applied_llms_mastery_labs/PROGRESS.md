# Progress

Track your journey through the 12 parts. Check off as you go.

- [x] **Part 1** — LLM Foundations & Real-World Use Cases — `use_case_classifier.py` (10/10 rule-based + LLM agreements, custom mode ready)
- [x] **Part 2** — Domain & Task Adaptation — `adaptation_advisor.py` + `adaptation_advisor.html` (scoring + relaxation analysis, both CLI and browser versions)
- [x] **Part 3** — Prompting & Prompt Engineering — `prompt_engineering_lab.py` (4 strategies x 5 tasks, self-consistency check, ReAct + injection bonus)
- [x] **Part 4** — Fine-Tuning LLMs — `finetuning_comparison.py` + `finetuning_comparison.html` (3 methods simulated, budget optimizer, ASCII loss curves, interactive browser version)
- [x] **Part 5** — Retrieval-Augmented Generation — `rag_pipeline.py` (20 docs, BM25 retrieval, 4 test queries, agentic RAG with follow-up search)
- [ ] **Part 6** — Tools for LLM Apps — `tool_ecosystem.py`
- [ ] **Part 7** — LLM Evaluation — `eval_metrics.py`
- [ ] **Part 8** — Building LLM Apps — `llm_app_builder.py`
- [ ] **Part 9** — Advanced Features & LLMOps — `llm_ops_dashboard.py`
- [ ] **Part 10** — Challenges with LLMs — `llm_safety_testing.py`
- [ ] **Part 11** — Emerging Research Trends — `research_explorer.py`
- [ ] **Part 12** — Neural Network Foundations — `nn_playground.py`

## Personal notes

### Key takeaways
- **Keyword matching is surprisingly effective** for use-case classification — simple rules matched the LLM on all 10 test cases in Part 1.
- **RAG is the default winner** for most real-world constraints — low cost, fast deployment, no training data needed. Fine-tuning and pre-training only win with massive data + expert teams + long timelines.
- **Scoring matrices make trade-offs explicit** — the Part 2 relaxation analysis shows exactly which constraint change would flip the recommendation.

### Open items / things to revisit
- Part 2 relaxation analysis: test edge cases where budget=very high + data=massive to see pre-training win
- Part 1: add more ambiguous test cases to stress-test the rule-based classifier
