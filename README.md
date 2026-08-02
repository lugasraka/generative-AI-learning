# Generative AI Learning

Lab companions for [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide). I don't retain things by reading once, so I keep a vibe-coding challenge per chapter — turn the concept into something that runs.

## Tracks

6 tracks covering agents, evals, LLMs, RAG, and agent security — 54 parts across 3 completed and 3 in-progress courses.

| Track | Course | Labs | Units | Status | Time per unit |
| --- | --- | --- | --- | --- | --- |
| Agentic AI Crash Course | `agentic_ai_crash_course/` | `agentic_ai_crash_course_labs/` | 10 parts | Labs done | 15-30 min |
| AI Evals for Everyone | `ai_evals_for_everyone/` | `ai_evals_for_everyone_labs/` | 11 chapters | Labs done | 20-40 min |
| Applied LLMs Mastery 2024 | `Applied_LLMs_Mastery_2024/` | `applied_llms_mastery_labs/` | 12 parts | Labs done | 15-30 min |
| Agentic RAG 101 | `agentic_rag_101/` | `agentic_rag_101_labs/` | 6 parts | In progress | 10-15 min |
| LLM Agents 101 | `agents_101/` | `agents_101_labs/` | 6 parts | In progress | 10-20 min |
| Securing Agentic AI | `securing_agentic_ai_systems/` | `securing_agentic_ai_systems_labs/` | 9 parts | In progress | 15-20 min |

Finish one track before starting another. They don't share a scenario, so jumping around breaks the compounding.

## How to use

1. Pick a track → read a part in the course folder → open the matching `*_labs` folder.
2. Read the README, build the challenge, iterate.
3. Tick it off in PROGRESS.md.

## Repo layout

Each track follows the same pattern: a read-only course folder alongside a `*_labs/` folder with one subdirectory per part/chapter containing a `README.md` (concept recap + challenge) and a runnable script.

```
.
├── agentic_ai_crash_course/          # original course (read only)
├── agentic_ai_crash_course_labs/     # my labs
│   ├── README.md
│   ├── PROGRESS.md
│   ├── part1_what_are_ai_agents_anyway/
│   └── ...
├── agentic_rag_101/                  # self-paced course (6 parts)
├── agentic_rag_101_labs/             # my labs (scaffold only)
└── ...
```

## Rules

- **No API keys.** Everything runs through the opencode CLI or pure logic. Local only.
- **Ugly is fine.** The point is to learn the concept. Code that runs and teaches beats code that's clean and doesn't.
- **Problem first.** Each lab opens with a real problem. Architecture comes after.
- **Vibe code.** I drive. The assistant scaffolds. "Make it tighter", "add a column", "why did this fail" are the point.

## Progress

- [Agentic AI labs](./agentic_ai_crash_course_labs/PROGRESS.md)
- [AI Evals labs](./ai_evals_for_everyone_labs/PROGRESS.md)
- [Applied LLMs labs](./applied_llms_mastery_labs/PROGRESS.md)
- [Agents 101 labs](./agents_101_labs/PROGRESS.md)
- [Agentic RAG 101 labs](./agentic_rag_101_labs/PROGRESS.md)
- [Securing Agentic AI labs](./securing_agentic_ai_systems_labs/PROGRESS.md)

## Certificates

- **AI Evals for Everyone** — [Certificate of Completion](./certificates/ai-evals-for-everyone-certificate.pdf) (completed 8/1/2026, ID `2LALOO-CE000968`)

## Author

**Raka Adrianto** — [LinkedIn](https://www.linkedin.com/in/lugasraka/)

## Credits

Course material in `agentic_ai_crash_course/`, `ai_evals_for_everyone/`, and `Applied_LLMs_Mastery_2024/` comes from [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) by [Aishwarya N R](https://github.com/aishwaryanr). This fork adds lab companions on top.
