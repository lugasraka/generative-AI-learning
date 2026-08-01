"""
Part 6 — Tools for LLM Apps: Tool Ecosystem Recommender + Mini Orchestrator

Catalogs 40 real tools across the four LLM app tool categories (input
processing, LLM development, application, output), scores them against
scenarios with a rule-based engine, compares the rule-based stack with an
LLM's recommendation, and demos a tiny prompt-chaining + memory orchestrator.

Run:  python tool_ecosystem.py            (full run, needs opencode CLI)
      python tool_ecosystem.py --skip-llm  (skip LLM calls, offline)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")

CATEGORY_NAMES = {
    "input": "Input Processing",
    "dev": "LLM Development",
    "app": "Application",
    "output": "Output / Evaluation",
}

# ---------- Tool catalog ----------
# Each entry: name, category, license, hosted, cost, complexity, best_for, description

TOOLS: list[dict] = [
    # --- Input Processing ---
    {
        "name": "Databricks",
        "category": "input",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "high",
        "best_for": ["etl", "analytics", "big_data"],
        "description": "Unified data platform for ETL, analytics, and ML workloads at scale.",
    },
    {
        "name": "Apache Airflow",
        "category": "input",
        "license": "open-source",
        "hosted": False,
        "cost": "med",
        "complexity": "med",
        "best_for": ["etl", "scheduling", "pipelines"],
        "description": "Programmatic workflow authoring, scheduling, and monitoring.",
    },
    {
        "name": "Unstructured.io",
        "category": "input",
        "license": "open-source",
        "hosted": False,
        "cost": "med",
        "complexity": "med",
        "best_for": ["etl", "unstructured", "pdf", "documents"],
        "description": "ETL pipelines for unstructured data like PDFs, docs, and presentations.",
    },
    {
        "name": "Pinecone",
        "category": "input",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "low",
        "best_for": ["vector_db", "retrieval", "scaling"],
        "description": "Cloud-hosted vector database with enterprise scaling, SSO, and uptime SLAs.",
    },
    {
        "name": "Weaviate",
        "category": "input",
        "license": "open-source",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["vector_db", "retrieval", "scaling"],
        "description": "Open-source vector database with strong single-node performance.",
    },
    {
        "name": "Vespa",
        "category": "input",
        "license": "open-source",
        "hosted": False,
        "cost": "high",
        "complexity": "high",
        "best_for": ["vector_db", "retrieval", "big_data"],
        "description": "High-performance open-source serving engine for large-scale vector search.",
    },
    {
        "name": "Qdrant",
        "category": "input",
        "license": "open-source",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["vector_db", "retrieval"],
        "description": "Open-source vector database that scales well on a single node.",
    },
    {
        "name": "Chroma",
        "category": "input",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "low",
        "best_for": ["vector_db", "prototyping", "local"],
        "description": "Local vector store focused on developer experience for small-scale apps.",
    },
    {
        "name": "Faiss",
        "category": "input",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "med",
        "best_for": ["vector_db", "local", "experiments"],
        "description": "Facebook AI similarity search library for efficient vector indexing.",
    },
    {
        "name": "pgvector",
        "category": "input",
        "license": "open-source",
        "hosted": True,
        "cost": "low",
        "complexity": "low",
        "best_for": ["vector_db", "postgres", "sql"],
        "description": "Postgres extension adding vector support to the databases you already use.",
    },
    {
        "name": "Supabase",
        "category": "input",
        "license": "open-source",
        "hosted": True,
        "cost": "low",
        "complexity": "low",
        "best_for": ["vector_db", "postgres", "sql", "hosting"],
        "description": "Open-source Postgres backend bundling pgvector, auth, and storage for app data.",
    },
    # --- LLM Development ---
    {
        "name": "OpenAI API (GPT-4)",
        "category": "dev",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "low",
        "best_for": ["model_api", "inference", "quality"],
        "description": "Proprietary model API; wide compatibility with minimal fine-tuning need.",
    },
    {
        "name": "Hugging Face",
        "category": "dev",
        "license": "open-source",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["model_hub", "open_source", "hosting"],
        "description": "Model hub and hosting ecosystem for open-source models and datasets.",
    },
    {
        "name": "Meta LLaMA",
        "category": "dev",
        "license": "open-source",
        "hosted": True,
        "cost": "low",
        "complexity": "high",
        "best_for": ["open_source_models", "fine_tuning"],
        "description": "Open-source model family that demonstrated near-proprietary accuracy.",
    },
    {
        "name": "Ollama",
        "category": "dev",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "low",
        "best_for": ["local_models", "inference", "open_source"],
        "description": "Local model runner that serves open-source models on your own hardware.",
    },
    {
        "name": "LangChain",
        "category": "dev",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "med",
        "best_for": ["orchestration", "chaining", "loading", "memory"],
        "description": "Orchestration framework for prompt chaining, loaders, and memory.",
    },
    {
        "name": "LlamaIndex",
        "category": "dev",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "med",
        "best_for": ["indexing", "retrieval", "orchestration"],
        "description": "Indexing and retrieval framework for connecting data to LLMs.",
    },
    {
        "name": "PyTorch",
        "category": "dev",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "high",
        "best_for": ["training", "fine_tuning", "research"],
        "description": "Flexible deep learning framework favored for research and fine-tuning.",
    },
    {
        "name": "TensorFlow",
        "category": "dev",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "high",
        "best_for": ["training", "production", "deployment"],
        "description": "Scalable deep learning framework with strong production deployment story.",
    },
    {
        "name": "Fireworks.ai",
        "category": "dev",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["inference", "infrastructure", "speed"],
        "description": "LLM infrastructure optimized for fast, low-cost inference.",
    },
    {
        "name": "Anyscale",
        "category": "dev",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["infrastructure", "scaling", "compute"],
        "description": "Ray-based platform for scaling compute and training workloads.",
    },
    {
        "name": "Weights & Biases",
        "category": "dev",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["experiment_tracking", "metrics", "hyperparameters"],
        "description": "Experiment tracking platform for hyperparameters and metrics over time.",
    },
    {
        "name": "MLflow",
        "category": "dev",
        "license": "open-source",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["tracking", "registry", "deployment"],
        "description": "Open-source platform for model tracking, registry, and deployment.",
    },
    {
        "name": "Statsig",
        "category": "dev",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["ab_testing", "live_eval", "feature_flags"],
        "description": "Live performance evaluation with A/B testing and feature flags.",
    },
    # --- Application ---
    {
        "name": "Replicate",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["model_hosting", "api", "inference"],
        "description": "Hosting platform that simplifies deploying and using open-source models.",
    },
    {
        "name": "OctoML",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["edge", "browser", "deployment", "privacy"],
        "description": "Deployment to edge devices and browsers for privacy and lower latency.",
    },
    {
        "name": "Vercel",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["web_hosting", "frontend", "serverless"],
        "description": "Hosting for the static app layer with serverless functions.",
    },
    {
        "name": "Streamlit",
        "category": "app",
        "license": "open-source",
        "hosted": True,
        "cost": "low",
        "complexity": "low",
        "best_for": ["llm_app_hosting", "prototyping", "ui"],
        "description": "End-to-end hosting with quick Python UI prototyping for LLM apps.",
    },
    {
        "name": "Steamship",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["llm_app_hosting", "end_to_end"],
        "description": "End-to-end hosting tailored specifically for LLM applications.",
    },
    {
        "name": "AWS",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["cloud_hosting", "compute", "scaling"],
        "description": "Broad cloud hosting with GPU/CPU instances for training and inference.",
    },
    {
        "name": "Modal",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "med",
        "best_for": ["serverless", "compute", "hosting"],
        "description": "Serverless compute for running AI workloads without managing infra.",
    },
    {
        "name": "LangSmith",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["observability", "tracing", "evaluation"],
        "description": "LangChain's platform for tracing, observability, and evaluation.",
    },
    {
        "name": "LangKit",
        "category": "app",
        "license": "open-source",
        "hosted": False,
        "cost": "low",
        "complexity": "med",
        "best_for": ["monitoring", "output_quality", "observability"],
        "description": "WhyLabs toolkit giving visibility into the quality of model outputs.",
    },
    {
        "name": "Gantry",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["monitoring", "observability", "feedback"],
        "description": "Tracks inputs, outputs, metadata, and user feedback to explain model behavior.",
    },
    {
        "name": "Helicone",
        "category": "app",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["monitoring", "logging", "latency"],
        "description": "Real-time monitoring of model interactions with minimal setup.",
    },
    {
        "name": "Gradio",
        "category": "app",
        "license": "open-source",
        "hosted": True,
        "cost": "low",
        "complexity": "low",
        "best_for": ["llm_app_hosting", "prototyping", "ui"],
        "description": "Quick shareable UIs for demoing and hosting model demos.",
    },
    # --- Output / Evaluation ---
    {
        "name": "Humanloop",
        "category": "output",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "low",
        "best_for": ["prompt_eval", "prompt_engineering", "no_code"],
        "description": "No/low-code prompt engineering and evaluation across models.",
    },
    {
        "name": "PromptLayer",
        "category": "output",
        "license": "proprietary",
        "hosted": True,
        "cost": "med",
        "complexity": "low",
        "best_for": ["prompt_eval", "prompt_engineering", "logging"],
        "description": "Prompt logging and evaluation for comparing prompts and model outputs.",
    },
    {
        "name": "Honeyhive",
        "category": "output",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["performance_monitoring", "eval", "production"],
        "description": "Production performance monitoring with alerts on key metrics.",
    },
    {
        "name": "Scale AI",
        "category": "output",
        "license": "proprietary",
        "hosted": True,
        "cost": "high",
        "complexity": "med",
        "best_for": ["evaluation", "data_labeling", "monitoring"],
        "description": "Evaluation and data labeling at scale for model quality programs.",
    },
]

# ---------- Scenarios ----------

SCENARIOS: list[dict] = [
    {
        "id": "rag_chatbot",
        "name": "RAG chatbot over internal docs",
        "description": "A small team wants a chatbot that answers questions using internal PDFs and wikis.",
        "budget": "low",
        "expertise": "low",
        "prefer_open_source": True,
        "needs": [
            "vector_db",
            "retrieval",
            "embedding",
            "orchestration",
            "hosting",
            "monitoring",
            "model_api",
        ],
    },
    {
        "id": "finetune_task",
        "name": "Fine-tune a model for a specialized task",
        "description": "An ML team needs a bespoke model for a niche domain with abundant labeled data.",
        "budget": "high",
        "expertise": "high",
        "prefer_open_source": False,
        "needs": [
            "training",
            "fine_tuning",
            "experiment_tracking",
            "compute",
            "model_hub",
        ],
    },
    {
        "id": "consumer_search",
        "name": "High-volume consumer semantic search",
        "description": "A startup needs low-cost semantic search served to millions of free users.",
        "budget": "low",
        "expertise": "med",
        "prefer_open_source": True,
        "needs": [
            "vector_db",
            "retrieval",
            "open_source_models",
            "hosting",
            "scaling",
            "inference",
        ],
    },
    {
        "id": "prod_llm_app",
        "name": "Production LLM app with strict monitoring",
        "description": "An enterprise must ship a customer-facing LLM feature with strong SLAs and oversight.",
        "budget": "high",
        "expertise": "med",
        "prefer_open_source": False,
        "needs": [
            "monitoring",
            "observability",
            "evaluation",
            "ab_testing",
            "model_api",
            "hosting",
            "logging",
        ],
    },
]

# ---------- Scoring engine ----------

COST_FIT = {
    "low": {"low": 1.0, "med": 0.6, "high": 0.2},
    "med": {"low": 0.5, "med": 1.0, "high": 0.6},
    "high": {"low": 0.1, "med": 0.5, "high": 1.0},
}

COMPLEXITY_FIT = {
    "low": {"low": 1.0, "med": 0.5, "high": 0.0},
    "med": {"low": 0.7, "med": 1.0, "high": 0.4},
    "high": {"low": 0.2, "med": 0.6, "high": 1.0},
}


def score_tool(tool: dict, scenario: dict) -> tuple[float, list[str]]:
    """Score one tool against a scenario; returns (score, reasons)."""
    reasons: list[str] = []
    score = 0.0

    cost_fit = COST_FIT[scenario["budget"]][tool["cost"]]
    score += 0.3 * cost_fit
    if cost_fit >= 0.8:
        reasons.append("cost fits budget")

    cx_fit = COMPLEXITY_FIT[scenario["expertise"]][tool["complexity"]]
    score += 0.3 * cx_fit
    if cx_fit >= 0.8:
        reasons.append("complexity matches team expertise")

    overlap = len(set(tool["best_for"]) & set(scenario["needs"]))
    relevance = min(1.0, overlap / 2.0)
    score += 0.4 * relevance
    if relevance >= 0.5:
        reasons.append(f"relevant to needs ({overlap} matching tags)")

    if scenario["prefer_open_source"]:
        if tool["license"] == "open-source":
            score += 0.1
            reasons.append("open-source fits preference")
        else:
            score -= 0.1
            reasons.append("proprietary may clash with open-source preference")
    elif tool["hosted"] and tool["license"] == "proprietary":
        reasons.append("hosted and supported")

    score = max(0.0, min(1.0, score))
    return round(score, 3), reasons[:2]


def score_tools(scenario: dict) -> list[dict]:
    """Score every tool for a scenario, sorted best first."""
    scored = []
    for tool in TOOLS:
        score, reasons = score_tool(tool, scenario)
        scored.append({**tool, "score": score, "reasons": reasons})
    scored.sort(key=lambda t: t["score"], reverse=True)
    return scored


def recommend_stack(scenario: dict, top_n: int = 1) -> list[dict]:
    """Pick the best tool per category to assemble a 4-layer stack."""
    scored = score_tools(scenario)
    stack: list[dict] = []
    for category in ("input", "dev", "app", "output"):
        picks = [t for t in scored if t["category"] == category][:top_n]
        stack.extend(picks)
    return stack


# ---------- LLM agreement ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to the model via the opencode CLI; returns text or error."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


STACK_PROMPT = (
    "You are an AI engineer selecting a tool stack for an LLM application.\n"
    "Given the scenario, pick ONE real tool per category and reply with ONLY a "
    'JSON object like {{"input": "...", "development": "...", '
    '"application": "...", "output": "..."}}.\n\n'
    "Scenario: {name}. {description}\n"
    "Budget: {budget}. Team expertise: {expertise}. "
    "Prefer open source: {prefer_open_source}.\n"
    "Key needs: {needs}.\n\n"
    "JSON:"
)


def parse_stack(raw: str) -> dict[str, str] | None:
    """Parse the LLM's stack reply; falls back to regex extraction."""
    raw = raw.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return {str(k).lower(): str(v) for k, v in parsed.items()}
        except json.JSONDecodeError:
            pass
    fields: dict[str, str] = {}
    for key in ("input", "development", "application", "output"):
        m = re.search(rf'"{key}"\s*:\s*"([^"]+)"', raw)
        if m:
            fields[key] = m.group(1)
    return fields or None


