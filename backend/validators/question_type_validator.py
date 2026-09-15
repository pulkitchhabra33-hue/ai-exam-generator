from collections import Counter

from backend.utils.question_utils import build_question_id


def normalize_question_type(question_type):
    if not question_type:
        return ""

    value = str(question_type).strip().lower()

    mappings = {
        "mcq": "MCQ",
        "multiple choice": "MCQ",
        "multiple choice question": "MCQ",
        "very short answer": "Very Short Answer",
        "short answer": "Short Answer",
        "long answer": "Long Answer",
        "case study": "Case Study",
        "assertion-reason": "Assertion-Reason",
        "assertion reason": "Assertion-Reason",
        "assertion/reason": "Assertion-Reason",
        "application-based": "Application-based",
        "application based": "Application-based",
        "hots": "HOTS",
        "true/false": "True/False",
        "true / false": "True/False",
        "true or false": "True/False",
        "fill in the blanks": "Fill in the Blanks",
        "fill in the blank": "Fill in the Blanks",
        "match the following": "Match the Following",
        "one word answer": "One Word Answer",
        "source-based questions": "Source-Based Questions",
        "source based questions": "Source-Based Questions",
    }

    return mappings.get(value, str(question_type).strip())


def validate_question_types(
    generated_paper,
    teacher_data
):
    report = {
        "valid": True,
        "errors": []
    }

    generated_sections = generated_paper.get(
        "sections",
        []
    )

    expected_sections = teacher_data.get(
        "sections",
        []
    )

    if len(generated_sections) != len(expected_sections):
        report["valid"] = False
        report["errors"].append(
            f"Expected {len(expected_sections)} sections, "
            f"but generated {len(generated_sections)}."
        )

    for section_index, expected_section in enumerate(expected_sections):
        if section_index >= len(generated_sections):
            break

        generated_section = generated_sections[section_index]

        expected_groups = expected_section.get(
            "question_groups",
            []
        )

        generated_questions = generated_section.get(
            "questions",
            []
        )

        expected_counts = Counter()

        for group in expected_groups:
            expected_type = normalize_question_type(
                group.get(
                    "question_type",
                    ""
                )
            )

            expected_count = int(
                group.get(
                    "question_count",
                    0
                )
            )

            if not expected_type:
                report["valid"] = False
                report["errors"].append(
                    f"Section {section_index + 1} contains "
                    "a question group with no question_type."
                )
                continue

            expected_counts[expected_type] += expected_count

        generated_counts = Counter()

        for question in generated_questions:
            raw_type = question.get(
                "question_type"
            )

            if not raw_type:
                report["valid"] = False
                report["errors"].append(
                    f"Section {section_index + 1} contains "
                    "a question with no question_type."
                )
                continue

            normalized_type = normalize_question_type(
                raw_type
            )

            generated_counts[normalized_type] += 1

        for expected_type, expected_count in expected_counts.items():
            actual_count = generated_counts.get(
                expected_type,
                0
            )

            if actual_count != expected_count:
                report["valid"] = False
                report["errors"].append(
                    f"Section {section_index + 1}: "
                    f"Expected {expected_count} "
                    f"{expected_type} questions, "
                    f"but generated {actual_count}."
                )

        for generated_type in generated_counts:
            if generated_type not in expected_counts:
                report["valid"] = False
                report["errors"].append(
                    f"Section {section_index + 1}: "
                    f"Unexpected question type "
                    f"'{generated_type}'."
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
                continue

            question_type = normalize_question_type(
                question_type
            )

            if question_type == "MCQ":
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
                        "exactly 4 options."
                    )

                if any(
                    not str(option).strip()
                    for option in options
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
                        "invalid MCQ answer."
                    )

            elif question_type == "True/False":
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

            elif question_type == "Fill in the Blanks":
                question_text = str(
                    question.get(
                        "question",
                        ""
                    )
                ).strip()

                has_blank = (
                    "____" in question_text
                    or
                    "___" in question_text
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

            elif question_type == "Assertion-Reason":
                assertion = str(
                    question.get(
                        "assertion",
                        ""
                    )
                ).strip()

                reason = str(
                    question.get(
                        "reason",
                        ""
                    )
                ).strip()

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

            elif question_type == "Match the Following":
                left_column = question.get(
                    "left_column"
                )

                right_column = question.get(
                    "right_column"
                )

                if not isinstance(
                    left_column,
                    list
                ) or not left_column:
                    report["valid"] = False
                    report["errors"].append(
                        f"{question_id} is missing "
                        "the left matching column."
                    )

                if not isinstance(
                    right_column,
                    list
                ) or not right_column:
                    report["valid"] = False
                    report["errors"].append(
                        f"{question_id} is missing "
                        "the right matching column."
                    )

                if isinstance(left_column, list):
                    if any(
                        not str(item).strip()
                        for item in left_column
                    ):
                        report["valid"] = False
                        report["errors"].append(
                            f"{question_id} contains "
                            "an empty left matching item."
                        )

                if isinstance(right_column, list):
                    if any(
                        not str(item).strip()
                        for item in right_column
                    ):
                        report["valid"] = False
                        report["errors"].append(
                            f"{question_id} contains "
                            "an empty right matching item."
                        )

                if (
                    isinstance(left_column, list)
                    and
                    isinstance(right_column, list)
                    and
                    len(left_column) != len(right_column)
                ):
                    report["valid"] = False
                    report["errors"].append(
                        f"{question_id} has "
                        "unequal matching columns."
                    )

            question_text = str(
                question.get(
                    "question",
                    ""
                )
            ).strip()

            if not question_text:
                report["valid"] = False
                report["errors"].append(
                    f"{question_id} has no "
                    "question text."
                )

    return report