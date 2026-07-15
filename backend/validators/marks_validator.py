from backend.utils.question_utils import build_question_id

def validate_marks(generated_paper, teacher_data):
    report= {
        "valid": True,
        "errors": []
    }

    # -----------------------------
    # 1. TOTAL MARKS CHECK
    # -----------------------------

    expected_total= teacher_data.get("total_marks", 0)
    generated_total= 0

    for section in generated_paper.get("sections", []):
        for question in section.get("questions", []):
            generated_total += question.get("marks", 0)

    if expected_total != generated_total:
        report["valid"] = False
        
        report["errors"].append(
            f"Total marks mismatch: expected {expected_total}, got {generated_total}"
        )

    # -----------------------------
    # 2. SECTION MARKS CHECK
    # -----------------------------

    generated_sections= {
        section.get("section_name"): section 
        for section in generated_paper.get("sections", [])
    }

    for section in teacher_data.get("sections", []):
        section_name= section.get("section_name")
        expected_marks= section.get("marks", 0)
        generated_marks= 0

        # find matching section in generated paper
        matched_section= generated_sections.get(section_name)

        if not matched_section:
            report["valid"] = False
            report["errors"].append(
                f"Missing section: {section_name}"
            )

            continue
        
        for question in matched_section.get("questions", []):
            generated_marks += question.get("marks", 0)

        if expected_marks != generated_marks:
            report["valid"] = False
            report["errors"].append(
                f"Section {section_name} marks mismatch: expected {expected_marks}, got {generated_marks}"
            )

    # -----------------------------
    # 3. QUESTION MARK VALIDATION
    # -----------------------------

    allowed_marks= set()

    for section in teacher_data.get("sections", []):
        if "allowed_marks" in section:
            allowed_marks.update(
                section["allowed_marks"]
            )

        elif "marks_per_question" in section:
            allowed_marks.add(
                section["marks_per_question"]
            )

    for section in generated_paper.get("sections", []):
        for index, question in enumerate(section.get("questions", []), start= 1):

            question_id = build_question_id(
                section,
                index
            )

            mark= question.get("marks", 0)

            if allowed_marks and mark not in allowed_marks:
                report["valid"] = False

                report["errors"].append(
                    f"Question {question_id} has invalid marks value {mark}."
                )


    return report