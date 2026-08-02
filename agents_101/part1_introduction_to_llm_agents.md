# Part 1: Introduction to LLM Agents

![llm_guide.png](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/img/llm_guide.png)

An LLM agent is a large language model given the ability to act, not just answer. The clearest way to think about it: **an agent is a model plus a harness.** The model is the reasoning core. The harness is everything you build around it so it can take real actions: tools, memory, and a loop that lets it try, observe the result, and try again until the task is done.

## A Practical Example

Imagine you're building an assistant that plans vacations. It can answer simple questions like "What's the weather in Paris next week?" from a single call. But a real request looks like "Plan a 10-day Europe trip next summer with historic landmarks, local food, and a $3000 budget." That needs planning, budgeting, and looking things up across many sources.

An agent handles it by:
- Using the model to **reason and plan**
- Calling **tools** to search flights, hotels, and attractions
- Keeping track of the budget and preferences in **memory** across many steps

The model is the brain, the harness is what lets it get the job done.

---

**Next:** [Part 2: What's Inside an Agent: The Harness](part2_whats_inside_an_agent.md)
