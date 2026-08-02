# Part 5 — Evaluating Agents

## Concept in 10 lines

- **Evaluate the whole system, not just the model.** A better model doesn't fix a broken harness.
- Agents fail in ways unit tests can't predict — evaluation is its own discipline.
- Modern agent eval combines: **task benchmarks**, **custom evals**, and **production observability**.
- **Utility:** does it complete the task, and how efficiently (success rate, cost, steps).
- **Reliability and robustness:** does it hold up under messy inputs and adversarial cases.
- **Safety and trustworthiness:** does it stay within guardrails and behave predictably.
- A single metric is never enough — score across multiple dimensions.
- Custom evals built around how *your* system breaks are more valuable than generic benchmarks.
- Production observability catches failures that pre-deployment testing misses.

## Vibe-coding challenge

**Build an agent evaluation harness.** Create a Python script that:

1. Define a simple agent (a function that takes a task and returns a result — use rule-based logic, no LLM).
2. Create 8+ test cases covering: normal tasks, edge cases, adversarial inputs, and safety-sensitive requests.
3. Build a 3-dimension scoring system:
   - **Utility:** did the agent complete the task? (0 or 1) + efficiency score (steps taken / optimal steps).
   - **Reliability:** does it handle edge cases without crashing? (pass/fail per edge case).
   - **Safety:** does it refuse or safely handle dangerous requests? (pass/fail per safety case).
4. Run all test cases, collect results, and output:
   - A per-test-case results table (task, utility, reliability, safety).
   - Aggregate scores per dimension.
   - An overall "agent grade" (A/B/C/D/F) based on weighted averages.
5. Save results to a JSON file.

> Bonus: add a "regression" mode — run the same tests twice and verify results are deterministic.

### How to start

Tell me one of:
- *"Python with a rule-based agent"*
- *"Use opencode CLI as the agent under test"*
- *"Show me the test case structure first"*
- *"Make it a reusable framework I can extend"*
