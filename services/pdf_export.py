# services/pdf_export.py

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)


def generate_pdf(
    url: str,
    summary: str,
    flashcards: list[dict],
    quiz: list[dict]
) -> bytes:
    """
    Generates a PDF document with summary, flashcards and quiz.

    Parameters:
        url:        YouTube URL
        summary:    summary text from summarizer.py
        flashcards: list of {"front": ..., "back": ...} dicts
        quiz:       list of {"question": ..., "options": [...], 
                    "answer": ..., "explanation": ...} dicts

    Returns:
        PDF as bytes — ready to send to st.download_button
    """

    # Write to memory buffer — no file saved to disk
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # ── Styles ───────────────────────────────
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4*mm
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=6*mm,
        spaceAfter=3*mm
    )

    subheading_style = ParagraphStyle(
        "Subheading",
        parent=styles["Heading3"],
        fontSize=11,
        textColor=colors.HexColor("#0f3460"),
        spaceBefore=4*mm,
        spaceAfter=2*mm
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=2*mm,
        leading=14
    )

    url_style = ParagraphStyle(
        "URL",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=4*mm
    )

    answer_style = ParagraphStyle(
        "Answer",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#1a7a4a"),
        spaceAfter=2*mm,
        leading=14
    )

    # ── Build content ────────────────────────
    content = []

    # Title
    content.append(Paragraph("AI Knowledge Copilot", title_style))
    content.append(Paragraph(f"Source: {url}", url_style))
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#cccccc")))
    content.append(Spacer(1, 4*mm))

    # ── Summary section ──────────────────────
    content.append(Paragraph("Summary", heading_style))

    # Split summary by lines and add each as paragraph
    for line in summary.split("\n"):
        line = line.strip()
        if not line:
            content.append(Spacer(1, 2*mm))
            continue
        # Handle bold markdown (**text**)
        line = line.replace("**", "<b>", 1)
        line = line.replace("**", "</b>", 1)
        content.append(Paragraph(line, body_style))

    content.append(Spacer(1, 4*mm))
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#cccccc")))

    # ── Flashcards section ───────────────────
    content.append(Paragraph("Flashcards", heading_style))

    for i, card in enumerate(flashcards, 1):
        content.append(
            Paragraph(f"Card {i}: {card['front']}", subheading_style)
        )
        content.append(
            Paragraph(f"Answer: {card['back']}", answer_style)
        )
        content.append(Spacer(1, 2*mm))

    content.append(Spacer(1, 4*mm))
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#cccccc")))

    # ── Quiz section ─────────────────────────
    content.append(Paragraph("Quiz", heading_style))

    for i, q in enumerate(quiz, 1):
        content.append(
            Paragraph(f"Q{i}: {q['question']}", subheading_style)
        )

        for option in q["options"]:
            # Mark correct answer with a tick
            if option == q["answer"]:
                content.append(
                    Paragraph(f"✓ {option}", answer_style)
                )
            else:
                content.append(
                    Paragraph(f"   {option}", body_style)
                )

        content.append(
            Paragraph(
                f"Explanation: {q['explanation']}",
                ParagraphStyle(
                    "Explanation",
                    parent=body_style,
                    textColor=colors.HexColor("#666666"),
                    fontSize=9,
                    spaceBefore=1*mm
                )
            )
        )
        content.append(Spacer(1, 3*mm))

    # ── Build PDF ────────────────────────────
    doc.build(content)
    buffer.seek(0)
    return buffer.read()