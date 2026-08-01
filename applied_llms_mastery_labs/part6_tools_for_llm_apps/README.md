# Part 6 — Tools for LLM Apps

> Source: [week5_tools_for_LLM_apps.md](../../Applied_LLMs_Mastery_2024/week5_tools_for_LLM_apps.md)

## Concept in 10 lines

- Every LLM app (RAG, fine-tuned, or API-only) is built from the same 4 tool layers: **Input Processing**, **LLM Development**, **Application**, and **Output**.
- **Input Processing** tools load and transform data — ETL platforms (Databricks, Airflow), document loaders (Unstructured.io, LangChain loaders), and **vector databases** (Pinecone, Weaviate, Qdrant, Chroma, Faiss, pgvector).
- **LLM Development** tools cover the model itself (OpenAI API, Hugging Face, LLaMA), **orchestration** frameworks (LangChain, LlamaIndex), **compute/training** (PyTorch, TensorFlow, Anyscale, Fireworks), and **experimentation** (W&B, MLflow, Statsig).
- **Orchestration tools** automate prompt engineering, integrate external data, manage API calls, support prompt chaining and memory, and avoid vendor lock-in via model-agnostic designs.
- **Application tools** handle hosting (Replicate, Vercel, Streamlit, Steamship, AWS, Gradio) and **monitoring** (LangKit, Gantry, Helicone).
- **Output tools** manage post-output work: evaluation and prompt engineering (Humanloop, PromptLayer) and live performance monitoring (Honeyhive, Scale AI).
- LLM API apps rarely need raw compute; fine-tuning apps do. That distinction drives the whole tool choice.
- **Vector databases** are the input-layer backbone of RAG: store, compare, and retrieve embeddings at scale (cloud: Pinecone; open-source: Weaviate/Qdrant; local: Chroma/Faiss; Postgres: pgvector).
- **Experimentation/monitoring tools** matter most for fine-tuning and production — the LLM is a black box over an API, so you evaluate it, not train it.
- The "right" stack is a trade-off between **cost, complexity, and relevance** to your needs — which a scoring matrix can make explicit.

## Vibe-coding challenge

**Build a tool ecosystem recommender + mini orchestrator.** Create a Python script called `tool_ecosystem.py` that:

1. Defines a **catalog of 40 real tools** across the 4 categories. Each entry has `name`, `category`, `license`, `hosted`, `cost`, `complexity`, `best_for` tags, and a short description.

2. Implements a **scoring engine**:
   - `score_tool(tool, scenario)` — heuristic scoring on cost fit (30%), complexity fit (30%), and relevance to the scenario's needs (40%), with open-source preference adjustments and human-readable reasons.
   - `recommend_stack(scenario)` — assembles a 4-layer stack, one tool per category.

3. Tests against **4 scenarios**: a low-budget RAG chatbot, an ML team fine-tuning a model, a high-volume consumer semantic search, and an enterprise production LLM app with strict monitoring.

4. Implements an **LLM agreement check**:
   - `llm_recommend(scenario)` — prompts the model (via `opencode run`) for its own 4-tool stack as JSON.
   - `compare_stacks(...)` — computes per-category agreement and a match rate out of 4.

5. Implements a **mini orchestrator** (procedural, no classes):
   - A model-agnostic `ask_llm()` wrapper (the "avoid vendor lock-in" idea).
   - A 3-step prompt chain with **shared memory**: classify the need → select a tool → generate an implementation plan, feeding prior turns back into the next prompt.

6. For each scenario, prints: the rule-based stack (scores + reasons), the LLM stack, and the agreement. Then prints the orchestration transcript. Saves everything to `part6_results.md`.

> Bonus: run with `--skip-llm` to see the deterministic parts offline; flip a scenario's budget or expertise and watch the recommended stack change (relaxation-style analysis).

### How to start

Tell me one of:
- *"Scaffold tool_ecosystem.py in Python"*
- *"Start with just the catalog and scoring, skip the LLM agreement"*
- *"Use opencode CLI for the LLM calls"*
- *"I want to build it about [tool category] — help me write the tools first"*
