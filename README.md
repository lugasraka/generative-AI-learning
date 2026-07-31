# Generative AI Learning

Lab companions for the courses in the [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) repo. Built so I actually retain the material.

## Why this fork

I don't retain things by reading them once. So next to every course in the original repo, I keep a lab folder with a vibe-coding challenge per chapter. Each one is small. I write a rubric, a dataset, a prompt, or a script, then run it and break it. That's the whole idea: turn the concept into something that runs.

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
| Applied LLMs Mastery 2024 | `Applied_LLMs_Mastery_2024/` |  | 11 weeks | Labs TBD | TBD |

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
└── Applied_LLMs_Mastery_2024/        # original course (read only)
```

## Rules

- **No API keys.** Everything runs through the opencode CLI or pure logic. Local only.
- **Ugly is fine.** The point is to learn the concept. Code that runs and teaches beats code that's clean and doesn't.
- **Problem first.** Each lab opens with a real problem. Architecture comes after.
- **Vibe code.** I drive. The assistant scaffolds. "Make it tighter", "add a column", "why did this fail" are the point.
- **One persona where it helps.** The evals labs use SoleMates (a DTC shoe retailer) across all 11 chapters so the work compounds.

## Setup

- `python3` (3.10+)
- The `opencode` CLI, or any local LLM runner

That's it. No `pip install`, no cloud. If a lab needs something extra, the chapter README says so.

## Progress

- [Agentic AI labs](./agentic_ai_crash_course_labs/PROGRESS.md)
- [AI Evals labs](./ai_evals_for_everyone_labs/PROGRESS.md)

## Credits

The course material in `agentic_ai_crash_course/`, `ai_evals_for_everyone/`, and `Applied_LLMs_Mastery_2024/` comes from [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) by [Aishwarya N R](https://github.com/aishwaryanr). This fork only adds lab companions on top. For the original reading experience, go to the source repo.
