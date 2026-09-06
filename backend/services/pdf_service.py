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
from reportlab.lib.enums import TA_RIGHT
import os
import datetime
import html

def normalize_question_type(question_type):
    if not question_type:
        return ""

    value= str(question_type).strip().lower()

    aliases= {
         "mcq": "MCQ",

        "very short answer": "Very Short Answer",
        "very short": "Very Short Answer",

        "short answer": "Short Answer",
        "short": "Short Answer",

        "long answer": "Long Answer",
        "long": "Long Answer",

        "case study": "Case Study",
        "case-based": "Case Study",
        "case based": "Case Study",

        "assertion-reason": "Assertion-Reason",
        "assertion reason": "Assertion-Reason",
        "assertion/reason": "Assertion-Reason",

        "application-based": "Application-based",
        "application based": "Application-based",

        "hots": "HOTS",

        "true/false": "True/False",
        "true false": "True/False",

        "fill in the blanks": "Fill in the Blanks",
        "fill-in-the-blanks": "Fill in the Blanks",

        "match the following": "Match the Following",

        "one word answer": "One Word Answer",
        "one-word answer": "One Word Answer",

        "source-based questions": "Source-Based Questions",
        "source based questions": "Source-Based Questions",

        "diagram-based questions": "Diagram-Based Questions",
        "diagram based questions": "Diagram-Based Questions"
    }

    return aliases.get(
        value,
        str(question_type).strip()
    )

def safe_text(value):
    if value is None:
        return ""

    return html.escape(
        str(value).strip()
    )

def generate_pdf(
    data,
    filename="paper.pdf",
    include_answers=True
):

    # --------------------------------------------------
    # CREATE UNIQUE FILENAME
    # --------------------------------------------------

    if not filename:

        timestamp = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = f"paper_{timestamp}.pdf"


    # --------------------------------------------------
    # CREATE PDF FOLDER
    # --------------------------------------------------

    folder = "backend/pdfs"

    os.makedirs(
        folder,
        exist_ok=True
    )


    filepath = os.path.join(
        folder,
        filename
    )


    # --------------------------------------------------
    # PDF DOCUMENT
    # --------------------------------------------------

    doc = SimpleDocTemplate(
        filepath,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )


    # --------------------------------------------------
    # STYLES
    # --------------------------------------------------

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Title"],
        spaceAfter=12
    )


    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8
    )


    question_style = ParagraphStyle(
        "QuestionStyle",
        parent=styles["Normal"],
        leading=15,
        spaceAfter=5
    )


    marks_style = ParagraphStyle(
        "MarksStyle",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
        leading=15
    )


    option_style = ParagraphStyle(
        "OptionStyle",
        parent=styles["Normal"],
        leftIndent=12,
        leading=14,
        spaceAfter=3
    )


    answer_style = ParagraphStyle(
        "AnswerStyle",
        parent=styles["Normal"],
        leading=14,
        spaceAfter=6
    )


    # --------------------------------------------------
    # PDF ELEMENTS
    # --------------------------------------------------

    elements = []


    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    elements.append(
        Paragraph(
            data.get(
                "title",
                "Exam Paper"
            ),
            title_style
        )
    )


    elements.append(
        Spacer(
            1,
            8
        )
    )


    # --------------------------------------------------
    # INSTRUCTIONS
    # --------------------------------------------------

    instructions = data.get(
        "instructions",
        []
    )


    if instructions:

        elements.append(
            Paragraph(
                "Instructions:",
                styles["Heading2"]
            )
        )


        for instruction in instructions:

            elements.append(
                Paragraph(
                    f"• {instruction}",
                    styles["Normal"]
                )
            )


        elements.append(
            Spacer(
                1,
                12
            )
        )


    # --------------------------------------------------
    # SECTIONS + QUESTIONS
    # --------------------------------------------------

    question_counter = 1


    for section in data.get(
        "sections",
        []
    ):

        section_name = section.get(
            "name",
            ""
        )


        if section_name:

            elements.append(
                Paragraph(
                    section_name,
                    section_style
                )
            )


        elements.append(
            Spacer(
                1,
                4
            )
        )


        for question in section.get(
            "questions",
            []
        ):
            question_text= safe_text(
                question.get(
                    "question",
                    ""
                )
            )

            marks= question.get("marks", "")

            question_type= normalize_question_type(
                question.get(
                    "question_type",
                    ""
                )
            )

            # --------------------------------------------------
            # QUESTION + MARKS
            # --------------------------------------------------

            question_number = (
                f"<b>{question_counter}.</b>"
            )


            question_paragraph = Paragraph(
                f"{question_number} {question_text}",
                question_style
            )


            marks_paragraph = Paragraph(
                f"<b>[{safe_text(marks)}]</b>",
                marks_style
            )


            question_table = Table(
                [
                    [
                        question_paragraph,
                        marks_paragraph
                    ]
                ],
                colWidths=[
                    430,
                    50
                ],
                hAlign="LEFT"
            )


            question_table.setStyle(
                TableStyle(
                    [
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP"
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            0
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            0
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            0
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            0
                        )
                    ]
                )
            )


            elements.append(
                question_table
            )


            elements.append(
                Spacer(
                    1,
                    4
                )
            )

            # TYPE-SPECIFIC CONTENT

            render_styles = {
                "Normal": styles["Normal"],
                "OptionStyle": option_style
            }

            type_elements= render_question_content(
                question,
                question_type,
                render_styles
            )

            elements.extend(
                type_elements
            )

            question_counter += 1

        elements.append(
            Spacer(
                1,
                10
            )
        )


    # --------------------------------------------------
    # ANSWER KEY
    # --------------------------------------------------

    if include_answers:

        elements.append(
            Paragraph(
                "Answer Key",
                styles["Heading2"]
            )
        )


        counter = 1


        for section in data.get(
            "sections",
            []
        ):

            for question in section.get(
                "questions",
                []
            ):

                answer = str(
                    question.get(
                        "answer",
                        ""
                    )
                ).strip()


                elements.append(
                    Paragraph(
                        f"<b>{counter}.</b> {answer}",
                        answer_style
                    )
                )


                counter += 1


        elements.append(
            Spacer(
                1,
                10
            )
        )


    # --------------------------------------------------
    # SOLUTIONS
    # --------------------------------------------------

    if include_answers:

        elements.append(
            Paragraph(
                "Solutions",
                styles["Heading2"]
            )
        )


        counter = 1


        for section in data.get(
            "sections",
            []
        ):

            for question in section.get(
                "questions",
                []
            ):

                solution = str(
                    question.get(
                        "solution",
                        ""
                    )
                ).strip()


                elements.append(
                    Paragraph(
                        f"<b>{counter}.</b> {solution}",
                        answer_style
                    )
                )


                counter += 1


    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------

    try:
        doc.build(
            elements
        )

    except Exception as e:
        print(
            "Error building PDF:",
            e
        )

        raise

    return filepath


