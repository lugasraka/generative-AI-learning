"""
Part 11 — Emerging Research Trends: Interactive Research Explorer

Explores five LLM research areas (multimodal, open-source, agents,
domain-specific, new architectures) via an interactive CLI menu with
ELI5 explanations, a trend timeline, comparison mode, quiz, and
personalized reading list. Optionally generates a self-contained HTML
version.

Run:  python research_explorer.py
      python research_explorer.py --skip-llm
      python research_explorer.py --html
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from typing import Any

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
LLM_TIMEOUT_SECONDS = 60

# ---------- Research data ----------

AREAS: dict[str, dict[str, Any]] = {
    "multimodal_llms": {
        "title": "Multimodal LLMs",
        "icon": "\U0001f50d",
        "color": "#3b82f6",
        "subtopics": {
            "architecture": {
                "title": "Architecture",
                "detail": (
                    "Most MM-LLMs have 5 components: Modality Encoder (extracts "
                    "features from images/audio/video), Input Projector (aligns "
                    "features to the text space), LLM Backbone (core reasoning), "
                    "Output Projector (maps LLM output to modality features), and "
                    "Modality Generator (produces images/video/audio via diffusion)."
                ),
                "references": [
                    "MM-LLMs: Recent Advances (arxiv.org/abs/2401.13601)",
                ],
                "eli5": (
                    "Imagine a person who can read, see pictures, and listen to "
                    "music all at once. An MM-LLM is like that person — it has "
                    "special eyes for images, ears for audio, and a brain that "
                    "puts it all together to understand and respond."
                ),
            },
            "training": {
                "title": "Training",
                "detail": (
                    "Two stages: (1) MM Pre-Training — learn to align images, "
                    "video, and text together; (2) MM Instruction Tuning — "
                    "fine-tune with SFT (supervised) and RLHF (human feedback) "
                    "so the model follows instructions across modalities."
                ),
                "references": [
                    "MM-LLMs: Recent Advances (arxiv.org/abs/2401.13601)",
                ],
                "eli5": (
                    "First you show the model lots of pictures with captions so "
                    "it learns what goes together (like teaching a child with "
                    "flashcards). Then you give it practice questions and correct "
                    "its mistakes so it gets better at following your requests."
                ),
            },
            "key_models": {
                "title": "Key Models",
                "detail": (
                    "GPT-4o (OpenAI, omni-modal), Gemini (Google, natively "
                    "multimodal), Claude 3 (Anthropic, 3 capability tiers), "
                    "LLaVA (open-source, visual instruction tuning)."
                ),
                "references": [
                    "OpenAI GPT-4o technical report",
                    "Google Gemini technical report",
                ],
                "eli5": (
                    "There are a few star players: GPT-4o can see and hear, "
                    "Gemini was born multimodal (images are its first language), "
                    "Claude 3 comes in three sizes (like small/medium/large), "
                    "and LLaVA is the open-source champion."
                ),
            },
            "future": {
                "title": "Future Directions",
                "detail": (
                    "Mobile deployment, embodied intelligence (robots using "
                    "MM-LLMs), continual instruction tuning without forgetting, "
                    "and extending to more modalities like web pages and heat maps."
                ),
                "references": [
                    "PaLM-E (embodied intelligence)",
                ],
                "eli5": (
                    "In the future, these models will fit in your phone, help "
                    "robots see and act, and keep learning new things without "
                    "forgetting old ones — like a student who never stops growing."
                ),
            },
        },
    },
    "open_source": {
        "title": "Open-Source Models",
        "icon": "\U0001f513",
        "color": "#22c55e",
        "subtopics": {
            "llama": {
                "title": "LLaMA Family",
                "detail": (
                    "Meta's LLaMA (Feb 2023, 13B) outperformed GPT-3 on many "
                    "benchmarks. LLaMA 2 (Jul 2023) added 40% more data, doubled "
                    "context, and released chat and code variants."
                ),
                "references": [
                    "Meta AI LLaMA 2 technical report",
                ],
                "eli5": (
                    "LLaMA is a family of smart models from Meta. The first "
                    "version was already great, and the second version learned "
                    "40% more and can chat and write code. It is free for "
                    "everyone to use."
                ),
            },
            "mistral": {
                "title": "Mistral / Mixtral",
                "detail": (
                    "Mistral 7B (Sep 2023) outperformed all open models up to "
                    "13B. Mixtral 8x7B (Dec 2023) introduced sparse Mixture of "
                    "Experts, activating only a few experts per token."
                ),
                "references": [
                    "Mistral AI technical reports",
                ],
                "eli5": (
                    "Mistral made a small model that punches way above its "
                    "weight. Then they made Mixtral, which is like having 8 "
                    "specialists but only asking 2 of them per question — "
                    "fast and smart."
                ),
            },
            "olmo": {
                "title": "OLMo",
                "detail": (
                    "Part of the AI2 framework (Jan 2024). Fully open: training "
                    "data (Dolma), code, model weights (4 x 7B variants), and "
                    "evaluation tools (Catwalk)."
                ),
                "references": [
                    "OLMo technical report (AI2)",
                ],
                "eli5": (
                    "OLMo is like a science fair project where the student "
                    "shares everything: the recipe, the ingredients, the code, "
                    "and even the mistakes. Anyone can reproduce and improve it."
                ),
            },
            "llm360": {
                "title": "LLM360 Initiative",
                "detail": (
                    "Advocates fully open LLM development: code, data, "
                    "checkpoints, and intermediate results. Released AMBER and "
                    "CRYSTALCODER (7B each) with complete transparency."
                ),
                "references": [
                    "LLM360 initiative",
                ],
                "eli5": (
                    "LLM360 wants to make AI training a team sport. They share "
                    "every step of the process — not just the final model but "
                    "every checkpoint along the way."
                ),
            },
        },
    },
    "agents": {
        "title": "LLM Agents",
        "icon": "\U0001f916",
        "color": "#8b5cf6",
        "subtopics": {
            "architecture": {
                "title": "Architecture (4 Modules)",
                "detail": (
                    "Profiling (who am I?), Memory (what do I know?), Planning "
                    "(what should I do?), Action (which tools do I call?). "
                    "Together these let the agent break down tasks, reason, "
                    "and execute autonomously."
                ),
                "references": [
                    "A Survey on LLM-based Autonomous Agents "
                    "(arxiv.org/abs/2308.11432)",
                ],
                "eli5": (
                    "An agent is like a helper robot with a name tag (profiling), "
                    "a notebook (memory), a to-do list (planning), and a toolbox "
                    "(action). It figures out what to do, remembers what it did, "
                    "and uses the right tools."
                ),
            },
            "capabilities": {
                "title": "Capabilities",
                "detail": (
                    "Autonomy (reactive to proactive), task completion (simple "
                    "chat to complex workflows), adaptability (natural language "
                    "instructions), advanced skills (planning + execution), and "
                    "human-AI collaboration."
                ),
                "references": [],
                "eli5": (
                    "Agents can work on their own, handle big projects, adapt "
                    "to new instructions, plan ahead, and work alongside humans "
                    "like a real team member."
                ),
            },
            "multi_agent": {
                "title": "Multi-Agent Systems",
                "detail": (
                    "Scaling to multiple agents raises challenges: coordination, "
                    "communication overhead, computational demands, and collective "
                    "intelligence vs individual optimization."
                ),
                "references": [],
                "eli5": (
                    "Having one smart assistant is great, but having a whole team "
                    "of them is even better — if they can talk to each other and "
                    "not step on each other's toes."
                ),
            },
            "future": {
                "title": "Future Directions",
                "detail": (
                    "Expanding to multimodal environments, mitigating cascading "
                    "hallucinations, building reliable learning environments, "
                    "and developing comprehensive benchmarks across domains."
                ),
                "references": [],
                "eli5": (
                    "The future is agents that can see, hear, and act in the "
                    "real world without making mistakes that snowball — and "
                    "tests to prove they are reliable."
                ),
            },
        },
    },
    "domain_specific": {
        "title": "Domain-Specific LLMs",
        "icon": "\U0001f3af",
        "color": "#f59e0b",
        "subtopics": {
            "clinical": {
                "title": "Clinical / Biomedical",
                "detail": (
                    "BioBERT: pre-trained on biomedical corpora for text mining. "
                    "Hi-BEHRT: hierarchical Transformer for long electronic "
                    "health records. These models understand medical jargon and "
                    "regulatory requirements."
                ),
                "references": [
                    "BioBERT (pubmed.ncbi.nlm.nih.gov)",
                ],
                "eli5": (
                    "These are like medical librarians who have read every "
                    "healthcare textbook and can find the exact information "
                    "doctors need, even in very long patient records."
                ),
            },
            "finance": {
                "title": "Finance",
                "detail": (
                    "BloombergGPT (50B params, trained on financial data) excels "
                    "at financial tasks. FinGPT fine-tunes existing LLMs for "
                    "financial understanding."
                ),
                "references": [
                    "BloombergGPT technical report",
                    "FinGPT (arxiv.org/abs/2306.06031)",
                ],
                "eli5": (
                    "Imagine a financial advisor who has read every annual report, "
                    "every news article about money, and can spot trends in "
                    "markets. BloombergGPT is that advisor."
                ),
            },
            "code": {
                "title": "Code-Specific",
                "detail": (
                    "WizardCoder: complex instruction fine-tuning for code. "
                    "CodeT5: focuses on semantics in code, understanding "
                    "developer-assigned identifiers."
                ),
                "references": [
                    "WizardCoder (arxiv.org/abs/2304.12244)",
                ],
                "eli5": (
                    "Code-specific models are like expert programmers who "
                    "understand not just the syntax but the meaning behind "
                    "variable names and what the code is trying to do."
                ),
            },
            "future": {
                "title": "Future Trends",
                "detail": (
                    "Multimodal domain models, real-time knowledge updates, "
                    "integration with decision-making algorithms, and "
                    "stronger ethical/fairness standards for sensitive fields."
                ),
                "references": [],
                "eli5": (
                    "Domain models will soon read images too, learn new things "
                    "on the fly, work alongside other AI tools, and be extra "
                    "careful about fairness in healthcare and finance."
                ),
            },
        },
    },
    "new_architectures": {
        "title": "New Architectures",
        "icon": "\u2699\ufe0f",
        "color": "#ef4444",
        "subtopics": {
            "moe": {
                "title": "Mixture of Experts",
                "detail": (
                    "Replaces dense FFN layers with sparse MoE layers. Each "
                    "layer has multiple 'experts' (neural networks) and a Gate "
                    "Network that routes tokens to the best 1-2 experts. "
                    "Faster training + inference but high memory (all params "
                    "loaded). Mixtral 8x7B is the famous example."
                ),
                "references": [
                    "Mixtral of Experts (arxiv.org/abs/2401.04088)",
                ],
                "eli5": (
                    "Imagine a hospital with 8 specialist doctors. When a "
                    "patient comes in, a receptionist (the gate) sends them to "
                    "only the 2 most relevant doctors. You get specialist care "
                    "without paying for all 8 at once."
                ),
            },
            "mamba": {
                "title": "Mamba (Selective State Spaces)",
                "detail": (
                    "Uses Selective State Spaces instead of attention. Linear "
                    "time complexity (vs quadratic for Transformers). 5x faster "
                    "for long sequences (up to 1M tokens). A potential "
                    "Transformer successor."
                ),
                "references": [
                    "Mamba: Linear-Time Sequence Modeling (arxiv.org/abs/2312.00752)",
                ],
                "eli5": (
                    "Transformers read a whole book every time they answer a "
                    "question. Mamba reads only the relevant pages — like a "
                    "smart student who uses the index instead of re-reading "
                    "everything. Much faster for long texts."
                ),
            },
            "rwkv": {
                "title": "RWKV (RNN-Transformer Hybrid)",
                "detail": (
                    "Combines RNN linear scaling with Transformer parallelized "
                    "training. Handles very long contexts without quadratic "
                    "memory. Integrates with HuggingFace Transformers."
                ),
                "references": [
                    "RWKV: Reinventing RNNs for the Transformer Era",
                ],
                "eli5": (
                    "RWKV is like a hybrid car — it uses the best of two engines. "
                    "From RNNs it gets speed with long texts, from Transformers "
                    "it gets smart training. The result is fast, efficient, and "
                    "open-source."
                ),
            },
            "comparison": {
                "title": "Comparing the Three",
                "detail": (
                    "MoE: proven, used by Mixtral, high memory but fast. "
                    "Mamba: newest, linear scaling, best for very long sequences. "
                    "RWKV: most mature hybrid, RNN inference + Transformer training. "
                    "All three aim to reduce Transformer compute costs."
                ),
                "references": [],
                "eli5": (
                    "MoE is like having multiple specialists you pick from, "
                    "Mamba reads only what matters, and RWKV switches between "
                    "two reading modes. They all want to make AI faster and "
                    "cheaper than the Transformer baseline."
                ),
            },
        },
    },
}

AREA_KEYS = list(AREAS.keys())

TIMELINE: list[dict[str, str]] = [
    {
        "date": "2023-02",
        "event": "LLaMA (Meta)",
        "detail": "13B params, outperforms GPT-3 on NLP benchmarks",
    },
    {
        "date": "2023-03",
        "event": "GPT-4 (OpenAI)",
        "detail": "Multimodal capabilities, major reasoning improvements",
    },
    {
        "date": "2023-07",
        "event": "LLaMA 2 (Meta)",
        "detail": "40% more data, chat + code variants, doubled context",
    },
    {
        "date": "2023-09",
        "event": "Mistral 7B",
        "detail": "Outperforms all open-source LLMs up to 13B",
    },
    {
        "date": "2023-10",
        "event": "Mixtral 8x7B",
        "detail": "Sparse Mixture of Experts, fast + smart",
    },
    {
        "date": "2023-11",
        "event": "OLMo (AI2)",
        "detail": "Fully open: data, code, weights, eval tools",
    },
    {
        "date": "2023-12",
        "event": "Gemini (Google)",
        "detail": "Natively multimodal, 3 capability tiers",
    },
    {
        "date": "2023-12",
        "event": "Mamba",
        "detail": "Selective state spaces, linear time, 5x faster",
    },
    {
        "date": "2024-01",
        "event": "GPT-4o (OpenAI)",
        "detail": "Omni-modal: text + vision + audio in one model",
    },
    {
        "date": "2024-01",
        "event": "LLM360",
        "detail": "AMBER + CRYSTALCODER, fully open training pipeline",
    },
    {
        "date": "2024-02",
        "event": "Claude 3 (Anthropic)",
        "detail": "Opus/Sonnet/Haiku tiers, strong safety alignment",
    },
    {
        "date": "2024-03",
        "event": "RWKV v5",
        "detail": "Hybrid RNN-Transformer, HuggingFace integration",
    },
]

QUIZ: list[dict[str, Any]] = [
    {
        "question": (
            "Which architecture uses a 'Gate Network' to route tokens to "
            "specialized expert sub-networks?"
        ),
        "options": ["Mamba", "RWKV", "Mixture of Experts", "LLaVA"],
        "answer": 2,
        "area": "new_architectures",
    },
    {
        "question": ("What is the key innovation of Mamba over standard Transformers?"),
        "options": [
            "Better accuracy on all benchmarks",
            "Linear time complexity (vs quadratic)",
            "Native multimodal support",
            "Larger default context window",
        ],
        "answer": 1,
        "area": "new_architectures",
    },
    {
        "question": (
            "Which model framework is fully open with training data, code, "
            "model weights, and evaluation tools?"
        ),
        "options": ["LLaMA", "Mistral", "OLMo", "GPT-4"],
        "answer": 2,
        "area": "open_source",
    },
    {
        "question": ("What are the 4 core modules of the LLM agent architecture?"),
        "options": [
            "Input, Process, Output, Store",
            "Profiling, Memory, Planning, Action",
            "Encode, Decode, Route, Generate",
            "Parse, Retrieve, Reason, Respond",
        ],
        "answer": 1,
        "area": "agents",
    },
    {
        "question": (
            "Which domain-specific LLM is designed for biomedical text mining?"
        ),
        "options": ["BloombergGPT", "WizardCoder", "BioBERT", "FinGPT"],
        "answer": 2,
        "area": "domain_specific",
    },
]

READING_LIST_SUGGESTIONS: dict[str, list[dict[str, str]]] = {
    "multimodal_llms": [
        {
            "title": "MM-LLMs: Recent Advances (arXiv 2401.13601)",
            "reason": "Comprehensive survey of multimodal LLM architecture and training",
        },
        {
            "title": "LLaVA: Visual Instruction Tuning",
            "reason": "Foundational paper on open-source visual instruction tuning",
        },
    ],
    "open_source": [
        {
            "title": "LLaMA 2: Open Foundation and Fine-Tuned Chat Models",
            "reason": "Meta's open-source chat and code model release",
        },
        {
            "title": "OLMo: Accelerating the Science of Language Models",
            "reason": "Fully reproducible open training pipeline",
        },
        {
            "title": "Mistral 7B / Mixtral 8x7B",
            "reason": "Proof that small models can beat large ones with smart architecture",
        },
    ],
    "agents": [
        {
            "title": "A Survey on LLM-based Autonomous Agents (arXiv 2308.11432)",
            "reason": "Definitive agent architecture survey",
        },
        {
            "title": "LLM Powered Autonomous Agents (Lilian Weng blog)",
            "reason": "Excellent practical overview with examples",
        },
    ],
    "domain_specific": [
        {
            "title": "BloombergGPT: A Large Language Model for Finance",
            "reason": "Landmark domain-specific 50B model",
        },
        {
            "title": "BioBERT: pre-trained biomedical text mining",
            "reason": "Foundational biomedical NLP model",
        },
    ],
    "new_architectures": [
        {
            "title": "Mamba: Linear-Time Sequence Modeling (arXiv 2312.00752)",
            "reason": "The Transformer challenger with linear scaling",
        },
        {
            "title": "Mixtral of Experts (arXiv 2401.04088)",
            "reason": "Proven MoE at scale in open-source",
        },
        {
            "title": "RWKV: Reinventing RNNs for the Transformer Era",
            "reason": "Best of RNN + Transformer worlds",
        },
    ],
}

# ---------- LLM calling ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode and return text or a bracketed error."""
    try:
        result = subprocess.run(
            ["opencode", "run", "-m", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=LLM_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"[opencode timeout after {LLM_TIMEOUT_SECONDS}s]"
    except OSError as error:
        return f"[opencode error] {error}"
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Display helpers ----------


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def numbered_menu(items: list[str]) -> None:
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")


def get_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        try:
            val = int(input(prompt))
            if lo <= val <= hi:
                return val
        except (ValueError, EOFError):
            pass
        print(f"  Enter a number between {lo} and {hi}.")


# ---------- CLI features ----------


def show_area_detail(area_key: str, online: bool) -> None:
    area = AREAS[area_key]
    banner(f"{area['icon']}  {area['title']}")
    topics: dict[str, dict[str, object]] = area["subtopics"]  # type: ignore[assignment]
    keys = list(topics.keys())
    for i, k in enumerate(keys, 1):
        t = topics[k]
        print(f"\n  {i}. {t['title']}")
        print(f"     {t['detail']}")
        refs: list[str] = [str(r) for r in t.get("references", [])]
        if refs:
            print(f"     References: {', '.join(refs)}")
    print()
    sub = get_int("  Select a subtopic for ELI5 (0 to skip): ", 0, len(keys))
    if sub == 0:
        return
    key = keys[sub - 1]
    t = topics[key]
    if online:
        prompt = (
            "Explain this concept in 3 simple sentences for someone learning "
            f"about LLMs: {t['detail']}"
        )
        response = ask_llm(prompt)
        if response.startswith("["):
            response = str(t["eli5"])
    else:
        response = str(t["eli5"])
    print(f"\n  ELI5: {response}")


def run_comparison(area1: str, area2: str, online: bool) -> str:
    a1 = AREAS[area1]
    a2 = AREAS[area2]
    if online:
        prompt = (
            f"Compare and contrast {a1['title']} and {a2['title']} in LLM "
            "research. What do they have in common? How do they differ? "
            "Which is more impactful? Answer in 4 sentences."
        )
        return ask_llm(prompt)
    return (
        f"{a1['title']} and {a2['title']} are both active LLM research "
        "areas. Each addresses different challenges — one focuses on "
        "expanding model capabilities while the other improves efficiency "
        "or accessibility. Their combined progress pushes the field forward."
    )


def run_quiz() -> tuple[int, list[dict[str, str]]]:
    """Run the quiz and return (score, results)."""
    score = 0
    results: list[dict[str, str]] = []
    for q in QUIZ:
        print(f"\n  Q: {q['question']}")
        options: list[str] = q["options"]  # type: ignore[assignment]
        for j, opt in enumerate(options):
            print(f"     {chr(65 + j)}) {opt}")
        choice = get_int("  Your answer (A/B/C/D): ", 1, 4)
        correct_idx = q["answer"]  # type: ignore[assignment]
        is_correct = choice - 1 == correct_idx
        if is_correct:
            score += 1
        results.append(
            {
                "question": str(q["question"]),
                "your_answer": options[choice - 1],
                "correct_answer": options[correct_idx],
                "result": "CORRECT" if is_correct else "WRONG",
            }
        )
        print(
            f"  {'CORRECT' if is_correct else 'WRONG'} (answer: {options[correct_idx]})"
        )
    return score, results


def generate_reading_list(area_keys: list[str], time_budget: str, online: bool) -> str:
    titles = [AREAS[k]["title"] for k in area_keys]
    if online:
        prompt = (
            f"Given these LLM research topics: {', '.join(titles)}, and the "
            f"user has {time_budget} to read, recommend 3-5 papers or articles "
            "to read, prioritized by impact. Return a numbered list with "
            "title and one-line reason."
        )
        return ask_llm(prompt)
    items: list[str] = []
    for k in area_keys:
        for entry in READING_LIST_SUGGESTIONS.get(k, []):
            items.append(f"- {entry['title']} ({entry['reason']})")
    return "\n".join(items)


# ---------- Main CLI ----------


def run_cli(online: bool) -> tuple[str, int]:
    """Run the interactive CLI menu. Returns (reading_list, quiz_score)."""
    reading_list = ""
    quiz_score = 0
    while True:
        banner("RESEARCH EXPLORER")
        numbered_menu(
            [a["title"] for a in AREAS.values()]  # type: ignore[misc]
            + [
                "Compare two areas",
                "Trend timeline",
                "Personalized reading list",
                "Quiz",
                "Quit",
            ]
        )
        n_areas = len(AREAS)
        choice = get_int("\n  Pick: ", 0, n_areas + 5)

        if choice == 0 or choice == n_areas + 5:
            break
        elif choice <= n_areas:
            show_area_detail(AREA_KEYS[choice - 1], online)
        elif choice == n_areas + 1:
            print("\n  Pick two areas to compare (comma-separated, e.g. 1,3):")
            numbered_menu([a["title"] for a in AREAS.values()])  # type: ignore[misc]
            raw = input("  > ").strip()
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                i1, i2 = int(parts[0]), int(parts[1])
                if 1 <= i1 <= n_areas and 1 <= i2 <= n_areas and i1 != i2:
                    banner("COMPARISON")
                    result = run_comparison(
                        AREA_KEYS[i1 - 1], AREA_KEYS[i2 - 1], online
                    )
                    print(f"\n  {result}")
                else:
                    print("  Invalid selection.")
            else:
                print("  Please enter two comma-separated numbers.")
        elif choice == n_areas + 2:
            banner("TREND TIMELINE")
            for entry in TIMELINE:
                print(f"  {entry['date']}  {entry['event']}")
                print(f"           {entry['detail']}")
        elif choice == n_areas + 3:
            banner("READING LIST")
            print("  Which areas interest you? (comma-separated numbers)")
            numbered_menu([a["title"] for a in AREAS.values()])  # type: ignore[misc]
            raw = input("  > ").strip()
            parts = [p.strip() for p in raw.split(",")]
            selected = [
                AREA_KEYS[int(p) - 1]
                for p in parts
                if p.isdigit() and 1 <= int(p) <= n_areas
            ]
            if not selected:
                selected = AREA_KEYS[:]
            print("  How much time? (15min / 30min / 1hr)")
            time_input = input("  > ").strip() or "30min"
            reading_list = generate_reading_list(selected, time_input, online)
            print(f"\n{reading_list}")
        elif choice == n_areas + 4:
            banner("QUIZ")
            quiz_score, _ = run_quiz()
            print(f"\n  Score: {quiz_score}/{len(QUIZ)}")

    return reading_list, quiz_score


# ---------- HTML Generation ----------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Research Trend Explorer</title>
<style>
:root{--blue:#3b82f6;--green:#22c55e;--purple:#8b5cf6;--amber:#f59e0b;--red:#ef4444;--text:#1e293b;--muted:#64748b;--border:#e2e8f0;--bg:#f1f5f9;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--text);background:var(--bg);line-height:1.6}
.container{max-width:1040px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.8rem;margin-bottom:4px}
.subtitle{color:var(--muted);font-size:0.95rem;margin-bottom:22px}
h2{font-size:1.25rem;margin:28px 0 12px}
h3{font-size:1rem;margin-bottom:6px}

.areas-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px}
.area-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s}
.area-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.08)}
.area-card .icon{font-size:1.6rem;margin-bottom:6px}
.area-card .title{font-weight:700;font-size:0.95rem}
.area-card .count{font-size:0.78rem;color:var(--muted)}

