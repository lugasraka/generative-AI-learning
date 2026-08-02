"""
Part 3 — Multi-Agent Systems: Writer + Critic Loop

Builds a 2-agent system with a flat cooperative pattern. The Writer
generates text, the Critic evaluates it, and they iterate until quality
is acceptable or max rounds are reached.

Run:  python writer_critic_loop.py
"""

import sys
import re
import random


# ---------- Quality criteria ----------

FILLER_WORDS = {"very", "really", "just", "basically", "actually", "quite", "somewhat"}


def count_filler(text: str) -> int:
    words = text.lower().split()
    return sum(1 for w in words if w.strip(".,!?;:") in FILLER_WORDS)


def has_specifics(text: str) -> bool:
    """Check for numbers, proper nouns, or concrete details."""
    return bool(re.search(r"\d+", text)) or bool(re.search(r"[A-Z][a-z]+", text))


def word_count(text: str) -> int:
    return len(text.split())


def quality_score(text: str) -> int:
    """Score 0-100 based on simple heuristics."""
    score = 100
    fillers = count_filler(text)
    score -= fillers * 10
    if not has_specifics(text):
        score -= 20
    wc = word_count(text)
    if wc < 10:
        score -= 20
    elif wc > 80:
        score -= 10
    if text.count(".") < 2:
        score -= 10
    return max(0, min(100, score))


# ---------- Writer agent ----------

TOPIC_TEMPLATES = {
    "python": [
        "Python is a versatile language used in {domain}. "
        "It has {feature} which makes it popular among {audience}.",
        "When building {project}, Python offers {benefit}. "
        "The ecosystem includes {tool} for {use_case}.",
    ],
    "agents": [
        "AI agents combine {component} with {capability} to {outcome}. "
        "The key challenge is {challenge}.",
        "Multi-agent systems use {pattern} to {goal}. "
        "This approach works well for {scenario}.",
    ],
    "default": [
        "{topic} is an important area in {field}. "
        "Key aspects include {aspect1} and {aspect2}.",
        "Understanding {topic} requires {requirement}. The main benefit is {benefit}.",
    ],
}

FILL_INS = {
    "domain": ["web development", "data science", "automation", "machine learning"],
    "feature": [
        "simple syntax",
        "a rich standard library",
        "dynamic typing",
        "list comprehensions",
    ],
    "audience": ["developers", "researchers", "data engineers", "hobbyists"],
    "project": ["an API", "a data pipeline", "a CLI tool", "a web app"],
    "benefit": ["rapid prototyping", "strong community support", "extensive libraries"],
    "tool": ["FastAPI", "pandas", "pytest", "Django"],
    "use_case": ["building APIs", "data analysis", "testing", "web development"],
    "component": ["language models", "tool access", "memory systems", "planning loops"],
    "capability": ["reasoning", "retrieval", "code execution", "web search"],
    "outcome": ["solve complex tasks", "automate workflows", "answer questions"],
    "challenge": ["coordination", "context management", "evaluation", "safety"],
    "pattern": ["hierarchical delegation", "peer-to-peer debate", "specialized roles"],
    "goal": ["divide and conquer", "parallelize work", "combine perspectives"],
    "scenario": ["enterprise workflows", "research tasks", "creative projects"],
    "topic": ["this subject", "the topic", "the concept"],
    "field": ["computer science", "AI", "software engineering"],
    "aspect1": ["theory", "practice", "history", "applications"],
    "aspect2": ["tools", "methods", "case studies", "future trends"],
    "requirement": ["hands-on practice", "reading papers", "building projects"],
}


def writer_generate(topic: str, feedback: str = "") -> str:
    """Generate text based on topic and optional critic feedback."""
    templates = TOPIC_TEMPLATES.get(topic, TOPIC_TEMPLATES["default"])
    template = random.choice(templates)

    def fill(match: "re.Match[str]") -> str:
        key = match.group(1)
        options = FILL_INS.get(key, ["X"])
        return random.choice(options)

    text = re.sub(r"\{(\w+)\}", fill, template)

    # If we have feedback, try to improve
    if feedback:
        if "specifics" in feedback.lower() or "number" in feedback.lower():
            text = f"For example, in 2025, {text[0].lower() + text[1:]}"
        if "filler" in feedback.lower():
            for filler in FILLER_WORDS:
                text = text.replace(f" {filler} ", " ")

    return text


# ---------- Critic agent ----------


def critic_evaluate(text: str) -> dict:
    """Evaluate text and return score + feedback."""
    score = quality_score(text)
    feedback_parts = []
    fillers = count_filler(text)
    if fillers > 0:
        feedback_parts.append(f"Remove {fillers} filler word(s)")
    if not has_specifics(text):
        feedback_parts.append("Add specific details (numbers, names, examples)")
    if word_count(text) < 15:
        feedback_parts.append("Expand with more detail")
    if score >= 80:
        feedback_parts.append("Looks good!")

    return {
        "score": score,
        "feedback": "; ".join(feedback_parts) if feedback_parts else "No issues found",
        "approved": score >= 80,
    }


# ---------- Multi-agent loop ----------


def run_writer_critic(topic: str, max_rounds: int = 3) -> dict:
    """Run the writer-critic loop for a given topic."""
    transcript: list[dict] = []
    current_text = ""
    feedback = ""

    for round_num in range(1, max_rounds + 1):
        # Writer generates
        current_text = writer_generate(topic, feedback)
        word_changes = word_count(current_text)

        # Critic evaluates
        eval_result = critic_evaluate(current_text)

        entry = {
            "round": round_num,
            "writer_output": current_text,
            "critic_score": eval_result["score"],
            "critic_feedback": eval_result["feedback"],
            "approved": eval_result["approved"],
            "word_count": word_changes,
        }
        transcript.append(entry)

        if eval_result["approved"]:
            break

        feedback = eval_result["feedback"]

    return {
        "topic": topic,
        "transcript": transcript,
        "final_text": current_text,
        "final_score": transcript[-1]["critic_score"],
        "rounds": len(transcript),
    }


# ---------- Display ----------


def print_transcript(result: dict) -> None:
    topic = result["topic"]
    print(f"\n{'=' * 60}")
    print(f"  WRITER + CRITIC LOOP — Topic: {topic}")
    print(f"{'=' * 60}")

    for entry in result["transcript"]:
        rnd = entry["round"]
        print(f"\n  --- Round {rnd} ---")
        print(f'  Writer:  "{entry["writer_output"]}"')
        print(
            f"  Critic:  score={entry['critic_score']}/100 | {entry['critic_feedback']}"
        )
        if entry["approved"]:
            print(f"  >> APPROVED")

    print(f"\n{'=' * 60}")
    print(
        f"  RESULT: {result['rounds']} round(s), final score: {result['final_score']}/100"
    )
    print(f'  FINAL TEXT: "{result["final_text"]}"')
    print(f"{'=' * 60}")


# ---------- Main ----------


def main() -> None:
    print("=" * 60)
    print("  MULTI-AGENT SYSTEMS — Writer + Critic Loop")
    print("=" * 60)

    topics = ["python", "agents"]
    all_results = []

    for topic in topics:
        result = run_writer_critic(topic, max_rounds=3)
        all_results.append(result)
        print_transcript(result)

    # Summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    for r in all_results:
        print(
            f"  Topic: {r['topic']:12s} | Rounds: {r['rounds']} | Final score: {r['final_score']}"
        )
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
