# Part 1 — What Are AI Agents Anyway?

## Concept in 10 lines

- **Generative AI** understands and produces content. **Agentic AI** understands, generates, *and acts*.
- LLMs are stateless text predictors. Tools are what turn them into agents.
- An agent = LLM + Tools + Planning + Memory + State/Control.
- Agents are **engineering wrappers** around models — the intelligence still comes from the model.
- The big question is the **autonomy vs. control** tradeoff.
- Don't start with "let's build an agent." Start with "what problem am I solving?"
- Tools are the "hands." The LLM is the "brain."

## Vibe-coding challenge

**Build a "thinking vs. doing" demo.** Create a tiny CLI script that:

1. Without any tool: prompts an LLM (opencode CLI, or mock) with *"What's the weather in Tokyo right now?"* and shows that the LLM can only guess or refuse.
2. With a tool: same prompt, but the LLM can call a `get_weather(city)` function you wrote. Show that it now produces a real, structured answer.
3. Print both side-by-side so the difference is visceral.

> Bonus: extend `get_weather` with a second tool (`convert_currency(amount, from, to)`) and ask a multi-step question like *"If it's 30C in Tokyo, what's that in Fahrenheit, and how much is 10,000 JPY in USD?"*

### How to start

Tell me one of:
- *"Scaffold this for me in Python"*
- *"I want to do it in TypeScript"*
- *"Use opencode CLI as the LLM"*
- *"Walk me through it without code first"*
