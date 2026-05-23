from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors
from reportlab.pdfgen import canvas

import os
import datetime

def add_page_number(canvas, doc):
    page_num= canvas.getPageNumber()
    text= f"Page {page_num}"
    canvas.setFont("Helvetica", 10)
    canvas.line(40, 30, 550, 30)
    canvas.drawRightString(550, 15, text)

def generate_pdf(data, filename=None, include_answers=True):

    # 🔥 Unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if not filename:
        filename = f"paper_{timestamp}.pdf"

    # 📁 Create folder
    folder = "backend/pdfs"
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)

    # 📄 PDF document
    doc = SimpleDocTemplate(
        filepath,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # 🎨 Custom Question Style
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        spaceAfter=14,
        leading=20
    )

    elements = []

    # 🏫 School Exam Header

    school_name = data.get("school_name", "ABC PUBLIC SCHOOL")
    exam_name = data.get("exam_name", "MODEL QUESTION PAPER")
    subject = data.get("subject", "")
    class_name = data.get("class_name", "")
    time_limit = data.get("time_limit", "3 Hours")
    total_marks = data.get("total_marks", 100)

    # School Name
    elements.append(
        Paragraph(
            f"<para align='center'><b>{school_name}</b></para>",
            styles["Title"]
        )
    )

    # Exam Name
    elements.append(
        Paragraph(
            f"<para align='center'><b>{exam_name}</b></para>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    # Subject + Class
    subject_table = Table(
        [
            [
                f"Subject : {subject}",
                f"Class : {class_name}"
            ]
        ],
        colWidths=[250, 250]
    )

    subject_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    elements.append(subject_table)

    # Time + Maximum Marks
    info_table = Table(
        [
            [
                f"Time : {time_limit}",
                f"M.M. : {total_marks}"
            ]
        ],
        colWidths=[250, 250]
    )

    info_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.black),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),

        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),

        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),

        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))

    elements.append(info_table)

    elements.append(Spacer(1, 15))

    # 📌 Instructions
    elements.append(
        Paragraph(
            "<b>Instructions :-</b>",
            styles["Heading3"]
        )
    )

    elements.append(Spacer(1, 8))

    for inst in data.get("instructions", []):
        elements.append(
            Paragraph(
                f"• {inst}",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 18))

    # ❓ Questions
    question_counter = 1

    for section in data.get("sections", []):

        # Section Heading
        elements.append(
            Paragraph(
                f"<para align='center'><b>{section.get('name', '')}</b></para>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        for q in section.get("questions", []):

            question_text = f"""
            <b>Q.{question_counter}</b>
            {q.get('question')}
            <br/><br/>
            <b>[{q.get('marks')} Marks]</b>
            """

            elements.append(
                Paragraph(
                    question_text,
                    question_style
                )
            )

            # MCQ Options
            options = q.get("options", [])

            if options:
                for opt in options:
                    elements.append(
                        Paragraph(
                            f"• {opt}",
                            styles["Normal"]
                        )
                    )

            elements.append(Spacer(1, 12))

            question_counter += 1

        elements.append(Spacer(1, 18))

    # ✅ Answer Key
    if include_answers:

        elements.append(
            Paragraph(
                "<b>Answer Key</b>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        counter = 1

        for section in data.get("sections", []):
            for q in section.get("questions", []):

                ans = q.get("answer", "Not Provided")

                elements.append(
                    Paragraph(
                        f"{counter}. {ans}",
                        styles["Normal"]
                    )
                )

                counter += 1

        elements.append(Spacer(1, 18))

    # ✅ Solutions
    if include_answers:

        elements.append(
            Paragraph(
                "<b>Solutions</b>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        counter = 1

        for section in data.get("sections", []):
            for q in section.get("questions", []):

                sol = q.get("solution", "No solution provided")

                elements.append(
                    Paragraph(
                        f"<b>{counter}.</b> {sol}",
                        styles["Normal"]
                    )
                )

                elements.append(Spacer(1, 10))

                counter += 1

    # 🔥 Build PDF
    try:
        doc.build(
            elements,
            onFirstPage= add_page_number,
            onLaterPages= add_page_number
        )

    except Exception as e:
        print("Error building PDF:", e)
        raise

    return filepath