def llm_recommend(scenario: dict) -> dict[str, str] | None:
    """Ask the LLM for a stack recommendation."""
    prompt = STACK_PROMPT.format(
        name=scenario["name"],
        description=scenario["description"],
        budget=scenario["budget"],
        expertise=scenario["expertise"],
        prefer_open_source=scenario["prefer_open_source"],
        needs=", ".join(scenario["needs"]),
    )
    raw = ask_llm(prompt)
    if raw.startswith("["):
        return None
    return parse_stack(raw)


def normalize_name(name: str) -> str:
    """Lowercase and strip common suffixes for name comparison."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def compare_stacks(rule_stack: list[dict], llm_stack: dict[str, str]) -> list[dict]:
    """Compare rule-based vs LLM stacks per category."""
    rule_names = {t["category"]: t["name"] for t in rule_stack}
    rows = []
    for category in ("input", "dev", "app", "output"):
        rule_name = rule_names.get(category, "")
        llm_key = {
            "input": "input",
            "dev": "development",
            "app": "application",
            "output": "output",
        }[category]
        llm_name = llm_stack.get(llm_key, "")
        agree = bool(llm_name) and normalize_name(rule_name) == normalize_name(llm_name)
        rows.append(
            {
                "category": category,
                "rule_based": rule_name,
                "llm": llm_name,
                "agree": agree,
            }
        )
    return rows


# ---------- Mini orchestrator ----------

MEMORY: list[str] = []


def remember(text: str) -> None:
    """Append a turn to the orchestrator's working memory."""
    MEMORY.append(text)


