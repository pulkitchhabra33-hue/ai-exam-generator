from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import os
import datetime
import html
import uuid
import re

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

def draw_page_frame(canvas, doc):
    canvas.saveState()

    width, height = doc.pagesize

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.7)

    canvas.rect(
        25,
        25,
        width - 50,
        height - 50
    )

    canvas.setFont(
        "Helvetica",
        9
    )

    canvas.drawCentredString(
        width / 2,
        14,
        f"Page {canvas.getPageNumber()}"
    )

    canvas.restoreState()


def has_attempt_all_instruction(instructions):
    patterns = [
        r"\battempt\s+(all|every)\s+(the\s+)?(questions?|qns?)\b",
        r"\battempt\s+(all|every)\b",
        r"\ball\s+(the\s+)?(questions?|qns?)\s+(must|should|are to be)\s+attempted\b",
        r"\banswer\s+(all|every)\s+(the\s+)?(questions?|qns?)\b",
        r"\b(all|every)\s+(the\s+)?(questions?|qns?)\s+(must|should)\s+be\s+answered\b"
    ]

    combined = " ".join(
        str(instruction).lower().strip()
        for instruction in instructions
    )

    combined = re.sub(
        r"[^\w\s]",
        " ",
        combined
    )

    combined = re.sub(
        r"\s+",
        " ",
        combined
    ).strip()

    return any(
        re.search(pattern, combined)
        for pattern in patterns
    )


