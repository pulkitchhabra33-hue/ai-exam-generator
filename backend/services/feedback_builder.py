def build_feedback(validation_report):
    feedback= []
    
    details= validation_report.get(
        "details", 
        {}
    )

    #Structure Validator
    structure= details.get(
        "validate_structure",
        {}
    )

    if not structure.get("valid", True):
        feedback.append(
            "Fix the paper structure while preserving teacher requirements."
        )
    
    #Marks Validator
    marks= details.get(
        "validate_marks",
        {}
    )

    if not marks.get("valid", True):
        feedback.append(
            "Correct question marks and section totals without changing total exam marks."
        )

    #Blueprint Validator
    blueprint= details.get(
        "validate_blueprint",
        {}
    )

    if not blueprint.get("valid", True):
        feedback.append(
            "Adjust difficulty, cognitive level and question type distribution to better match the reference blueprint."
        )

    #Similarity Validator
    similarity= details.get(
        "valdiate_similarity",
        {}
    )

    if not similarity.get("valid", True):
        feedback.append(
            "Rewrite questions that are too similar to repository questions while preserving syllabus coverage."
        )

    #Duplicate Validator
    duplicate= details.get(
        "validate_duplicate",
        {}
    )

    if not duplicate.get("valid", True):
        feedback.append(
            "Replace duplicated questions with unique questions that assess the same concepts."
        )

    #Grammar Validator
    grammar= details.get(
        "validate_grammar",
        {}
    )

    if not grammar.get("valid", True):
        feedback.append(
            "Correct grammar, spelling and punctuation without changing the meaning of the questions."
        )

    return feedback