def memory_block() -> str:
    """Render prior turns as a numbered memory transcript."""
    if not MEMORY:
        return "(no prior context)"
    return "\n".join(f"{i}. {line}" for i, line in enumerate(MEMORY, 1))


def pick_tool_for_category(category: str) -> dict:
    """Deterministically choose the top catalog tool for a category."""
    category_tools = [t for t in TOOLS if t["category"] == category]
    return max(category_tools, key=lambda t: len(t["best_for"]))


def run_orchestration_demo(query: str) -> list[dict]:
    """Run a chained 3-step orchestration with shared memory."""
    transcript: list[dict] = []
    global MEMORY
    MEMORY = []

    step1_prompt = (
        "You are an LLM app orchestrator. Classify the user request into exactly "
        'one of: "input", "development", "application", "output". '
        "Reply with just that word.\n\n"
        f"USER REQUEST: {query}"
    )
    step1 = ask_llm(step1_prompt)
    category = step1.strip().lower().strip('"')
    if category not in CATEGORY_NAMES:
        category = "application"
    remember(f'Classified need: "{category}" ({CATEGORY_NAMES[category]})')
    transcript.append(
        {
            "step": 1,
            "name": "Classify need",
            "prompt": step1_prompt,
            "output": step1,
            "detail": f"category={category}",
        }
    )

    tool = pick_tool_for_category(category)
    remember(f"Selected tool: {tool['name']}")
    transcript.append(
        {
            "step": 2,
            "name": "Select tool",
            "prompt": "",
            "output": tool["name"],
            "detail": f"{tool['description']} (from catalog)",
        }
    )

    step3_prompt = (
        "You are an LLM app orchestrator. Using the classified need and selected "
        "tool below, outline a 3-step implementation plan.\n\n"
        "MEMORY (prior turns):\n{memory}\n\n"
        f"ORIGINAL USER REQUEST: {query}\n\n"
        "3-STEP PLAN:"
    ).format(memory=memory_block())
    step3 = ask_llm(step3_prompt)
    remember(f"Plan drafted: {step3[:80]}...")
    transcript.append(
        {
            "step": 3,
            "name": "Generate plan",
            "prompt": step3_prompt,
            "output": step3,
            "detail": "",
        }
    )

    transcript.append(
        {
            "step": "mem",
            "name": "Memory snapshot",
            "prompt": "",
            "output": memory_block(),
            "detail": "",
        }
    )
    return transcript


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_stack(scenario: dict, stack: list[dict]) -> None:
    """Print a recommended stack for a scenario."""
    print(f'\n  Scenario: "{scenario["name"]}"')
    for t in stack:
        print(
            f"    [{CATEGORY_NAMES[t['category']]:18}] {t['name']:<26} "
            f"score={t['score']:.2f}  ({'; '.join(t['reasons'])})"
        )