def render_question_content(
        question,
        question_type,
        styles
):
    elements= []

    # MCQ

    if question_type == "MCQ":
        options= question.get(
            "options",
            []
        )

        option_labels= [
            "A",
            "B",
            "C",
            "D"
        ]

        for index, option in enumerate(options[:4]):
            option_text = safe_text(option)
            # Remove AI-provided A), B), C), D)
            # if already present.

            # if (
            #     len(option_text) >= 2
            #     and option_text[:2].upper()
            #     in ["A", "B", "C", "D"]
            # ):
            #     option_text= (
            #         option_text[2:]
            #         .strip()
            #     )

            label= option_labels[index]

            elements.append(
                Paragraph(
                    f"<b>{label})</b> {option_text}",
                    styles["OptionStyle"]
                )
            )

        elements.append(
            Spacer(
                1,
                5
            )
        )

        return elements

    # TRUE / FALSE

    if question_type == "True/False":
        elements.append(
            Paragraph(
                "<b>True / False</b>",
                styles["OptionStyle"]
            )
        )

        elements.append(
            Spacer(
                1,
                5
            )
        )

        return elements

    # Fill in the Blanks

    if question_type == "Fill in the Blanks":
        # The blank should already exist in
        # the generated question text.

        elements.append(
            Spacer(
                1,
                3
            )
        )

        return elements

        # Assertion-Reason

    if question_type == "Assertion-Reason":
        assertion= safe_text(
            question.get(
                "assertion",
                ""
            )
        )

        if assertion:
            elements.append(
                Paragraph(
                    f"<b>Assertion:</b> {assertion}",
                    styles["OptionStyle"]
                )
            )

        reason= safe_text(
            question.get(
                "reason",
                ""
            )
        )

        if reason:
            elements.append(
                Paragraph(
                    f"<b>Reason:</b> {reason}",
                    styles["OptionStyle"]
                )
            )

        elements.append(
            Spacer(
                1,
                5
            )
        )

        return elements

    # Match the Following

    if question_type == "Match the Following":
        left_column= question.get(
            "left_column",
            []
        )

        right_column= question.get(
            "right_column",
            []
        )

        rows= [
            [
                Paragraph(
                    "<b>Column A</b>",
                    styles["Normal"]
                ),
                Paragraph(
                    "<b>Column B</b>",
                    styles["Normal"]
                )
            ]
        ]

        max_rows= max(
            len(left_column),
            len(right_column)
        )

        for index in range(max_rows):
            left_value= ""
            right_value= ""

            if index < len(left_column):
                left_value= safe_text(
                    left_column[index]
                )

            if index <len(right_column):
                right_value= safe_text(
                    right_column[index]
                )

            rows.append(
                [
                    Paragraph(
                        left_value,
                        styles["Normal"]
                    ),
                    Paragraph(
                        right_value,
                        styles["Normal"]
                    )
                ]
            )

        match_table= Table(
            rows,
            colWidths=[
                250,
                230
            ]
        )

        match_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.black
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ]
            )
        )

        elements.append(match_table)

        elements.append(
            Spacer(
                1,
                8
            )
        )

        return elements

    # SOURCE-BASED QUESTIONS

    if question_type == "Source-Based Questions":
        source= safe_text(
            question.get(
                "source",
                ""
            )
        )

        if source:
            elements.append(
                Paragraph(
                    f"<b>Source:</b> {source}",
                    styles["OptionStyle"]
                )
            )

            elements.append(
                Spacer(
                    1,
                    5
                )
            )

        return elements

    # DIAGRAM-BASED QUESTIONS

    if question_type == "Diagram-Based Questions":
        diagram= safe_text(
            question.get(
                "diagram",
                ""
            )
        )

        if diagram:
            elements.append(
                Paragraph(
                    f"<b>Diagram:</b> {diagram}",
                    styles["OptionStyle"]
                )
            )

        elements.append(
            Spacer(
                1,
                5
            )
        )

        return elements


    # CASE-STUDY

    if question_type == "Case Study":
        case_text= safe_text(
            question.get(
                "case",
                question.get(
                    "passage",
                    ""
                )
            )
        )

        if case_text:
            elements.append(
                Paragraph(
                    f"<b>Case:</b> {case_text}",
                    styles["OptionStyle"]
                )
            )

            elements.append(
                Spacer(
                    1,
                    5
                )
            )

        return elements
    
    # --------------------------------------------------
    # OTHER TYPES
    # --------------------------------------------------

    # Very Short Answer
    # Short Answer
    # Long Answer
    # Application-based
    # HOTS
    # One Word Answer

    return elements