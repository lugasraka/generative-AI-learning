# Part 9 — Real-World Agentic Systems

## Concept in 10 lines

- Three public systems to study: **NotebookLM**, **Perplexity**, **OpenAI DeepResearch**.
- **NotebookLM** — Q&A over your files. Mostly RAG + short-term memory. Sits between workflow and semi-autonomous.
- **Perplexity** — answer-engine on the open web. Web search + RAG + light planning. Semi-autonomous.
- **DeepResearch** — open-ended research with multi-step planning, iterative retrieval, multiple tools. Strongly autonomous.
- All three blend: planning, tool use, RAG, memory — in different proportions.
- Pick one and use its free version. Watch how much *you* control vs. how much *it* decides.
- You don't need their internals — observe the behavior and map it back to the patterns from earlier parts.

## Vibe-coding challenge

**Reverse-engineer one of the three.**

Pick one (NotebookLM, Perplexity, or DeepResearch — your call) and do this without writing any production code:

1. Use the free version. Pick a real task you'd actually use it for (e.g., *"Summarize my Q3 OKRs"*, *"Compare pricing of 3 SaaS tools"*, *"Research competitors in the X space"*).
2. Run it. Note:
   - What tools/capabilities did it seem to use?
   - How many steps did it take? Did you see iteration?
   - What memory/retrieval behavior did you notice?
   - Where did you have to intervene vs. let it run?
3. Write a 1-page breakdown in a new file `analysis.md` in this folder, mapping what you observed to the agentic concepts (tools, RAG, planning, memory, autonomy level).
4. Suggest 2-3 things you'd change or improve if you were building it.

> Bonus: try the *same* task in all three systems and compare the autonomy levels in a small table.

### How to start

Tell me one of:
- *"I'll pick NotebookLM — guide me on what to look for"*
- *"I'll pick Perplexity"*
- *"I'll pick DeepResearch"*
- *"Just give me a checklist of what to observe"*
