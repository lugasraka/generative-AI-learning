# Part 2 — Domain & Task Adaptation

> Source: [week1_part2_domain_task_adaptation.md](../../Applied_LLMs_Mastery_2024/week1_part2_domain_task_adaptation.md)

## Concept in 10 lines

- General-purpose LLMs work okay for many tasks, but **domain-specific** needs (finance, healthcare, legal) require deeper specialization.
- There are **three adaptation methods**, each with different cost/effort/performance trade-offs:
  1. **Domain-Specific Pre-Training** — train a model from scratch on domain data. Best performance, highest cost (weeks-months, millions of dollars). Examples: BloombergGPT (finance), ESMFold (proteins).
  2. **Domain-Specific Fine-Tuning** — take a pre-trained model and fine-tune on domain data. Good performance, moderate cost (hours-days, hundreds of dollars). Examples: Alpaca, ChatDoctor.
  3. **RAG (Retrieval-Augmented Generation)** — no training needed. Retrieve relevant docs at query time and stuff them into the prompt. Lowest cost, fastest to deploy, but depends on retrieval quality.
- The decision depends on: **budget**, **dataset size**, **timeline**, **privacy requirements**, **performance needs**, and **team expertise**.
- RAG is the most common starting point in industry because it requires no training and can be updated by simply swapping documents.
- Fine-tuning shines when you need the model to adopt a specific format, tone, or reasoning pattern that can't be achieved through prompting alone.
- Pre-training only makes sense for very large organizations with unique domain data and the compute budget to match.
- **The key insight**: you don't always need the most expensive method. Start with RAG, evaluate, then escalate only if needed.

## Vibe-coding challenge

**Build an adaptation advisor.** Create a Python script called `adaptation_advisor.py` that:

1. Defines 3 adaptation methods with their properties:
   - `pre_training` — cost: "very high", time: "weeks-months", data_needed: "massive", performance: "highest", privacy: "full control"
   - `fine_tuning` — cost: "moderate", time: "hours-days", data_needed: "moderate", performance: "high", privacy: "good"
   - `rag` — cost: "low", time: "hours-days", data_needed: "documents only", performance: "good", privacy: "excellent (no training)"

2. Asks the user 6 questions via input prompts:
   - "What's your budget range?" (low / moderate / high / very high)
   - "How much domain-specific data do you have?" (none / small / moderate / massive)
   - "How quickly do you need this?" (today / this week / this month / no rush)
   - "How sensitive is the data?" (public / internal / confidential / regulated)
   - "What performance level do you need?" (good enough / high / highest possible)
   - "Does your team have ML expertise?" (no / basic / experienced / expert)

3. Implements a **scoring function** that weights each answer and scores all 3 methods. Each method gets a score from 0-100 based on how well it fits the user's constraints.

4. Prints a **recommendation table** showing all 3 methods with their scores, a visual bar (e.g., `[████████░░]`), and a one-line explanation of why it scored that way.

5. Sends the user's scenario to `opencode run -m <model>` asking: "Given these constraints, which approach would you recommend: pre-training, fine-tuning, or RAG? Explain in 2 sentences."

6. Prints both the **rule-based recommendation** and the **LLM recommendation** side by side.

> Bonus: add a second output — a "what if you relax one constraint?" analysis that shows how the recommendation changes if the user improves budget, gets more data, or extends the timeline.

### How to start

Tell me one of:
- *"Scaffold adaptation_advisor.py in Python"*
- *"Start with just the scoring logic, no LLM"*
- *"Use opencode CLI for the LLM recommendation"*
- *"Show me the decision matrix first before we code"*
