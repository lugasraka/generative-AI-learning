"""
SoleMates — Generate a 1-page printable PDF of the eval cheat sheet.

Strategy: condense the 35-term cheat sheet to the essentials that fit
on a single Letter page. Drops the glossary (35 terms) and keeps:
  - Title + subtitle
  - 5 use-most terms (1 line each)
  - 3 anti-patterns (1 line each)
  - 4-step mental model
  - 1 thing to remember
  - 3 questions before shipping a metric
  - 3 things I still don't get (learning list)

Output: eval_cheatsheet_one_pager.pdf

Usage:
  python make_one_pager.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepInFrame,
)
from pathlib import Path

HERE = Path(__file__).parent
OUTPUT_PDF = HERE / "eval_cheatsheet_one_pager.pdf"

# Colors
NAVY = HexColor("#1a3a5c")
SLATE = HexColor("#3a4a5c")
RED = HexColor("#a23a3a")
GREEN = HexColor("#2a6a3a")
GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#eeeeee")


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontSize=18,
            textColor=NAVY,
            spaceAfter=2,
            leading=20,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontSize=9,
            textColor=GRAY,
            spaceAfter=10,
            leading=11,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=11,
            textColor=NAVY,
            spaceBefore=6,
            spaceAfter=3,
            leading=13,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=SLATE,
            spaceAfter=2,
            leading=11,
        ),
        "body_bold": ParagraphStyle(
            "body_bold",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=NAVY,
            spaceAfter=2,
            leading=11,
            fontName="Helvetica-Bold",
        ),
        "body_italic": ParagraphStyle(
            "body_italic",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=GRAY,
            spaceAfter=2,
            leading=11,
            fontName="Helvetica-Oblique",
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=base["Normal"],
            fontSize=11,
            textColor=RED,
            spaceAfter=2,
            leading=13,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
        ),
    }


def build_story(styles):
    story = []

    # Title
    story.append(Paragraph("SoleMates AI Eval Cheat Sheet", styles["title"]))
    story.append(
        Paragraph(
            "v0.1 — One-page printable. Full 35-term glossary in <code>eval_cheatsheet.md</code>.",
            styles["subtitle"],
        )
    )

    # Section 1: 5 use-most terms
    story.append(Paragraph("5 Terms I Use Most", styles["h2"]))
    terms = [
        (
            "Input / Expected / Actual",
            "What the system sees, what should happen, what did happen. Eval = closing the Expected→Actual gap.",
        ),
        (
            "Guardrail",
            "Online metric that triggers immediate action. e.g. <i>policy_accuracy</i> runs on every response, blocks/refers on fire.",
        ),
        (
            "Improvement flywheel",
            "Offline metric that feeds the next prompt. e.g. <i>tone</i> judge on top-20 by score → v3→v3.1 prompt.",
        ),
        (
            "Log filtering",
            "Sample by signal, not at random. <i>score_log</i> on 100 rows: 1 must / 19 should / 80 low.",
        ),
        (
            "Signal-metric divergence",
            "Signals flag a row as interesting, metric says PASS. The 20 top-scored rows all passed policy. Blind spot.",
        ),
    ]
    for name, desc in terms:
        story.append(Paragraph(f"<b>{name}.</b> {desc}", styles["body"]))

    # Section 2: 3 anti-patterns
    story.append(Paragraph("3 Anti-Patterns I Now Recognize", styles["h2"]))
    ap = [
        (
            "Metric overload",
            "47-metric dashboard no one reads. Resist until you can name a real failure mode the others miss.",
        ),
        (
            "Calibration neglect",
            "Uncalibrated LLM judge &gt; no judge. Test on 50 hand-labeled examples before trusting.",
        ),
        (
            "Coverage obsession",
            '12 hand-picked &gt; 200 generic. Aims for "must not get wrong" + production sample + log-filter long tail.',
        ),
    ]
    for name, desc in ap:
        story.append(Paragraph(f"<b>{name}.</b> {desc}", styles["body"]))

    # Section 3: 4-step mental model
    story.append(Paragraph("4-Step Mental Model", styles["h2"]))
    story.append(
        Paragraph(
            "<b>Input</b> (user + context) → <b>Expected</b> (plain language, debatable) → "
            "<b>Actual</b> (what really happened) → <b>Metric</b> (closes the gap).",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "If you can't fill in Expected, you don't have a metric. You have a vibe.",
            styles["body_italic"],
        )
    )

    # Section 4: the 1 thing
    story.append(Paragraph("If You Only Remember One Thing", styles["h2"]))
    story.append(
        Paragraph(
            "Start simple. Add only when you can name the failure mode.",
            styles["callout"],
        )
    )
    story.append(
        Paragraph(
            'We shipped 4 metrics after 8 chapters. No 5th because no failure mode justified it. The "add a 5th" pressure comes from vendor pitches and 47-metric dashboards.',
            styles["body_italic"],
        )
    )

    # Section 5: 3 questions
    story.append(Paragraph("3 Questions Before Shipping Any Metric", styles["h2"]))
    questions = [
        (
            "1. How will I know when this metric is lying to me?",
            "Every metric lies sometimes. Code metrics have false +. LLM judges drift. Define the failure mode before shipping.",
        ),
        (
            "2. What's the cost per call?",
            "Sub-ms code → online. 5s LLM judge → offline + sampled. The cost difference is 5,000× and the decision is structural.",
        ),
        (
            "3. What action does the result trigger?",
            'If no action, why measure? "Tracked weekly" is not an action. "When X crosses Y, ship a new prompt" is.',
        ),
    ]
    for q, a in questions:
        story.append(Paragraph(f"<b>{q}</b>", styles["body_bold"]))
        story.append(Paragraph(a, styles["body"]))

    # Section 6: still don't get
    story.append(Paragraph("Things I Still Don't Get (v2 learning list)", styles["h2"]))
    sdg = [
        "Inter-rater agreement stats (Cohen's kappa, Krippendorff's alpha) — never computed on real data",
        "Drift detection over time — the v3.1 prompt will drift; no system to alarm on it",
        "Online guardrail architectures — separate service? pre-commit hook? in-prompt? unclear",
    ]
    for item in sdg:
        story.append(Paragraph(f"• {item}", styles["body"]))

    # Footer
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Source: <i>free_courses/ai_evals_for_everyone_labs/chapter10_glossary_of_terms/eval_cheatsheet.md</i> · "
            "v0.1 · PM at SoleMates",
            styles["body_italic"],
        )
    )

    return story


def make_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.4 * inch,
        title="SoleMates AI Eval Cheat Sheet — One Pager",
        author="SoleMates PM",
    )

    styles = make_styles()
    story = build_story(styles)

    # Wrap in KeepInFrame to force everything onto 1 page (shrinks if needed)
    page_w, page_h = letter
    frame_w = page_w - 0.6 * inch - 0.6 * inch
    frame_h = page_h - 0.5 * inch - 0.4 * inch
    story = [KeepInFrame(frame_w, frame_h, story, mode="shrink")]

    doc.build(story)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    make_pdf()
