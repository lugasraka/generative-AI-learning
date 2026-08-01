# Progress

Track your journey through the 12 parts. Check off as you go.

- [x] **Part 1** — LLM Foundations & Real-World Use Cases — `use_case_classifier.py` (10/10 rule-based + LLM agreements, custom mode ready)
- [x] **Part 2** — Domain & Task Adaptation — `adaptation_advisor.py` + `adaptation_advisor.html` (scoring + relaxation analysis, both CLI and browser versions)
- [x] **Part 3** — Prompting & Prompt Engineering — `prompt_engineering_lab.py` (4 strategies x 5 tasks, self-consistency check, ReAct + injection bonus)
- [x] **Part 4** — Fine-Tuning LLMs — `finetuning_comparison.py` + `finetuning_comparison.html` (3 methods simulated, budget optimizer, ASCII loss curves, interactive browser version)
- [x] **Part 5** — Retrieval-Augmented Generation — `rag_pipeline.py` (20 docs, BM25 retrieval, 4 test queries, agentic RAG with follow-up search)
- [x] **Part 6** — Tools for LLM Apps — `tool_ecosystem.py` + `part6_results.md` (40-tool catalog, 4 scenarios, rule-based stack vs LLM agreement, mini orchestrator with prompt chaining + memory)
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

- **A 4-layer tool stack can be auto-assembled with transparent scoring** — cost (30%), complexity (30%), and need-relevance (40%) pick sensible stacks (e.g., Supabase+LlamaIndex for a budget RAG bot, PyTorch+AWS for fine-tuning).
- **Rule-based vs LLM agreement depends on how sharp the constraints are** — with `deepseek-v4-flash` the LLM diverged (0/4) on the open-ended scenarios but matched the catalog exactly (4/4) on the production-monitoring one; free-form LLMs pick tools outside the catalog (vLLM, Langfuse) and combine several per slot, so exact-name agreement understates how close the underlying reasoning is.
- **Orchestration = classify → select → plan with shared memory** — feeding prior turns back into the next prompt is a simple, visible version of what LangChain/LlamaIndex automate.

### Open items / things to revisit
- Part 2 relaxation analysis: test edge cases where budget=very high + data=massive to see pre-training win
- Part 1: add more ambiguous test cases to stress-test the rule-based classifier
- Part 6: add a fuzzy/semantic agreement scorer (e.g., substring/token overlap) to see if rule vs LLM stacks are closer than exact matching suggests
