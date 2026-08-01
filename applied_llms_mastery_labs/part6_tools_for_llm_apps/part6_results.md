# Part 6 — Tool Ecosystem Results

> **Model:** `opencode-go/deepseek-v4-flash`  
> **Date:** 2026-08-02 00:10:40

## Catalog Stats

- Total tools: 40
- Input Processing: 11
- LLM Development: 13
- Application: 12
- Output / Evaluation: 4

## Scenario Recommendations

### RAG chatbot over internal docs

**Rule-based stack:**

- `[input]` **Supabase** (score=1.00, low cost, low complexity)
  - cost fits budget, complexity matches team expertise
- `[dev]` **LlamaIndex** (score=0.95, low cost, med complexity)
  - cost fits budget, relevant to needs (2 matching tags)
- `[app]` **LangKit** (score=0.75, low cost, med complexity)
  - cost fits budget, relevant to needs (1 matching tags)
- `[output]` **PromptLayer** (score=0.38, med cost, low complexity)
  - complexity matches team expertise, proprietary may clash with open-source preference

**LLM stack:**
- `input`: Unstructured
- `development`: LangChain + Chroma + sentence-transformers
- `application`: Ollama + Streamlit on a Docker VPS
- `output`: Langfuse

**Agreement:**

- `input` rule='Supabase' llm='Unstructured' → differ
- `dev` rule='LlamaIndex' llm='LangChain + Chroma + sentence-transformers' → differ
- `app` rule='LangKit' llm='Ollama + Streamlit on a Docker VPS' → differ
- `output` rule='PromptLayer' llm='Langfuse' → differ

**Match rate:** 0/4 categories

### Fine-tune a model for a specialized task

**Rule-based stack:**

- `[input]` **Databricks** (score=0.60, high cost, high complexity)
  - cost fits budget, complexity matches team expertise
- `[dev]` **PyTorch** (score=0.73, low cost, high complexity)
  - complexity matches team expertise, relevant to needs (2 matching tags)
- `[app]` **AWS** (score=0.68, high cost, med complexity)
  - cost fits budget, relevant to needs (1 matching tags)
- `[output]` **Honeyhive** (score=0.48, high cost, med complexity)
  - cost fits budget, hosted and supported

**LLM stack:**
- `input`: Amazon S3
- `development`: AWS SageMaker
- `application`: Weights & Biases
- `output`: SageMaker Endpoints

**Agreement:**

- `input` rule='Databricks' llm='Amazon S3' → differ
- `dev` rule='PyTorch' llm='AWS SageMaker' → differ
- `app` rule='AWS' llm='Weights & Biases' → differ
- `output` rule='Honeyhive' llm='SageMaker Endpoints' → differ

**Match rate:** 0/4 categories

### High-volume consumer semantic search

**Rule-based stack:**

- `[input]` **Supabase** (score=1.00, low cost, low complexity)
  - cost fits budget, relevant to needs (2 matching tags)
- `[dev]` **LlamaIndex** (score=0.90, low cost, med complexity)
  - cost fits budget, complexity matches team expertise
- `[app]` **LangKit** (score=0.70, low cost, med complexity)
  - cost fits budget, complexity matches team expertise
- `[output]` **PromptLayer** (score=0.29, med cost, low complexity)
  - proprietary may clash with open-source preference

**LLM stack:**
- `input`: BGE-M3
- `development`: FastAPI
- `application`: Qdrant
- `output`: vLLM

**Agreement:**

- `input` rule='Supabase' llm='BGE-M3' → differ
- `dev` rule='LlamaIndex' llm='FastAPI' → differ
- `app` rule='LangKit' llm='Qdrant' → differ
- `output` rule='PromptLayer' llm='vLLM' → differ

**Match rate:** 0/4 categories

### Production LLM app with strict monitoring

**Rule-based stack:**

- `[input]` **Pinecone** (score=0.51, high cost, low complexity)
  - cost fits budget, hosted and supported
- `[dev]` **Statsig** (score=0.80, high cost, med complexity)
  - cost fits budget, complexity matches team expertise
- `[app]` **Gantry** (score=1.00, high cost, med complexity)
  - cost fits budget, complexity matches team expertise
- `[output]` **Scale AI** (score=1.00, high cost, med complexity)
  - cost fits budget, complexity matches team expertise

**LLM stack:**
- `input`: Pinecone
- `development`: Statsig
- `application`: Gantry
- `output`: Scale AI

**Agreement:**

- `input` rule='Pinecone' llm='Pinecone' → agree
- `dev` rule='Statsig' llm='Statsig' → agree
- `app` rule='Gantry' llm='Gantry' → agree
- `output` rule='Scale AI' llm='Scale AI' → agree

**Match rate:** 4/4 categories

## Orchestration Demo (Prompt Chaining + Memory)

### Step 1: Classify need

```
You are an LLM app orchestrator. Classify the user request into exactly one of: "input", "development", "application", "output". Reply with just that word.

USER REQUEST: I want to summarize our quarterly sales report into an email and send it to the team.
```

**Output:** output

### Step 2: Select tool

**Output:** Humanloop

### Step 3: Generate plan

```
You are an LLM app orchestrator. Using the classified need and selected tool below, outline a 3-step implementation plan.

MEMORY (prior turns):
1. Classified need: "output" (Output / Evaluation)
2. Selected tool: Humanloop

ORIGINAL USER REQUEST: I want to summarize our quarterly sales report into an email and send it to the team.

3-STEP PLAN:
```

**Output:** ## 3-Step Implementation Plan

**Step 1 — Generate the email draft**
- Parse the quarterly sales report (CSV/JSON) and feed key metrics (revenue, growth, top products, outliers) into the LLM with a strict "email summary" system prompt.
- Target output: a concise, send-ready email in a fixed structure (subject + greeting + summary + call-to-action).

**Step 2 — Evaluate the output with Humanloop**
- Log the generated email to Humanloop as a datapoint.
- Define evaluation criteria (e.g., factual accuracy vs. source numbers, tone, completeness, actionability) using LLM-as-judge + human review.
- Score the draft and capture any failed checks (hallucinated figures, missing key metric) with error strings rather than exceptions, per repo convention.

**Step 3 — Iterate and ship**
- Route the draft: if Humanloop score ≥ threshold and accuracy checks pass → send to the team; if below threshold → regenerate with corrective prompt feedback.
- Record the final sent version and its score in Humanloop as ground truth for future runs.

Result: an email that is generated, evaluated for quality, and only sent when it clears the bar — with every step logged for review.

### Step mem: Memory snapshot

**Output:** 1. Classified need: "output" (Output / Evaluation)
2. Selected tool: Humanloop
3. Plan drafted: ## 3-Step Implementation Plan

**Step 1 — Generate the email draft**
- Parse the...
