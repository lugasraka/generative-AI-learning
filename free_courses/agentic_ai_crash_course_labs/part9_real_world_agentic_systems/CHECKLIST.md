# Part 9 — Real-World Agentic Systems: Reverse-Engineer Checklist

Pick **one** of: NotebookLM, Perplexity, or OpenAI DeepResearch (free versions all work).
Run it on a **real task you actually care about** — pick something you already know
the answer to, so you can spot when the system gets it wrong.

---

## Step 0 — Pick a real task

Good tasks (pick one you have a stake in):
- A product comparison: *"Compare pricing and features of [Tool A], [Tool B], [Tool C] for [your use case]."* — you already know the rough landscape.
- A research question: *"What are the main differences between [X] and [Y] in 2026?"* — pick a domain you follow.
- A summary of something public: *"Summarize the latest [annual report / RFC / paper / changelog] for [X]."* — something you can verify.
- A "what should I do" question: *"I want to [learn X / pick a Y / start a Z]. Give me a 2-week plan."* — you'll know if the plan is realistic.

**Write the task here:**

```
Task: _____________________________________________________________
```

---

## Step 1 — Run it and observe

Use the free version. While it runs, watch for these signals:

### 1a. What tools/capabilities did it seem to use?
- Did it search the web? (you'll see search queries or sources cited)
- Did it open/read specific URLs or docs?
- Did it generate any structured intermediate output (a plan, a list, a table) before the final answer?
- Did it seem to use a code interpreter or a calculator?
- Did it ask you a clarifying question before starting?

```
Tools observed: ____________________________________________________
```

### 1b. How many steps did it take?
- Single shot (one answer, no iteration you can see)?
- A few discrete steps (plan -> retrieve -> write)?
- Heavy iteration (multiple retrieves, drafts, self-corrections)?

```
Steps observed: ____________________________________________________
```

### 1c. Memory / retrieval behavior
- Did it seem to remember earlier turns in the same session?
- Did it cite specific sources? How many? Are they real?
- Did it retrieve the same source multiple times (sign of agentic RAG)?
- Did it seem to have any cross-session memory (e.g., preferences)?

```
Memory/retrieval: __________________________________________________
```

### 1d. Where did you intervene vs. let it run?
- Did you have to rephrase the prompt to get a useful answer?
- Did you stop it early? Why?
- Did you edit / correct its output?

```
Interventions: _____________________________________________________
```

---

## Step 2 — Map back to agentic concepts

Fill in the row for the system you tested. Mark H/M/L for how heavily it relies on each.

| Concept                | How this system used it | H/M/L |
|------------------------|-------------------------|-------|
| **Tool use**           |                         |       |
| **RAG**                |                         |       |
| **Agentic RAG** (multi-pass retrieval) |            |       |
| **Planning** (explicit plan visible?) |              |       |
| **Memory — short-term** |                        |       |
| **Memory — long-term** |                         |       |
| **Human-in-the-loop**  |                         |       |
| **Autonomy level** (1=rule, 2=workflow, 3=semi-auto, 4=auto) |  | |

---

## Step 3 — 2-3 things I'd change or improve

Think like a builder:

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

---

## Bonus — Compare all three

Run the **same task** in all three systems and fill in:

| System         | Autonomy (1-4) | Tools used | Did you intervene? | One-line verdict |
|----------------|----------------|------------|--------------------|------------------|
| NotebookLM     |                |            |                    |                  |
| Perplexity     |                |            |                    |                  |
| DeepResearch   |                |            |                    |                  |

---

## After you fill this in

When you're done, the writeup becomes your `analysis.md`. The structure is
already here — just add your notes inline. Or, if you want me to convert
this into a polished `analysis.md` after you've tested, paste your filled-in
notes and I'll format it.

---

## Suggested starter tasks (pick one)

1. **Tools comparison** — *"Compare [Linear], [Jira], and [GitHub Issues] for a 5-person startup's bug tracking in 2026."* You probably have opinions already.
2. **Domain research** — *"What are the main differences between [vector DB] and [Postgres with pgvector] for a small RAG app in 2026?"* — there's a real landscape to map.
3. **Public report summary** — Pick any annual report / changelog / RFC you have on hand. You'll know when the summary is wrong.
4. **Personal decision** — *"I want to learn [Rust / system design / etc.] from scratch. Give me a 4-week plan."* — you'll instantly know if the plan is realistic.
