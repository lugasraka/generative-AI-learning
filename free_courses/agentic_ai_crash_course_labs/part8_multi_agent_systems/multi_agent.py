"""
Part 8 — Multi-agent systems: writer + critic loop (flat) + manager (hierarchical bonus).

Flat pattern (default): Writer drafts -> Critic critiques -> Writer revises ...
Hierarchical pattern (bonus): A Manager decides whether to loop back to Writer,
or end the loop, based on the Critic's verdict.

Run:  python multi_agent.py
"""

import os
import re
import subprocess
import sys

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/minimax-m3")


# ---------- LLM helper ----------


def ask_llm(system: str, user_msg: str) -> str:
    """Send a single-turn prompt to opencode CLI."""
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, f"{system}\n\n{user_msg}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Agent prompts ----------

WRITER_SYSTEM = """You are a Writer. Produce a short, well-structured paragraph on the topic.

Rules:
- One paragraph, 80-130 words.
- Clear topic sentence in the first line.
- No preamble, no explanation, no "Here is the draft" — just the paragraph.
- If you receive a previous draft and critique, REVISE it concretely:
  address each critique point in the next draft.
- Do not repeat the critique back to the user.
"""

CRITIC_SYSTEM = """You are a Critic. Read the Writer's draft and respond with 1-2
short, specific, actionable suggestions for improvement.

Rules:
- Be concrete: name the sentence or claim you would change.
- If the draft is already clear, accurate, and well-structured, reply with
  exactly: LOOKS_GOOD
- Do not rewrite the draft. Only suggest changes.
- Keep your response under 60 words.
"""

MANAGER_SYSTEM = """You are a Manager overseeing a Writer and a Critic.

You see the latest draft and the latest critique.
Reply with EXACTLY one of:
  REVISE   - if the critique has actionable points to address
  END      - if the critique was LOOKS_GOOD or the draft is good enough

No other text. Just the single word on the first line.
"""


# ---------- Agents ----------


def writer(
    topic: str, prior_draft: str | None = None, critique: str | None = None
) -> str:
    user_msg = f"Topic: {topic}"
    if prior_draft:
        user_msg += f"\n\nPrevious draft:\n{prior_draft}"
    if critique:
        user_msg += f"\n\nCritique to address:\n{critique}"
    return ask_llm(WRITER_SYSTEM, user_msg)


def critic(draft: str) -> str:
    return ask_llm(CRITIC_SYSTEM, f"Draft:\n{draft}")


def manager(latest_draft: str, latest_critique: str) -> str:
    reply = ask_llm(
        MANAGER_SYSTEM,
        f"Latest draft:\n{latest_draft}\n\nLatest critique:\n{latest_critique}",
    )
    return reply.strip().splitlines()[0].strip().upper()


# ---------- Flat loop ----------


def flat_loop(topic: str, max_rounds: int = 3) -> list[dict]:
    """Writer <-> Critic, no manager. Loop until LOOKS_GOOD or max_rounds."""
    transcript: list[dict] = []
    draft: str | None = None
    critique: str | None = None

    for r in range(1, max_rounds + 1):
        draft = writer(topic, prior_draft=draft, critique=critique)
        transcript.append({"round": r, "speaker": "writer", "text": draft})

        critique = critic(draft)
        transcript.append({"round": r, "speaker": "critic", "text": critique})

        if "LOOKS_GOOD" in critique.upper():
            transcript.append(
                {
                    "round": r,
                    "speaker": "system",
                    "text": "(critic approved; loop ends)",
                }
            )
            break
    else:
        transcript.append(
            {"round": max_rounds, "speaker": "system", "text": "(hit max_rounds)"}
        )

    return transcript


# ---------- Hierarchical loop (bonus) ----------


def hierarchical_loop(topic: str, max_rounds: int = 3) -> list[dict]:
    """Writer <-> Critic, but a Manager decides whether to loop or end."""
    transcript: list[dict] = []
    draft: str | None = None
    critique: str | None = None
    decision: str | None = None

    for r in range(1, max_rounds + 1):
        draft = writer(topic, prior_draft=draft, critique=critique)
        transcript.append({"round": r, "speaker": "writer", "text": draft})

        critique = critic(draft)
        transcript.append({"round": r, "speaker": "critic", "text": critique})

        decision = manager(draft, critique)
        transcript.append({"round": r, "speaker": "manager", "text": decision})

        if decision == "END":
            break
    else:
        if decision != "END":
            transcript.append(
                {"round": max_rounds, "speaker": "system", "text": "(hit max_rounds)"}
            )

    return transcript


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def show_transcript(t: list[dict]) -> None:
    for entry in t:
        r = entry["round"]
        sp = entry["speaker"].upper()
        print(f"  Round {r}  [{sp}]")
        for line in entry["text"].splitlines():
            print(f"    | {line}")
        print()


# ---------- Demo ----------

if __name__ == "__main__":
    print(f"Model: {MODEL}\n")
    topic = "Why short, iterative loops matter in agent design"

    banner(f"FLAT PATTERN — Writer <-> Critic (max 3 rounds)\nTopic: {topic}")
    flat = flat_loop(topic, max_rounds=3)
    show_transcript(flat)

    banner(
        f"HIERARCHICAL PATTERN (bonus) — Manager decides loop vs. end\nTopic: {topic}"
    )
    hier = hierarchical_loop(topic, max_rounds=3)
    show_transcript(hier)
