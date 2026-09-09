def build_feedback(validation_report):

    feedback = []

    details = validation_report.get(
        "details",
        {}
    )

    errors = validation_report.get(
        "errors",
        []
    )

    # ============================================================
    # SPECIFIC VALIDATION ERRORS
    # ============================================================

    for error in errors:

        if error:

            feedback.append(
                f"Specific validation error: {error}"
            )

    # ============================================================
    # STRUCTURE VALIDATOR
    # ============================================================

    structure = details.get(
        "validate_structure",
        {}
    )

    if not structure.get("valid", True):

        feedback.append(
            "Fix the paper structure while preserving "
            "the teacher's requested section order, "
            "section count and question count."
        )

    # ============================================================
    # MARKS VALIDATOR
    # ============================================================

    marks = details.get(
        "validate_marks",
        {}
    )

    if not marks.get("valid", True):

        feedback.append(
            "Correct question marks and section totals "
            "without changing the teacher's requested "
            "total exam marks."
        )

    # ============================================================
    # BLUEPRINT VALIDATOR
    # ============================================================

    blueprint = details.get(
        "validate_blueprint",
        {}
    )

    if not blueprint.get("valid", True):

        feedback.append(
            "Adjust difficulty, cognitive level and "
            "question type distribution to match the "
            "teacher's requested blueprint."
        )

    # ============================================================
    # SIMILARITY VALIDATOR
    # ============================================================

    similarity = details.get(
        "validate_similarity",
        {}
    )

    if not similarity.get("valid", True):

        feedback.append(
            "Rewrite questions that are too similar "
            "to repository questions while preserving "
            "the required syllabus coverage, difficulty "
            "and question type."
        )

    # ============================================================
    # DUPLICATE VALIDATOR
    # ============================================================

    duplicate = details.get(
        "validate_duplicates",
        {}
    )

    if not duplicate.get("valid", True):

        feedback.append(
            "Replace duplicated questions with unique "
            "questions that assess the same intended "
            "concepts while preserving the required "
            "question count and marks."
        )

    # ============================================================
    # QUESTION TYPE VALIDATOR
    # ============================================================

    question_types = details.get(
        "validate_question_types",
        {}
    )

    if not question_types.get("valid", True):

        feedback.append(
            "Correct the question-type distribution. "
            "Each section must contain exactly the "
            "requested number of questions for every "
            "question type."
        )

    # ============================================================
    # REMOVE DUPLICATE FEEDBACK
    # ============================================================

    unique_feedback = []

    for item in feedback:

        if item not in unique_feedback:

            unique_feedback.append(
                item
            )

    return unique_feedback