# ---------- Save results ----------


def save_results(
    catalog_stats: dict,
    scenario_reports: list[dict],
    orchestration: list[dict],
    path: str,
) -> None:
    """Write the run output to part6_results.md."""
    lines: list[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("# Part 6 — Tool Ecosystem Results\n")
    lines.append(f"> **Model:** `{MODEL}`  ")
    lines.append(f"> **Date:** {now}\n")

    lines.append("## Catalog Stats\n")
    lines.append(f"- Total tools: {catalog_stats['total']}")
    for cat, count in catalog_stats["by_category"].items():
        lines.append(f"- {CATEGORY_NAMES[cat]}: {count}")
    lines.append("")

    lines.append("## Scenario Recommendations\n")
    for report in scenario_reports:
        lines.append(f"### {report['scenario']['name']}\n")
        lines.append("**Rule-based stack:**\n")
        for t in report["stack"]:
            lines.append(
                f"- `[{t['category']}]` **{t['name']}** "
                f"(score={t['score']:.2f}, {t['cost']} cost, {t['complexity']} complexity)"
            )
            if t["reasons"]:
                lines.append(f"  - {', '.join(t['reasons'])}")
        if report["llm_stack"]:
            lines.append("\n**LLM stack:**")
            for cat, name in report["llm_stack"].items():
                lines.append(f"- `{cat}`: {name}")
            lines.append("\n**Agreement:**\n")
            for row in report["agreement"]:
                mark = "agree" if row["agree"] else "differ"
                lines.append(
                    f"- `{row['category']}` rule={row['rule_based']!r} llm={row['llm']!r} → {mark}"
                )
            matched = sum(1 for r in report["agreement"] if r["agree"])
            lines.append(f"\n**Match rate:** {matched}/4 categories")
        else:
            lines.append("\n**LLM stack:** (skipped or unavailable)")
        lines.append("")

    lines.append("## Orchestration Demo (Prompt Chaining + Memory)\n")
    for record in orchestration:
        lines.append(f"### Step {record['step']}: {record['name']}\n")
        if record["prompt"]:
            lines.append(f"```\n{record['prompt']}\n```\n")
        lines.append(f"**Output:** {record['output']}\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------- Main ----------


def main() -> None:
    parser = argparse.ArgumentParser(description="Part 6 tool ecosystem lab")
    parser.add_argument(
        "--skip-llm", action="store_true", help="skip all opencode LLM calls"
    )
    args = parser.parse_args()

    print(f"Model: {MODEL}")
    banner("TOOL ECOSYSTEM — RECOMMENDER + MINI ORCHESTRATOR")

    by_category: dict[str, int] = {}
    for tool in TOOLS:
        by_category[tool["category"]] = by_category.get(tool["category"], 0) + 1
    catalog_stats = {"total": len(TOOLS), "by_category": by_category}
    print(f"\n  Catalog: {len(TOOLS)} tools across 4 categories")
    for cat, count in sorted(by_category.items()):
        print(f"    {CATEGORY_NAMES[cat]:18} {count} tools")

    scenario_reports = []
    for i, scenario in enumerate(SCENARIOS, 1):
        pct = i / len(SCENARIOS) * 100
        bar_filled = round(pct / 5)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(f"\n  [{i}/{len(SCENARIOS)}] {bar} {pct:.0f}%  {scenario['name']}")

        stack = recommend_stack(scenario)
        print_stack(scenario, stack)

        llm_stack = None
        agreement = []
        if not args.skip_llm:
            print("\n  Asking LLM for its stack...")
            llm_stack = llm_recommend(scenario)
            if llm_stack:
                print(f"    LLM stack: {json.dumps(llm_stack)}")
                agreement = compare_stacks(stack, llm_stack)
                matched = sum(1 for r in agreement if r["agree"])
                print(f"    Agreement: {matched}/4 categories")
            else:
                print("    (no LLM stack available)")

        scenario_reports.append(
            {
                "scenario": scenario,
                "stack": stack,
                "llm_stack": llm_stack,
                "agreement": agreement,
            }
        )

    banner("MINI ORCHESTRATOR (Prompt Chaining + Memory)")
    demo_query = (
        "I want to summarize our quarterly sales report into an email "
        "and send it to the team."
    )
    print(f"\n  Demo query: {demo_query}\n")
    orchestration = []
    if args.skip_llm:
        orchestration = [
            {
                "step": 1,
                "name": "Classify need",
                "prompt": "(skipped)",
                "output": "(skipped)",
                "detail": "",
            }
        ]
        print("  (LLM calls skipped)")
    else:
        orchestration = run_orchestration_demo(demo_query)
        for record in orchestration:
            if record["name"] == "Memory snapshot":
                print(f"  [mem] {record['output'][:120].replace(chr(10), ' | ')}...")
            else:
                print(
                    f"  [step {record['step']}] {record['name']}: {record['output'][:100]}"
                )
        print()

    results_path = os.path.join(os.path.dirname(__file__), "part6_results.md")
    save_results(catalog_stats, scenario_reports, orchestration, results_path)
    print(f"  Results saved to: {results_path}")

    banner("DONE — Part 6 complete. Next: Part 7 (LLM Evaluation)")


if __name__ == "__main__":
    main()
