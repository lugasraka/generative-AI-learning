"""
Part 7 — Memory in agents: short-term (session) + long-term (semantic/episodic/procedural).

Storage is in-memory dicts. The point is the flow: what the agent "sees" when
combining both, and the difference between Session 1 (storing prefs) and
Session 2 (recalling them with empty short-term).

Run:  python memory_agent.py
"""

import sys
import textwrap

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")


# ---------- Storage backends ----------

# Short-term: list of turns, keyed by (user_id, session_id)
# Cleared when a new session starts.
SHORT_TERM: dict[tuple[str, str], list[dict]] = {}

# Long-term: per-user buckets of three flavors
#   semantic   — facts about the world / the user
#   episodic   — past actions / events
#   procedural — preferences / style
LONG_TERM: dict[str, dict[str, list[dict]]] = {}


def _lt(user_id: str) -> dict[str, list[dict]]:
    if user_id not in LONG_TERM:
        LONG_TERM[user_id] = {"semantic": [], "episodic": [], "procedural": []}
    return LONG_TERM[user_id]


def _st(user_id: str, session_id: str) -> list[dict]:
    return SHORT_TERM.setdefault((user_id, session_id), [])


# ---------- API ----------


VALID_TYPES = {"semantic", "episodic", "procedural"}


def remember(
    user_id: str, memory_type: str, content: str, key: str | None = None
) -> None:
    """Write a memory item to long-term storage."""
    if memory_type not in VALID_TYPES:
        raise ValueError(f"memory_type must be one of {VALID_TYPES}")
    _lt(user_id)[memory_type].append(
        {
            "key": key or content[:30],
            "value": content,
        }
    )


def forget(user_id: str, memory_type: str, key: str) -> bool:
    """Remove a memory item by key. Returns True if something was removed."""
    if memory_type not in VALID_TYPES:
        return False
    bucket = _lt(user_id)[memory_type]
    before = len(bucket)
    _lt(user_id)[memory_type] = [m for m in bucket if m["key"] != key]
    return len(_lt(user_id)[memory_type]) < before


def add_turn(user_id: str, session_id: str, role: str, content: str) -> None:
    """Append a turn to short-term memory for this session."""
    _st(user_id, session_id).append({"role": role, "content": content})


def new_session(user_id: str) -> str:
    """Start a fresh short-term session for this user. Returns the new session_id."""
    import uuid

    sid = uuid.uuid4().hex[:8]
    SHORT_TERM[(user_id, sid)] = []
    return sid


def recall(user_id: str, query: str) -> dict:
    """Pull everything relevant from long-term for this user.

    Naive retrieval: substring match of query words in memory values.
    Returns a dict of {memory_type: [items]}.
    """
    q_words = {w for w in query.lower().split() if len(w) > 2}
    out: dict[str, list[dict]] = {"semantic": [], "episodic": [], "procedural": []}
    for mem_type, items in _lt(user_id).items():
        for item in items:
            if q_words & set(item["value"].lower().split()):
                out[mem_type].append(item)
            elif mem_type == "procedural":
                # procedural prefs should surface often — include by default
                out[mem_type].append(item)
    return out


def get_context(user_id: str, session_id: str, query: str) -> dict:
    """The 'view' the agent has right now: short-term + recalled long-term."""
    return {
        "short_term": list(_st(user_id, session_id)),
        "long_term_recall": recall(user_id, query),
    }


# ---------- Display ----------


def banner(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def show_context(ctx: dict) -> None:
    print("  Short-term memory (this session):")
    if not ctx["short_term"]:
        print("    (empty)")
    for t in ctx["short_term"]:
        print(f"    {t['role']:>9}: {t['content']}")

    print("\n  Long-term recall (across sessions):")
    lt = ctx["long_term_recall"]
    for mem_type, items in lt.items():
        if items:
            print(f"    {mem_type}:")
            for it in items:
                print(f"      - [{it['key']}] {it['value']}")
        else:
            print(f"    {mem_type}: (none)")


# ---------- Simulation from the README ----------


def main() -> None:
    USER = "alice"

    banner("SESSION 1 — user shares preferences and past context")
    sid1 = "s1"
    add_turn(USER, sid1, "user", "Hey, can you help me draft a project update?")
    add_turn(USER, sid1, "assistant", "Sure — what's the update?")
    add_turn(USER, sid1, "user", "I prefer bullet points and short sentences.")
    remember(
        USER, "procedural", "I prefer bullet points and short sentences.", key="style"
    )
    remember(USER, "semantic", "Alice works on Project Northstar.", key="project")
    remember(USER, "episodic", "On 2026-01-15 Alice sent the Q4 update.", key="q4_sent")
    print(f"Context right now: {sid1}")
    show_context(get_context(USER, sid1, "draft a project update"))

    # ---------- New session: short-term cleared, long-term persists ----------

    banner("SESSION 2 — fresh session, but long-term memory persists")
    sid2 = "s2"  # empty short-term
    add_turn(USER, sid2, "user", "Summarize this article about remote work.")
    print(f"Context right now: {sid2}  (new session, short-term was empty)")
    show_context(get_context(USER, sid2, "summarize the article"))

    banner("SESSION 2 — user asks a follow-up; procedural style should be recalled")
    add_turn(
        USER,
        sid2,
        "assistant",
        "(summary of article, but I should respect the user's style)",
    )
    add_turn(USER, sid2, "user", "Now draft a project update for the team.")
    print(f"Context right now: {sid2}  (follow-up turn)")
    show_context(get_context(USER, sid2, "draft a project update"))

    # ---------- Bonus: forget ----------

    banner("BONUS — forget(): remove the Q4 episodic memory")
    print(f"Before forget: {len(LONG_TERM[USER]['episodic'])} episodic memories")
    removed = forget(USER, "episodic", "q4_sent")
    print(f"forget(episodic, 'q4_sent') returned: {removed}")
    print(f"After  forget: {len(LONG_TERM[USER]['episodic'])} episodic memories")
    print("\nRemaining long-term for alice:")
    for mem_type, items in LONG_TERM[USER].items():
        for it in items:
            print(f"  {mem_type:>11}: [{it['key']}] {it['value']}")


if __name__ == "__main__":
    main()
