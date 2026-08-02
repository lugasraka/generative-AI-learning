# Progress

Track your journey through the 12 parts. Check off as you go.

- [x] **Part 1** — LLM Foundations & Real-World Use Cases — `use_case_classifier.py` (10/10 rule-based + LLM agreements, custom mode ready)
- [x] **Part 2** — Domain & Task Adaptation — `adaptation_advisor.py` + `adaptation_advisor.html` (scoring + relaxation analysis, both CLI and browser versions)
- [x] **Part 3** — Prompting & Prompt Engineering — `prompt_engineering_lab.py` (4 strategies x 5 tasks, self-consistency check, ReAct + injection bonus)
- [x] **Part 4** — Fine-Tuning LLMs — `finetuning_comparison.py` + `finetuning_comparison.html` (3 methods simulated, budget optimizer, ASCII loss curves, interactive browser version)
- [x] **Part 5** — Retrieval-Augmented Generation — `rag_pipeline.py` (20 docs, BM25 retrieval, 4 test queries, agentic RAG with follow-up search)
- [x] **Part 6** — Tools for LLM Apps — `tool_ecosystem.py` + `part6_results.md` (40-tool catalog, 4 scenarios, rule-based stack vs LLM agreement, mini orchestrator with prompt chaining + memory)
- [x] **Part 7** — LLM Evaluation — `eval_metrics.py` (10 samples, 6 metrics, optional LLM judge, rank correlation, review alerts, retrieval precision/recall)
- [x] **Part 8** — Building LLM Apps — `llm_app_builder.py` (GenAI topic, progressive Stages 1-5, Stage 6 bonus agent, offline fallbacks)
- [x] **Part 9** — Advanced Features & LLMOps — `llm_ops_dashboard.py` + `llm_ops_dashboard.html` (100 synthetic logs, percentile latency, cost/quality/error metrics, anomaly + drift + alert rules, 10-min trend buckets, CSV export, LLM recommendations, interactive browser dashboard via `--html`)
- [x] **Part 10** — Challenges with LLMs — `llm_safety_testing.py` (23 tests across 5 categories: hallucination, injection, brittleness, contradiction, refusal calibration; 22/23 passed)
- [x] **Part 11** — Emerging Research Trends — `research_explorer.py` + `research_explorer.html` (5 research areas, 20 subtopics, interactive CLI + browser, ELI5, compare mode, timeline, quiz, reading list)
- [x] **Part 12** — Neural Network Foundations — `nn_playground.py` + `nn_playground.html` (tokenization, scaled dot-product attention, positional encoding, transformer block, multi-head attention, BPE, interactive browser playground)

## Personal notes

### Key takeaways
- **Keyword matching is surprisingly effective** for use-case classification — simple rules matched the LLM on all 10 test cases in Part 1.
- **RAG is the default winner** for most real-world constraints — low cost, fast deployment, no training data needed. Fine-tuning and pre-training only win with massive data + expert teams + long timelines.
- **Scoring matrices make trade-offs explicit** — the Part 2 relaxation analysis shows exactly which constraint change would flip the recommendation.

- **A 4-layer tool stack can be auto-assembled with transparent scoring** — cost (30%), complexity (30%), and need-relevance (40%) pick sensible stacks (e.g., Supabase+LlamaIndex for a budget RAG bot, PyTorch+AWS for fine-tuning).
- **Rule-based vs LLM agreement depends on how sharp the constraints are** — with `deepseek-v4-flash` the LLM diverged (0/4) on the open-ended scenarios but matched the catalog exactly (4/4) on the production-monitoring one; free-form LLMs pick tools outside the catalog (vLLM, Langfuse) and combine several per slot, so exact-name agreement understates how close the underlying reasoning is.
- **Orchestration = classify → select → plan with shared memory** — feeding prior turns back into the next prompt is a simple, visible version of what LangChain/LlamaIndex automate.
- **Lexical metrics can reward a confident wrong answer** — Part 7's incorrect mountain answer scored well on overlap and relevance, while the LLM judge caught the contradiction.
- **Complexity should be earned incrementally** — Part 8 shows how prompting, chaining, RAG, memory, tools, and agents each add capability, coordination cost, and new failure modes.
- **Percentiles beat averages for latency** — Part 9's p95/p99 caught a slow tail that the mean (1008ms) hid, and fixed 10-minute error buckets pinpointed localized spikes the overall 14% rate blurred.
- **Hallucination is the hardest safety failure to catch** — Part 10 found the model passed 22/23 tests, but confidently fabricated a Nobel Prize winner on a question about a fictitious award; the failure is especially dangerous because the text reads fluently and sounds authoritative.
- **LLM research is converging on three fronts** — Part 11 maps the landscape: models get smaller but smarter (MoE, Mamba, RWKV), more multimodal, and more agentic; open-source (LLaMA, OLMo) is closing the gap with proprietary models.
- **Every modern LLM is built from the same foundation** — Part 12 walks through the actual math: tokenization, scaled dot-product attention, positional encoding, residual connections, layer normalization, and feed-forward layers. The Transformer architecture is surprisingly simple once you see each piece in isolation.

### Open items / things to revisit
- Part 2 relaxation analysis: test edge cases where budget=very high + data=massive to see pre-training win
- Part 1: add more ambiguous test cases to stress-test the rule-based classifier
- Part 6: add a fuzzy/semantic agreement scorer (e.g., substring/token overlap) to see if rule vs LLM stacks are closer than exact matching suggests
