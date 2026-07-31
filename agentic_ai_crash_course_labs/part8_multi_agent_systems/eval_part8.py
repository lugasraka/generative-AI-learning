"""
Part 10 — Eval harness for the Part 8 multi-agent (writer + critic) system.

Test cases assert:
  - Writer + Critic both produced output
  - Loop terminated within max_rounds (didn't hit the cap)
  - Final draft is non-empty and above a minimum length
  - Flat loop: must end with either LOOKS_GOOD or max_rounds
  - Hierarchical loop: Manager decided END or REVISE consistently

Run:  python eval_part8.py
"""

import json
import os
import subprocess
import sys
import time

# Force UTF-8 stdout on Windows
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/minimax-m3")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "eval_part8_results.json")


# ---------- LLM helpers ----------

WRITER_SYSTEM = """You are a Writer. Produce a short, well-structured paragraph on the topic.

Rules:
- One paragraph, 80-130 words.
- Clear topic sentence in the first line.
- No preamble, no explanation, no "Here is the draft" — just the paragraph.
- If you receive a previous draft and critique, REVISE it concretely.
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


def ask_llm(system: str, user_msg: str) -> str:
    result = subprocess.run(
        ["opencode", "run", "-m", MODEL, f"{system}\n\n{user_msg}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


# ---------- Agents ----------


def writer(topic, prior_draft=None, critique=None):
    user_msg = f"Topic: {topic}"
    if prior_draft:
        user_msg += f"\n\nPrevious draft:\n{prior_draft}"
    if critique:
        user_msg += f"\n\nCritique to address:\n{critique}"
    return ask_llm(WRITER_SYSTEM, user_msg)


def critic(draft):
    return ask_llm(CRITIC_SYSTEM, f"Draft:\n{draft}")


def manager(latest_draft, latest_critique):
    reply = ask_llm(
        MANAGER_SYSTEM,
        f"Latest draft:\n{latest_draft}\n\nLatest critique:\n{latest_critique}",
    )
    return reply.strip().splitlines()[0].strip().upper()


# ---------- Loops ----------


def flat_loop(topic, max_rounds=3):
    transcript = []
    draft = None
    critique = None
    end_reason = "max_rounds"
    for r in range(1, max_rounds + 1):
        draft = writer(topic, prior_draft=draft, critique=critique)
        if draft.startswith("[opencode error]"):
            return {
                "transcript": transcript,
                "final": draft,
                "rounds": r,
                "end_reason": "infra_error",
            }
        transcript.append(("writer", draft, r))
        critique = critic(draft)
        if critique.startswith("[opencode error]"):
            return {
                "transcript": transcript,
                "final": critique,
                "rounds": r,
                "end_reason": "infra_error",
            }
        transcript.append(("critic", critique, r))
        if "LOOKS_GOOD" in critique.upper():
            end_reason = "looks_good"
            break
    return {
        "transcript": transcript,
        "final": draft,
        "rounds": len([t for t in transcript if t[0] == "writer"]),
        "end_reason": end_reason,
    }


def hierarchical_loop(topic, max_rounds=3):
    transcript = []
    draft = None
    critique = None
    end_reason = "max_rounds"
    for r in range(1, max_rounds + 1):
        draft = writer(topic, prior_draft=draft, critique=critique)
        if draft.startswith("[opencode error]"):
            return {
                "transcript": transcript,
                "final": draft,
                "rounds": r,
                "end_reason": "infra_error",
            }
        transcript.append(("writer", draft, r))
        critique = critic(draft)
        if critique.startswith("[opencode error]"):
            return {
                "transcript": transcript,
                "final": critique,
                "rounds": r,
                "end_reason": "infra_error",
            }
        transcript.append(("critic", critique, r))
        decision = manager(draft, critique)
        if decision.startswith("[opencode error]"):
            return {
                "transcript": transcript,
                "final": decision,
                "rounds": r,
                "end_reason": "infra_error",
            }
        transcript.append(("manager", decision, r))
        if decision == "END":
            end_reason = "manager_end"
            break
    return {
        "transcript": transcript,
        "final": draft,
        "rounds": len([t for t in transcript if t[0] == "writer"]),
        "end_reason": end_reason,
    }


# ---------- Test cases ----------


TEST_CASES = [
    {
        "id": "flat_short_topic",
        "topic": "Why short, iterative loops matter in agent design",
        "pattern": "flat",
        "min_words": 60,
        "max_words": 200,
    },
    {
        "id": "flat_workflow_topic",
        "topic": "The value of starting with the problem before picking the architecture",
        "pattern": "flat",
        "min_words": 60,
        "max_words": 200,
    },
    {
        "id": "hier_short_topic",
        "topic": "Why short, iterative loops matter in agent design",
        "pattern": "hierarchical",
        "min_words": 60,
        "max_words": 200,
    },
]


# ---------- Eval runner ----------


def evaluate_case(case):
    started = time.time()
    fn = flat_loop if case["pattern"] == "flat" else hierarchical_loop
    result = fn(case["topic"], max_rounds=3)
    elapsed = time.time() - started

    final = result["final"]
    final_word_count = len(final.split()) if final and not final.startswith("[") else 0

    checks = []

    # 1. Final draft is non-empty and long enough
    ok = final_word_count >= case["min_words"]
    checks.append(
        (
            f"final has >= {case['min_words']} words",
            ok,
            f"got {final_word_count} words" if not ok else "",
        )
    )

    # 2. Final draft isn't ridiculously over-long
    ok = final_word_count <= case["max_words"]
    checks.append(
        (
            f"final has <= {case['max_words']} words",
            ok,
            f"got {final_word_count} words" if not ok else "",
        )
    )

    # 3. Loop didn't hit infra error
    ok = result["end_reason"] != "infra_error"
    checks.append(
        (
            "no infra error",
            ok,
            result["final"][:80] if not ok else "",
        )
    )

    # 4. At least one writer + critic exchange happened
    writers = [t for t in result["transcript"] if t[0] == "writer"]
    critics = [t for t in result["transcript"] if t[0] == "critic"]
    ok = len(writers) >= 1 and len(critics) >= 1
    checks.append(
        (
            "at least 1 writer+critic round",
            ok,
            f"writers={len(writers)}, critics={len(critics)}" if not ok else "",
        )
    )

    # 5. Pattern-specific termination
    if case["pattern"] == "flat":
        ok = result["end_reason"] in {"looks_good", "max_rounds"}
        checks.append(
            (
                "flat loop terminated (looks_good or max_rounds)",
                ok,
                f"end_reason={result['end_reason']}" if not ok else "",
            )
        )
    else:
        ok = result["end_reason"] in {"manager_end", "max_rounds"}
        checks.append(
            (
                "hierarchical loop terminated (manager_end or max_rounds)",
                ok,
                f"end_reason={result['end_reason']}" if not ok else "",
            )
        )

    # 6. Hierarchical only: manager actually returned a valid decision in the last round
    if case["pattern"] == "hierarchical":
        mgr_decisions = [t[1] for t in result["transcript"] if t[0] == "manager"]
        ok = all(d in {"REVISE", "END"} for d in mgr_decisions)
        checks.append(
            (
                "manager decisions are REVISE/END only",
                ok,
                f"decisions={mgr_decisions}" if not ok else "",
            )
        )

    passed = all(c[1] for c in checks)
    return {
        "id": case["id"],
        "pattern": case["pattern"],
        "topic": case["topic"],
        "rounds": result["rounds"],
        "end_reason": result["end_reason"],
        "final_word_count": final_word_count,
        "elapsed_s": round(elapsed, 2),
        "checks": [{"name": n, "ok": ok, "note": note} for n, ok, note in checks],
        "passed": passed,
        "final": final,
    }


def print_table(results):
    print()
    print(
        f"{'ID':<22} {'PATTERN':<13} {'PASS/FAIL':<10} {'ROUNDS':<7} {'WORDS':<6} {'END':<14} {'TIME'}"
    )
    print("-" * 90)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"{r['id']:<22} {r['pattern']:<13} {status:<10} {r['rounds']:<7} {r['final_word_count']:<6} {r['end_reason']:<14} {r['elapsed_s']}s"
        )
    print()
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"Summary: {passed}/{total} passed ({100 * passed / total:.0f}%)")
    print()
    for r in results:
        if not r["passed"]:
            print(
                f"  FAIL: {r['id']}  (pattern: {r['pattern']}, rounds: {r['rounds']}, end: {r['end_reason']})"
            )
            for c in r["checks"]:
                if not c["ok"]:
                    print(f"     - {c['name']}: {c['note']}")
            print(f"     final: {r['final'][:150]!r}")


# ---------- Main ----------


if __name__ == "__main__":
    print(f"Model: {MODEL}\n")
    print(f"Running {len(TEST_CASES)} test cases (max 3 rounds each, may be slow)...\n")

    results = []
    for case in TEST_CASES:
        print(f"  -> {case['id']} ({case['pattern']}) ...", end="", flush=True)
        r = evaluate_case(case)
        results.append(r)
        print(
            f" {'PASS' if r['passed'] else 'FAIL'}  ({r['elapsed_s']}s, {r['rounds']} rounds)"
        )

    print_table(results)

    log = {
        "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
        },
        "results": [
            {k: v for k, v in r.items() if k not in ("checks", "final", "topic")}
            for r in results
        ],
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print(f"Results saved to {RESULTS_PATH}")
