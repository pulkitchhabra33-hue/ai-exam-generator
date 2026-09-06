from backend.utils.question_utils import build_question_id

def normalize_question_type(value):

    if not value:
        return ""

    value = (
        str(value)
        .strip()
        .lower()
    )

    aliases = {
        "mcq": "mcq",

        "very short answer": "very short answer",
        "very short": "very short answer",

        "short answer": "short answer",
        "short": "short answer",

        "long answer": "long answer",
        "long": "long answer",

        "case study": "case study",
        "case-study": "case study",
        "case based": "case study",
        "case-based": "case study",

        "assertion-reason": "assertion-reason",
        "assertion reason": "assertion-reason",
        "assertion/reason": "assertion-reason",

        "application-based": "application-based",
        "application based": "application-based",

        "hots": "hots",

        "true/false": "true/false",
        "true false": "true/false",

        "fill in the blanks": "fill in the blanks",
        "fill-in-the-blanks": "fill in the blanks",

        "match the following": "match the following",

        "one word answer": "one word answer",
        "one-word answer": "one word answer",

        "source-based questions": "source-based questions",
        "source based questions": "source-based questions",

        "diagram-based questions": "diagram-based questions",
        "diagram based questions": "diagram-based questions"
    }

    return aliases.get(
        value,
        value
    )

def validate_question_types(
        generated_paper,
        teacher_data
):
    report = {
        "valid": True,
        "errors": []
    }

    generated_sections = (
        generated_paper.get(
            "sections",
            []
        )
    )

    expected_sections = (
        teacher_data.get(
            "sections",
            []
        )
    )

    for section_index, (
        expected_section,
        generated_section
    ) in enumerate(
        zip(
            expected_sections,
            generated_sections
        )
    ):

        expected_type = normalize_question_type(
            expected_section.get(
                "question_type",
                ""
            )
        )

        generated_questions = (
            generated_section.get(
                "questions",
                []
            )
        )

        for question_index, question in enumerate(
            generated_questions,
            start=1
        ):

            question_id = build_question_id(
                generated_section,
                question_index
            )

            question_type = question.get(
                    "question_type"
                )

            if not question_type:
                report["valid"] = False

                report["errors"].append(
                    f"{question_id} is missing "
                    "the question_type field."
                )

                continue

            question_type = normalize_question_type(
                question_type
            )

            # --------------------------------------------------
            # TYPE MATCH
            # --------------------------------------------------

            if question_type != expected_type:

                report["valid"] = False

                report["errors"].append(
                    f"{question_id} has incorrect "
                    f"question type. Expected "
                    f"'{expected_section.get('question_type')}'."
                )

                continue

            # --------------------------------------------------
            # MCQ
            # --------------------------------------------------

            if expected_type == "mcq":

                options = question.get(
                    "options"
                )

                if not isinstance(
                    options,
                    list
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is an MCQ "
                        "but has no options list."
                    )

                    continue

                if len(options) != 4:

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} must have "
                        f"exactly 4 options, "
                        f"but has {len(options)}."
                    )

                    continue

                cleaned_options = [
                    str(option).strip()
                    for option in options
                ]

                if any(
                    not option
                    for option in cleaned_options
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} contains "
                        "an empty MCQ option."
                    )

                answer = str(
                    question.get(
                        "answer",
                        ""
                    )
                ).strip().upper()

                if answer not in (
                    "A",
                    "B",
                    "C",
                    "D"
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} has an "
                        "invalid MCQ answer. "
                        "Expected A, B, C or D."
                    )

            # --------------------------------------------------
            # TRUE / FALSE
            # --------------------------------------------------

            elif expected_type == "true/false":

                answer = str(
                    question.get(
                        "answer",
                        ""
                    )
                ).strip().lower()

                if answer not in (
                    "true",
                    "false"
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} must have "
                        "True or False as its answer."
                    )

            # --------------------------------------------------
            # FILL IN THE BLANKS
            # --------------------------------------------------

            elif expected_type == "fill in the blanks":

                question_text = str(
                    question.get(
                        "question",
                        ""
                    )
                )

                has_blank = (
                    "____" in question_text
                    or
                    "___" in question_text
                    or
                    "______" in question_text
                    or
                    "blank" in question_text.lower()
                )

                if not has_blank:

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is marked "
                        "as Fill in the Blanks "
                        "but contains no blank."
                    )

            # --------------------------------------------------
            # ASSERTION - REASON
            # --------------------------------------------------

            elif expected_type == "assertion-reason":

                assertion = question.get(
                    "assertion"
                )

                reason = question.get(
                    "reason"
                )

                if not assertion:

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is missing "
                        "the Assertion."
                    )

                if not reason:

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is missing "
                        "the Reason."
                    )

            # --------------------------------------------------
            # MATCH THE FOLLOWING
            # --------------------------------------------------

            elif expected_type == "match the following":

                left_column = question.get(
                    "left_column"
                )

                right_column = question.get(
                    "right_column"
                )

                if not isinstance(
                    left_column,
                    list
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is missing "
                        "the left matching column."
                    )

                if not isinstance(
                    right_column,
                    list
                ):

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} is missing "
                        "the right matching column."
                    )

            # --------------------------------------------------
            # ONE WORD ANSWER
            # --------------------------------------------------

            elif expected_type == "one word answer":

                answer = str(
                    question.get(
                        "answer",
                        ""
                    )
                ).strip()

                if not answer:

                    report["valid"] = False

                    report["errors"].append(
                        f"{question_id} has no answer."
                    )

            # --------------------------------------------------
            # GENERAL QUESTION CHECK
            # --------------------------------------------------

            question_text = str(
                question.get(
                    "question",
                    ""
                )
            ).strip()

            if not question_text:

                report["valid"] = False

                report["errors"].append(
                    f"{question_id} has no question text."
                )

    return report