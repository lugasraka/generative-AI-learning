# Generative AI Learning

Lab companions for the courses in the [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) repo. Built so I actually retain the material.

## Why this fork

I don't retain things by reading them once. So next to every course in the original repo, I keep a lab folder with a vibe-coding challenge per chapter. Each one is small. I write a rubric, a dataset, a prompt, or a script, then run it and break it. That's the whole idea: turn the concept into something that runs.

## Completed tracks

- **Agentic AI Crash Course** — 10 labs covering agents, tools, RAG, MCP, planning, memory, and multi-agent systems. Each part ships a runnable script.
- **AI Evals for Everyone** — 11 chapters building a full eval stack for SoleMates (a shoe retailer): reference datasets, code + LLM judge metrics, a 100-query production pilot, monitoring signals, and a capstone eval report.

## Tech stack

![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?logo=visual-studio-code&logoColor=white)
![opencode](https://img.shields.io/badge/opencode-CLI-000000?logo=terminal)
![MiniMax M3](https://img.shields.io/badge/MiniMax_M3-free-FF6B35)
![Mimo v2.5](https://img.shields.io/badge/Mimo_v2.5-free-6366F1)
![DeepSeek V4](https://img.shields.io/badge/DeepSeek_V4_free-4F46E5)
![MCP](https://img.shields.io/badge/MCP-protocol-00ADD8)

## How to use

1. Pick a track below.
2. Read a chapter or part in the original course folder.
3. Open the matching `*_labs` folder.
4. Read the chapter's `README.md`: short concept recap, then the challenge.
5. Build the thing. Iterate. Move on when it feels solid.
6. Tick the chapter off in the track's `PROGRESS.md`.

The original course text is untouched. Labs live in sibling folders so reading and building can happen side by side.

## Tracks

| Track | Course | Labs | Units | Status | Time per unit |
| --- | --- | --- | --- | --- | --- |
| Agentic AI Crash Course | `agentic_ai_crash_course/` | `agentic_ai_crash_course_labs/` | 10 parts | Labs done | 15-30 min |
| AI Evals for Everyone | `ai_evals_for_everyone/` | `ai_evals_for_everyone_labs/` | 11 chapters | Labs done | 20-40 min |
| Applied LLMs Mastery 2024 | `Applied_LLMs_Mastery_2024/` | `applied_llms_mastery_labs/` | 12 parts | 6/12 done | 15-30 min |

Finish one track before starting another. They don't share a scenario, so jumping around breaks the compounding.

## Repo layout

```
.
├── agentic_ai_crash_course/          # original course (read only)
├── agentic_ai_crash_course_labs/     # my labs
│   ├── README.md
│   ├── PROGRESS.md
│   ├── part1_what_are_ai_agents_anyway/
│   ├── ...
│   └── part10_ai_agent_lessons_whats_ahead/
├── ai_evals_for_everyone/            # original course (read only)
├── ai_evals_for_everyone_labs/       # my labs
│   ├── README.md
│   ├── PROGRESS.md
│   ├── chapter1_wth_are_ai_evals/
│   ├── ...
│   └── chapter11_capstone_eval_report/
├── Applied_LLMs_Mastery_2024/        # original course (read only)
├── applied_llms_mastery_labs/        # my labs
│   ├── README.md
│   ├── PROGRESS.md
│   ├── part1_llm_foundations_and_use_cases/
│   ├── ...
│   └── part12_neural_network_foundations/
```

## Rules

- **No API keys.** Everything runs through the opencode CLI or pure logic. Local only.
- **Ugly is fine.** The point is to learn the concept. Code that runs and teaches beats code that's clean and doesn't.
- **Problem first.** Each lab opens with a real problem. Architecture comes after.
- **Vibe code.** I drive. The assistant scaffolds. "Make it tighter", "add a column", "why did this fail" are the point.
- **One persona where it helps.** The evals labs use SoleMates (a DTC shoe retailer) across all 11 chapters so the work compounds.

## Progress

- [Agentic AI labs](./agentic_ai_crash_course_labs/PROGRESS.md)
- [AI Evals labs](./ai_evals_for_everyone_labs/PROGRESS.md)
- [Applied LLMs labs](./applied_llms_mastery_labs/PROGRESS.md)

## Author

**Raka Adrianto** — [LinkedIn](https://www.linkedin.com/in/lugasraka/)

## Credits

The course material in `agentic_ai_crash_course/`, `ai_evals_for_everyone/`, and `Applied_LLMs_Mastery_2024/` comes from [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) by [Aishwarya N R](https://github.com/aishwaryanr). This fork only adds lab companions on top. For the original reading experience, go to the source repo.