def generate_pdf(
    data,
    filename="paper.pdf",
    include_answers=True,
    include_solutions=True
):

    # --------------------------------------------------
    # CREATE UNIQUE FILENAME
    # --------------------------------------------------

    if not filename or filename == "paper.pdf":

        filename = (
            f"paper_{uuid.uuid4().hex}.pdf"
        )


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
        alignment=TA_CENTER,
        keepWithNext=1,
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

    school_name = safe_text(
        data.get(
            "school_name",
            ""
        )
    )

    exam_name = safe_text(
        data.get(
            "exam_name",
            ""
        )
    )

    subject = safe_text(
        data.get(
            "subject",
            ""
        )
    )

    class_name = safe_text(
        data.get(
            "class_name",
            ""
        )
    )

    time_limit = safe_text(
        data.get(
            "time_limit",
            ""
        )
    )

    total_marks = safe_text(
        data.get(
            "total_marks",
            ""
        )
    )

    header_title_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=5
    )

    header_exam_style = ParagraphStyle(
        "HeaderExam",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        spaceAfter=10
    )

    header_info_style = ParagraphStyle(
        "HeaderInfo",
        parent=styles["Normal"],
        leading=14
    )

    if school_name:
        elements.append(
            Paragraph(
                f"<b>{school_name}</b>",
                header_title_style
            )
        )

    if exam_name:
        elements.append(
            Paragraph(
                f"<b>{exam_name}</b>",
                header_exam_style
            )
        )

    if (
        class_name
        or subject
        or time_limit
        or total_marks
    ):
        header_table = Table(
            [
                [
                    Paragraph(
                        f"<b>Subject:</b> {subject}",
                        header_info_style
                    ),
                    Paragraph(
                        f"<b>Class:</b> {class_name}",
                        header_info_style
                    )
                ],
                [
                    Paragraph(
                        f"<b>Time:</b> {time_limit}",
                        header_info_style
                    ),
                    Paragraph(
                        f"<b>Maximum Marks:</b> {total_marks}",
                        header_info_style
                    )
                ]
            ],
            colWidths=[240, 240]
        )

        header_table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    )
                ]
            )
        )

        elements.append(
            header_table
        )

    elements.append(
        Spacer(
            1,
            10
        )
    )    


    # --------------------------------------------------
    # INSTRUCTIONS
    # --------------------------------------------------

    instructions = data.get(
        "instructions",
        []
    )

    if isinstance(
        instructions,
        str
    ):
        instructions = [
            line.strip()
            for line in instructions.splitlines()
            if line.strip()
        ]

    elif not isinstance(
        instructions,
        list
    ):
        instructions = []


    if not has_attempt_all_instruction(instructions):
        instructions.insert(
            0,
            "Attempt all questions."
        )

    instruction_elements = [
        Paragraph(
            "<b>Instructions:</b>",
            styles["Heading2"]
        )
    ]

    for instruction in instructions:
        instruction_elements.append(
            Paragraph(
                f"• {safe_text(instruction)}",
                styles["Normal"]
            )
        )

    instruction_box = Table(
        [
            [
                instruction_elements
            ]
        ],
        colWidths=[480]
    )

    instruction_box.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.black
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ]
        )
    )

    elements.append(
        instruction_box
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
            section.get(
                "section_name",
                ""
            )
        )


        if section_name:

            elements.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.black,
                    spaceBefore=6,
                    spaceAfter=6
                )
            )

            elements.append(
                Paragraph(
                    f"<b>{safe_text(section_name)}</b>",
                    section_style
                )
            )

            elements.append(
                HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=colors.black,
                    spaceBefore=2,
                    spaceAfter=8
                )
            )

        questions = section.get(
            "questions",
            []
        )

        grouped_questions = {}

        for question in questions:
            question_type = normalize_question_type(
                question.get(
                    "question_type",
                    ""
                )
            )

            if question_type not in grouped_questions:
                grouped_questions[question_type] = []

            grouped_questions[question_type].append(question)

        group_order = []

        for group in section.get(
            "question_groups",
            []
        ):
            question_type = normalize_question_type(
                group.get(
                    "question_type",
                    ""
                )
            )

            if (
                question_type
                and
                question_type not in group_order
            ):
                group_order.append(
                    question_type
                )

        ordered_types = (
            group_order
            +
            [
                question_type
                for question_type in grouped_questions
                if question_type not in group_order
            ]
        )

        # --------------------------------------------------
        # RENDER QUESTIONS BY QUESTION TYPE
        # --------------------------------------------------

        question_type_style = ParagraphStyle(
            "QuestionTypeHeading",
            parent=section_style,
            keepWithNext=1,
            spaceBefore=10,
            spaceAfter=8
        )

        for question_type in ordered_types:

            type_questions = grouped_questions.get(
                question_type,
                []
            )

            if not type_questions:
                continue

            heading = question_type

            if heading == "MCQ":
                heading = "Multiple Choice Questions"

            # Keep the question-type heading with the
            # first question of that type.
            elements.append(
                Paragraph(
                    f"<b>{safe_text(heading)}</b>",
                    question_type_style
                )
            )

            # --------------------------------------------------
            # RENDER EACH QUESTION EXACTLY ONCE
            # --------------------------------------------------

            for question in type_questions:

                question_text = safe_text(
                    question.get(
                        "question",
                        ""
                    )
                )

                marks = question.get(
                    "marks",
                    ""
                )

                question_type = normalize_question_type(
                    question.get(
                        "question_type",
                        ""
                    )
                )

                # --------------------------------------------------
                # QUESTION NUMBER + MARKS
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

                # --------------------------------------------------
                # TYPE-SPECIFIC CONTENT
                # --------------------------------------------------

                render_styles = {
                    "Normal": styles["Normal"],
                    "OptionStyle": option_style
                }

                type_elements = render_question_content(
                    question,
                    question_type,
                    render_styles
                )

                # --------------------------------------------------
                # KEEP COMPLETE QUESTION TOGETHER
                # --------------------------------------------------

                question_block = [
                    question_table,
                    Spacer(
                        1,
                        4
                    ),
                    *type_elements
                ]

                elements.append(
                    KeepTogether(
                        question_block
                    )
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

    if include_solutions:

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
            elements,
            onFirstPage=draw_page_frame,
            onLaterPages=draw_page_frame
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
    elements = []

    # MCQ

    if question_type == "MCQ":
        options = question.get(
            "options",
            []
        )

        option_labels = [
            "A",
            "B",
            "C",
            "D"
        ]

        for index, option in enumerate(options[:4]):
            option_text = safe_text(option)

            label = option_labels[index]

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
        return [
            Spacer(
                1,
                3
            )
        ]

    # Fill in the Blanks

    if question_type == "Fill in the Blanks":
        elements.append(
            Spacer(
                1,
                3
            )
        )

        return elements

    # Assertion-Reason

    # Assertion-Reason

    if question_type == "Assertion-Reason":

        assertion = safe_text(
            question.get(
                "assertion",
                ""
            )
        )

        reason = safe_text(
            question.get(
                "reason",
                ""
            )
        )

        if assertion:
            elements.append(
                Paragraph(
                    f"<b>Assertion (A):</b> {assertion}",
                    styles["OptionStyle"]
                )
            )

        if reason:
            elements.append(
                Paragraph(
                    f"<b>Reason (R):</b> {reason}",
                    styles["OptionStyle"]
                )
            )

        assertion_reason_options = [
            "Both Assertion (A) and Reason (R) are true and Reason (R) is the correct explanation of the Assertion (A).",
            "Both Assertion (A) and Reason (R) are true, but Reason (R) is not the correct explanation of the Assertion (A).",
            "Assertion (A) is true, but Reason (R) is false.",
            "Assertion (A) is false, but Reason (R) is true."
        ]

        option_labels = [
            "A",
            "B",
            "C",
            "D"
        ]

        for index, option in enumerate(
            assertion_reason_options
        ):

            elements.append(
                Paragraph(
                    f"<b>{option_labels[index]})</b> {option}",
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