def validate_structure(
        generated_paper,
        teacher_data
):
    report= {
        "valid": True,
        "errors": []
    }

    expected_sections= len(
        teacher_data["sections"]
    )

    generated_sections= len(
        generated_paper["sections"]
    )

    if expected_sections != generated_sections:
        report["valid"] = False
        report["errors"].append(
            "Section count mismatch."
        )

    for expected, generated in zip(
        teacher_data["sections"],
        generated_paper["sections"]
    ):
        expected_questions= expected["question_count"]
        generated_questions= len(
            generated["questions"]
        )

        if expected_questions != generated_questions:
            report["valid"] = False
            report["errors"].append(
                f"{expected['section_name']} has incorrect number of questions."
            )

        expected_marks= expected["marks"]

        generated_marks= sum(
            question.get("marks", 0)
            for question in generated["questions"]
        )

        if expected_marks != generated_marks:
            report["valid"] = False
            report["errors"].append(
                f"{expected['section_name']} marks mismatch."
            )

    return report