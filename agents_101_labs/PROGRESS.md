# Progress

Track your journey through the 6 parts. Check off as you go.

- [x] **Part 1** — Introduction to LLM Agents — `agent_loop_demo.py`
- [x] **Part 2** — What's Inside the Harness — `mini_agent_harness.py`
- [x] **Part 3** — Multi-Agent Systems — `writer_critic_loop.py`
- [x] **Part 4** — Real-World Agents — `agent_archetype_classifier.py`
- [x] **Part 5** — Evaluating Agents — `agent_eval_harness.py`
- [x] **Part 6** — Build Your Own Agent — `capstone_agent.py` + `capstone_agent_llm.py`

## Part 1 → 6 Recap

### Part 1 — The agent loop (sense → decide → act → observe)
- An **LLM agent = model + harness** — the model reasons, the harness acts. Plain LLMs only answer; agents try, observe, and retry (`part1_intro_to_llm_agents/agent_loop_demo.py:73`).
- The vacation planner demo shows the loop is a `while` cycle: `sense()` reads state, `decide()` picks a tool, `act()` calls it, `observe()` mutates state (`agent_loop_demo.py:86-141`).
- A complex request (3 days, $1500, Tokyo) becomes **planning + budgeting + lookup** — not a single prompt.
- Core tension surfaced early: **autonomy vs. control** — how much freedom does the loop get before it wastes effort?

### Part 2 — The 4-component harness
- Decomposes into **Agent Core + Memory + Tools + Planning** (`mini_agent_harness.py:158-227`). A good harness makes a mediocre model useful.
- `Memory` class shows the split: `short_term` dict for current task, `long_term` list for past runs with `.append_long()` (`mini_agent_harness.py:92-117`).
- `decompose()` is rule-based keyword matching — no LLM yet, but the same shape an LLM planner would produce (`mini_agent_harness.py:123-135`).
- `reflect()` returns `(ok, msg)` and triggers **retry with adjusted parameters** (e.g. 10% flight discount) when a step fails (`mini_agent_harness.py:138-152`, retry at `197-202`).
- Insight: a 70-line `while` loop + 3 tools + 1 memory dict is enough to feel "agentic."

### Part 3 — Multi-agent patterns
- Two-agent **writer + critic** loop with max-rounds termination (`writer_critic_loop.py:152-187`). Flat/cooperative pattern — no manager, no hierarchy.
- `quality_score()` uses deterministic heuristics: filler-word count, presence of specifics/numbers, word count bounds (`writer_critic_loop.py:35-49`). This is a *non-LLM judge* — directly relevant to Part 5.
- The writer uses **feedback-conditioned regeneration**: if critic flags "specifics," the template prepends an example sentence (`writer_critic_loop.py:115-121`).
- Key tradeoffs: multi-agent buys **parallelism + specialization**, costs **non-determinism + latency + weird failure modes**. Don't start here — start with one agent, scale only when it empirically fails.
- ~70% of enterprise use cases work fine as a **single well-designed agent**.

### Part 4 — Real-world archetypes
- 4 archetypes, each with distinct harness requirements (`agent_archetype_classifier.py:17-46`):
  - **coding** — file_system, code_execution, terminal, git; sandbox + no_network_by_default
  - **computer_use** — browser_control, screenshot, mouse; rate_limiting + confirm_before_actions
  - **deep_research** — web_search, page_fetch, citation; source_verification
  - **enterprise_workflow** — api_calls, database, ticketing; human_in_loop + audit_logging
- `classify_task()` is keyword-signal counting — fast, deterministic, but fragile on novel phrasings (`agent_archetype_classifier.py:164-174`).
- **Hybrid detection** (gap ≤ 1) flags tasks that span archetypes and need a multi-agent architecture (`agent_archetype_classifier.py:267-277`).
- Insight: the right harness is determined by the *category of task*, not the model. Same LLM, completely different scaffolding.

### Part 5 — Evaluation discipline
- 3-dimension scoring: **utility (40%) + reliability (30%) + safety (30%)** weighted into a letter grade (`agent_eval_harness.py:254-281`).
- 10 test cases across 4 categories: `normal`, `edge`, `adversarial`, `safety` (`agent_eval_harness.py:91-176`).
- `score_utility()` combines **correctness × efficiency** (steps taken vs optimal steps) — a correct-but-verbose agent gets penalized (`agent_eval_harness.py:182-206`).
- Safety tests check the agent **refuses** dangerous prompts — refusal counts as a pass, not a failure (`agent_eval_harness.py:218-224`).
- Hard lesson: **evaluate the system, not the model**. A better model doesn't fix a broken harness, and unit tests can't predict agent failure modes.

### Part 6 — Capstone synthesis
- Wires **every prior concept** into one domain (task tracker): `task_store` + `priority_sorter` + `summary_generator` tools, `AgentMemory` with JSON persistence, decompose→execute→reflect loop (`capstone_agent.py:193-263`).
- `decompose_task()` is keyword-based like Part 2, but the output is **structured action dicts** (action + args), ready to dispatch (`capstone_agent.py:116-179`).
- `run_evaluation()` runs 3 goals with **fresh memory per test** to prevent state leakage (`capstone_agent.py:269-312`).
- `capstone_agent_llm.py` upgrades planner + reflector to real LLM calls while keeping the same shape — proves the harness is model-agnostic (`capstone_agent_llm.py:215-241`, `350-369`).
- **Real takeaway**: a 350-line script combining loop + memory + 3 tools + planning + reflection + eval is a complete, runnable agent. The "magic" was always in the harness, not the model.

## Personal notes

### Key takeaways
- **Part 1**: The agent loop is just a `while` cycle over `sense/decide/act/observe` — the value comes from iteration, not complexity.
- **Part 2**: 4 components (core, memory, tools, planning) is the minimal harness. Reflection + retry is what makes it agentic, not just procedural.
- **Part 3**: Multi-agent is a scaling lever, not a starting point. Specialization helps when one agent empirically fails.
- **Part 4**: Choose harness shape by task category — coding vs. research vs. browser vs. enterprise need very different scaffolding.
- **Part 5**: Score on utility × reliability × safety, never on a single metric. Build evals around how *your* system breaks.
- **Part 6**: The capstone is ~350 lines and runs end-to-end. The model is interchangeable; the harness is the product.

### Open items / things to revisit
- **Capstone LLM latency** — `capstone_agent_llm.py` originally hung because reflection fires on every step × every eval case (~45+ LLM calls). Added env-var knobs: `OPENCODE_REFLECT=0` skips reflect, `OPENCODE_EVAL_LIMIT=N` caps eval cases, `OPENCODE_TIMEOUT=30` per-call (`capstone_agent_llm.py:26-34`). Re-enable full suite with `OPENCODE_EVAL_LIMIT=3` once performance improves.
- **Hybrid archetype detection** in Part 4 is keyword-gap based — fragile on paraphrases. Consider swapping for embedding similarity or a small LLM classifier.
- **Multi-agent cost model** in Part 3 — the demo hides non-determinism behind max_rounds. Real systems need a token/step budget per agent.
- **Eval determinism** in Part 5 — rule-based agent is deterministic, but LLM agents won't be. Revisit when wiring evals to the capstone.
- **Memory persistence** in Part 6 — `AgentMemory` saves on every `append_long` (capstone_agent.py:113). For high-volume runs, batch or async writes.
