# Part 8 — Building LLM Apps Results

> **Topic:** `GenAI`  
> **Model:** `opencode-go/deepseek-v4-flash`  
> **Date:** 2026-08-02 10:12:45

## Progressive Comparison

| Stage | Added capability |
|---:|---|
| 1 | Prompt template plus one LLM call |
| 2 | Sequential prompt chaining |
| 3 | External knowledge through keyword retrieval |
| 4 | Conversation history and user context |
| 5 | External calculator/search tools |
| 6 | Planning, memory, bounded tool loop, and synthesis |

## Stage 1 — Simple Prompt

**Response:**

Here are 3 expert insights about generative AI:

1. **Evals are the bottleneck, not model quality.** The gap between top models is small and closing. The real differentiator is building robust evaluation suites (golden datasets, unit tests, regression harnesses) so you can reliably improve and ship systems. Without evals, you're flying blind — every prompt tweak is a gamble.

2. **Context engineering > prompt engineering.** As context windows grow, the winning skill is curating *what* goes into the context: retrieval, chunking, tool results, memory. Garbage in the context is worse than no context — it actively degrades output quality. The best systems treat context as a database, not a text field.

3. **Agents compound uncertainty.** Chaining multiple LLM calls multiplies error rates (e.g. 95% × 95% × 95% ≈ 86%). Add humans-in-the-loop checkpoints at high-cost/high-risk steps, and design agent architectures to fail *early and cheaply* rather than late and expensively.

## Stage 2 — Prompt Chaining

- Topic extracted: `Trust`
- Final answer: This question is about Trust. **3 Expert Insights on Trust**

1. **Trust is behavior, not just belief** (Stephen M.R. Covey, *The Speed of Trust*): Trust is a measurable economic accelerator — high trust lowers transaction costs and speeds execution, while low trust adds hidden "taxes" (micromanagement, rework, red tape).

2. **Trust is built in moments, lost in seconds** (Frances Frei, HBS): It breaks down into three variables — authenticity, logic, and empathy. When trust dips, ask which one you're failing on; usually it's empathy that slips first.

3. **Trust requires competence AND reliability** (Brené Brown): People trust those who are honest, consistent, and willing to show vulnerability — but competence alone isn't enough. It's the combination of "I can do this" + "I'll do what I said" that compounds into long-term trust.

## Stage 3 — RAG

Retrieved documents:
- `rag-pattern` (overlap=4)
- `evaluation-pattern` (overlap=2)
- `agent-pattern` (overlap=1)

**Answer:** GenAI uses retrieval-augmented generation (RAG): it retrieves relevant documents and adds them to the prompt, so answers can use external knowledge.

## Stage 4 — Memory

- **user:** My name is Alice and I work in GenAI.
- **user:** What are the best tools for data visualization?
- **assistant:** Alice, given your GenAI work, here are the strongest options:

- **Python (Matplotlib/Seaborn)** — default for evals, token usage, and loss curves; great for the charts in your lab scripts.
- **Plotly** — interactive dashboards for model performance monitoring.
- **Observable / D3** — for web-grade visualizations of embeddings, attention, etc.
- **Grafana** — production LLM ops (latency, cost, error rates).
- **LLM-native**: pandas + matplotlib still rule for offline analysis; for GenAI-specific UIs, **Langfuse** or **W&B** come with built-in tracing/evals views.

For quick ad-hoc work, Matplotlib/Seaborn is the pragmatic pick; if you tell me what you're visualizing (agent traces? eval results?), I can suggest a concrete setup.
- **user:** Can you summarize what we have discussed?
- **assistant:** Alice, you work in GenAI and asked for the best data visualization tools; I recommended Matplotlib/Seaborn for evals and loss curves, Plotly for interactive dashboards, plus Langfuse/W&B for LLM-specific tracing and evals views. I offered to tailor a concrete setup if you share what you're visualizing (e.g., agent traces or eval results).

## Stage 5 — Tools

- Query: What's 100/7 rounded to the nearest integer?
- Tool call: `{"tool": "calculator", "input": "round(100/7)"}`
- Observation: 14
- Answer: 14

## Stage 6 — Bonus Agent

- Query: I am preparing a GenAI workshop. Calculate 100/7 rounded to the nearest integer and suggest one useful GenAI retrieval technique.
- Plan: ['Calculate 100/7 = 14.29 and round to 14', 'Suggest a GenAI retrieval technique, e.g. Retrieval-Augmented Generation (RAG) with vector embeddings', 'Reply with the answer and the RAG suggestion']
- Step 1: `{"tool": "calculator", "input": "100/7 rounded to nearest integer"}` -> 14
- Step 2: `{"tool": "search", "input": "GenAI retrieval"}` -> Retrieval-augmented generation retrieves relevant documents and adds them to a prompt so answers can use external knowledge. | GenAI applications should combine automated metrics, LLM judges, and human spot checks to evaluate quality.
- Step 3: `{"tool": "search", "input": "GenAI retrieval"}` -> Retrieval-augmented generation retrieves relevant documents and adds them to a prompt so answers can use external knowledge. | GenAI applications should combine automated metrics, LLM judges, and human spot checks to evaluate quality.
- Final answer: 100/7 = 14.29 → rounds to **14**.

**RAG suggestion:** Retrieval-Augmented Generation (RAG) with vector embeddings — retrieve relevant documents and inject them into the prompt so the model grounds answers in external knowledge (reduces hallucination).

## Takeaway

Each stage adds capability and failure modes. The simplest stage that solves the task is usually preferable; agents are useful when the extra planning and tool coordination justify their complexity.
