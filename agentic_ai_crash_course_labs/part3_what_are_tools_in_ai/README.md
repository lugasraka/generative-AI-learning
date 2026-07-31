# Part 3 — What Are Tools in AI?

## Concept in 10 lines

- Tools = external capabilities the LLM can call (APIs, DBs, internal functions).
- They turn an LLM from "talks" to "acts."
- A tool is defined by: **name**, **description** (when to use it), **input params**, **output structure**.
- The LLM's text output is parsed/structured into tool calls, executed, and the **observation** is fed back.
- This loop — reason → act → observe → reason — *is* the agent.
- Modern LLMs (GPT-4o, Claude, Gemini) produce structured tool calls natively — no parser needed.
- Tools give you **risk control**: the agent can't do anything outside what's registered.

## Vibe-coding challenge

**Build a 2-tool agent from scratch (no frameworks).** Write a small script that:

1. Defines two tools by hand:
   - `add(a, b)` — adds numbers
   - `get_joke(topic)` — returns a hardcoded joke from a small dict
2. Has a "planner" that takes a user prompt, decides which tool to call (or no tool), and returns structured JSON like `{"tool": "add", "args": {"a": 2, "b": 3}}`.
3. Executes the tool and prints the result.
4. Test prompts:
   - *"What's 17 + 25?"* → should call `add`
   - *"Tell me a joke about cats"* → should call `get_joke`
   - *"What's the meaning of life?"* → should return a plain text answer with no tool call

> Bonus: add a third tool `get_weather(city)` (mocked) and a 2-step prompt like *"Add 7 and 8, then tell me a joke about the result."*

### How to start

Tell me one of:
- *"Scaffold it in Python"*
- *"Use TypeScript"*
- *"Use the opencode CLI as the LLM"*
- *"Show me the loop diagram first"*