.detail-panel{display:none;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:24px}
.detail-panel.active{display:block}
.detail-panel h2{margin-top:0}
.close-btn{float:right;background:none;border:none;font-size:1.2rem;cursor:pointer;color:var(--muted)}

.subtopic{border-bottom:1px solid var(--border);padding:12px 0}
.subtopic:last-child{border-bottom:none}
.subtopic .st-title{font-weight:600;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.subtopic .st-title::after{content:'\\25BE';font-size:0.8rem}
.subtopic.open .st-title::after{content:'\\25B4'}
.st-body{display:none;margin-top:8px;font-size:0.9rem}
.subtopic.open .st-body{display:block}
.st-body .detail{margin-bottom:8px}
.st-body .refs{font-size:0.8rem;color:var(--muted);margin-bottom:8px}
.eli5-box{background:#f0f9ff;border-left:3px solid var(--blue);padding:10px 14px;border-radius:0 6px 6px 0;font-size:0.88rem;margin-top:8px;display:none}
.eli5-box.show{display:block}
.eli5-toggle{background:var(--blue);color:#fff;border:none;border-radius:6px;padding:5px 12px;font-size:0.82rem;cursor:pointer;margin-top:6px}
.eli5-toggle:hover{background:#2563eb}

.compare-section{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:24px}
.compare-section select{padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-size:0.9rem;margin-right:8px}
.compare-btn{background:var(--purple);color:#fff;border:none;border-radius:6px;padding:8px 20px;font-size:0.9rem;cursor:pointer}
.compare-btn:hover{background:#7c3aed}
.compare-result{margin-top:14px;font-size:0.9rem;padding:14px;background:#f5f3ff;border-radius:8px;min-height:40px}

.timeline{position:relative;padding-left:24px;margin:12px 0 24px}
.timeline::before{content:'';position:absolute;left:8px;top:0;bottom:0;width:2px;background:var(--border)}
.tl-item{position:relative;margin-bottom:16px;padding-left:20px}
.tl-item::before{content:'';position:absolute;left:-20px;top:6px;width:10px;height:10px;border-radius:50%;background:var(--blue);border:2px solid var(--card)}
.tl-item:hover::before{background:var(--purple);transform:scale(1.3)}
.tl-date{font-size:0.78rem;font-weight:700;color:var(--blue)}
.tl-event{font-weight:600;font-size:0.92rem}
.tl-detail{font-size:0.82rem;color:var(--muted)}

.quiz-q{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:12px}
.quiz-q .question{font-weight:600;margin-bottom:10px}
.quiz-q label{display:block;padding:5px 0;font-size:0.9rem;cursor:pointer}
.quiz-q input[type="radio"]{margin-right:8px}
.quiz-result{margin-top:6px;font-size:0.82rem;font-weight:600;display:none}
.quiz-result.correct{display:block;color:var(--green)}
.quiz-result.wrong{display:block;color:var(--red)}
.quiz-submit{background:var(--green);color:#fff;border:none;border-radius:8px;padding:12px 30px;font-size:1rem;font-weight:600;cursor:pointer}
.quiz-submit:hover{background:#16a34a}
.quiz-score{margin-top:14px;font-size:1.1rem;font-weight:700}

.reading-list{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px 20px}
.reading-list li{margin-bottom:6px;font-size:0.9rem}
.reading-list .reason{color:var(--muted);font-size:0.82rem}

@media(max-width:600px){.areas-grid{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="container">
<h1>Research Trend Explorer</h1>
<p class="subtitle">Explore five frontier areas of LLM research. Click a card, expand subtopics, ELI5 anything.</p>

<h2>Research Areas</h2>
<div class="areas-grid" id="areas-grid"></div>
<div class="detail-panel" id="detail-panel"></div>

<h2>Compare Two Areas</h2>
<div class="compare-section">
<select id="compare-a"></select>
<span style="color:var(--muted)">vs</span>
<select id="compare-b"></select>
<button class="compare-btn" id="compare-btn">Compare</button>
<div class="compare-result" id="compare-result">Select two areas and click Compare.</div>
</div>

<h2>Trend Timeline</h2>
<div class="timeline" id="timeline"></div>

<h2>Quiz (5 Questions)</h2>
<div id="quiz-area"></div>
<button class="quiz-submit" id="quiz-submit">Check Answers</button>
<div class="quiz-score" id="quiz-score"></div>

<h2>Reading List</h2>
<div class="reading-list" id="reading-list"></div>
</div>

<script>
const AREAS = __AREAS_JSON__;
const TIMELINE = __TIMELINE_JSON__;
const QUIZ = __QUIZ_JSON__;
const READING = __READING_JSON__;
const areaKeys = Object.keys(AREAS);

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function renderAreas(){
  const grid=document.getElementById('areas-grid');
  grid.innerHTML=areaKeys.map((k,i)=>{
    const a=AREAS[k];
    const n=Object.keys(a.subtopics).length;
    return '<div class="area-card" data-i="'+i+'"><div class="icon">'+a.icon+'</div><div class="title">'+esc(a.title)+'</div><div class="count">'+n+' subtopics</div></div>';
  }).join('');
  grid.querySelectorAll('.area-card').forEach(card=>card.addEventListener('click',()=>showDetail(+card.dataset.i)));
}

function showDetail(idx){
  const k=areaKeys[idx], a=AREAS[k], panel=document.getElementById('detail-panel');
  const topics=Object.entries(a.subtopics);
  let html='<button class="close-btn" onclick="document.getElementById(\\'detail-panel\\').classList.remove(\\'active\\')">&times;</button>';
  html+='<h2 style="color:'+a.color+'">'+a.icon+' '+a.title+'</h2>';
  topics.forEach(([sk,sv],ti)=>{
    html+='<div class="subtopic" id="st-'+idx+'-'+ti+'">';
    html+='<div class="st-title" onclick="this.parentElement.classList.toggle(\\'open\\')">'+esc(sv.title)+'</div>';
    html+='<div class="st-body">';
    html+='<div class="detail">'+esc(sv.detail)+'</div>';
    if(sv.references&&sv.references.length) html+='<div class="refs">Refs: '+sv.references.map(r=>esc(r)).join('; ')+'</div>';
    html+='<div class="eli5-box" id="eli5-'+idx+'-'+ti+'">'+esc(sv.eli5)+'</div>';
    html+='<button class="eli5-toggle" onclick="document.getElementById(\\'eli5-'+idx+'-'+ti+'\\').classList.toggle(\\'show\\')">Simplify (ELI5)</button>';
    html+='</div></div>';
  });
  panel.innerHTML=html;
  panel.classList.add('active');
  panel.scrollIntoView({behavior:'smooth',block:'start'});
}

function renderCompare(){
  const sels=[document.getElementById('compare-a'),document.getElementById('compare-b')];
  sels.forEach(sel=>{sel.innerHTML=areaKeys.map((k,i)=>'<option value="'+i+'">'+esc(AREAS[k].title)+'</option>').join('');});
  sels[1].selectedIndex=1;
  document.getElementById('compare-btn').addEventListener('click',()=>{
    const i1=+sels[0].value, i2=+sels[1].value;
    if(i1===i2){document.getElementById('compare-result').textContent='Pick two different areas.';return;}
    const a1=areaKeys[i1],a2=areaKeys[i2],key=a1<a2?a1+'__'+a2:a2+'__'+a1;
    const text=(AREAS[a1]._comparisons&&AREAS[a1]._comparisons[key])||'No comparison data available.';
    document.getElementById('compare-result').textContent=text;
  });
}

function renderTimeline(){
  const el=document.getElementById('timeline');
  el.innerHTML=TIMELINE.map(t=>'<div class="tl-item"><div class="tl-date">'+esc(t.date)+'</div><div class="tl-event">'+esc(t.event)+'</div><div class="tl-detail">'+esc(t.detail)+'</div></div>').join('');
}

function renderQuiz(){
  const el=document.getElementById('quiz-area');
  el.innerHTML=QUIZ.map((q,qi)=>{
    let h='<div class="quiz-q"><div class="question">'+qi+1+'. '+esc(q.question)+'</div>';
    q.options.forEach((o,oi)=>{h+='<label><input type="radio" name="q'+qi+'" value="'+oi+'"> '+esc(o)+'</label>';});
    h+='<div class="quiz-result" id="qr-'+qi+'"></div></div>';
    return h;
  }).join('');
  document.getElementById('quiz-submit').addEventListener('click',()=>{
    let score=0;
    QUIZ.forEach((q,qi)=>{
      const sel=document.querySelector('input[name="q'+qi+'"]:checked');
      const res=document.getElementById('qr-'+qi);
      if(!sel){res.textContent='Not answered';res.className='quiz-result wrong';return;}
      if(+sel.value===q.answer){score++;res.textContent='Correct!';res.className='quiz-result correct';}
      else{res.textContent='Wrong. Answer: '+q.options[q.answer];res.className='quiz-result wrong';}
    });
    document.getElementById('quiz-score').textContent='Score: '+score+'/'+QUIZ.length;
  });
}

function renderReading(){
  let html='<ul>';
  Object.entries(READING).forEach(([area,list])=>{
    if(list&&list.length){
      html+='<li><strong>'+esc(AREAS[area]?AREAS[area].title:area)+'</strong><ul>';
      list.forEach(r=>{html+='<li>'+esc(r.title)+'<div class="reason">'+esc(r.reason)+'</div></li>';});
      html+='</ul></li>';
    }
  });
  html+='</ul>';
  document.getElementById('reading-list').innerHTML=html;
}

function init(){renderAreas();renderCompare();renderTimeline();renderQuiz();renderReading();}
window.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>
"""


def build_html(online: bool) -> str:
    """Build a self-contained interactive HTML explorer."""
    areas_json = json.dumps(AREAS, indent=None)
    timeline_json = json.dumps(TIMELINE)
    quiz_json = json.dumps(QUIZ)
    reading_json = json.dumps(READING_LIST_SUGGESTIONS)

    page = HTML_TEMPLATE
    page = page.replace("__AREAS_JSON__", areas_json)
    page = page.replace("__TIMELINE_JSON__", timeline_json)
    page = page.replace("__QUIZ_JSON__", quiz_json)
    page = page.replace("__READING_JSON__", reading_json)
    return page


# ---------- Main ----------


def main() -> None:
    parser = argparse.ArgumentParser(description="Part 11 Research Trends Explorer")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="skip opencode calls and use fallback content",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="generate a self-contained interactive HTML file",
    )
    args = parser.parse_args()
    online = not args.skip_llm

    print(f"Model: {MODEL}")
    print(f"LLM calls: {'enabled' if online else 'skipped'}")

    if args.html:
        page = build_html(online)
        html_path = os.path.join(os.path.dirname(__file__), "research_explorer.html")
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(page)
        print(f"HTML explorer written to: {html_path}")

    reading_list, quiz_score = run_cli(online)

    results_path = os.path.join(os.path.dirname(__file__), "part11_results.md")
    lines = [
        "# Part 11 — Research Trends Explorer Results",
        "",
        f"> **Model:** `{MODEL}`  ",
        f"> **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Reading List",
        "",
    ]
    if reading_list:
        lines.append(reading_list)
    else:
        lines.append("_No reading list generated during this session._")
    lines.extend(
        [
            "",
            "## Quiz Score",
            "",
            f"**{quiz_score} / {len(QUIZ)}**" if quiz_score else "_Quiz not taken._",
            "",
            "## Takeaway",
            "",
            "LLM research is moving in three directions: more capable (multimodal, "
            "agentic), more efficient (MoE, Mamba, RWKV), and more open (LLaMA, "
            "OLMo, LLM360). The field rewards staying current — follow the "
            "timelines and read the source papers.",
        ]
    )
    with open(results_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    print(f"Results saved to: {results_path}")
    print("DONE — Part 11 complete. Next: Part 12 (Neural Network Foundations)")


if __name__ == "__main__":
    main()
