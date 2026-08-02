# Part 5: Evaluating Agents

Agents fail in ways unit tests can't predict, so evaluation is its own discipline. A useful principle: **evaluate the whole system, not just the model.** A better base model does not fix a broken harness, a missing tool, or context the agent never sees.

## Evaluation Approaches

Modern agent evaluation combines:

- **Task benchmarks** — for example tau-bench and similar multi-turn, tool-use suites
- **Custom evals** — built around how your own system breaks
- **Production observability** — to catch failures live

## Scoring Dimensions

Useful dimensions to score include:

- **Utility:** does it complete the task, and how efficiently (success rate, cost, steps).
- **Reliability and robustness:** does it hold up under messy inputs and adversarial cases.
- **Safety and trustworthiness:** does it stay within guardrails, avoid harmful actions, and behave predictably when given real-world autonomy.

## Further Reading

- For a full treatment, see the [AI Evals for Everyone](../free_courses/ai_evals_for_everyone/README.md) course.
- See [Securing Agentic AI Systems](../resources/securing_agentic_ai_systems.md) for what breaks once agents can act.

---

**Previous:** [Part 4: Agents in the Real World](part4_agents_in_the_real_world.md)
**Next:** [Part 6: Build Your Own Agent](part6_build_your_own_agent.md)
