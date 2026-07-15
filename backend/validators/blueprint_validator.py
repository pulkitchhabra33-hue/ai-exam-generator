from collections import Counter
from backend.services.expected_blueprint import (get_expected_blueprint, normalize_distribution)

TOLERANCE= 0.05

def validate_distribution(
        generated_counter,
        expected_counter,
        report,
        title
):
    for key, expected_count in expected_counter.items():
        actual_count= generated_counter.get(key, 0)

        if abs(actual_count - expected_count) > TOLERANCE:
            report["valid"] = False
            report["errors"].append(
                f"{title} '{key}' mismatch: "
                f"expected {expected_count * 100:.2f}%,"
                f"got {actual_count * 100:.2f}%"
            )

def validate_blueprint(
        generated_paper,
        exam_type,
        subject
):
    report= {
        "valid": True,
        "errors": []
    }

    expected= get_expected_blueprint(
        exam_type,
        subject
    )

    generated_difficulty= Counter()
    generated_cognitive= Counter()
    generated_types= Counter()


    # -----------------------------
    # Single traversal
    # -----------------------------

    for section in generated_paper.get("sections", []):
        for question in section.get("questions", []):

            difficulty= question.get("difficulty")
            cognitive= question.get("cognitive")
            qtype= question.get("question_type")

            if difficulty:
                generated_difficulty[difficulty] += 1
            
            if cognitive:
                generated_cognitive[cognitive] += 1

            if qtype:
                generated_types[qtype] += 1


    generated_difficulty = normalize_distribution(
    generated_difficulty
    )

    generated_cognitive = normalize_distribution(
        generated_cognitive
    )

    generated_types = normalize_distribution(
        generated_types
    )

    # -----------------------------
    # Difficulty
    # -----------------------------

    validate_distribution(
        generated_difficulty,
        expected.get("difficulty_distribution", {}),
        report,
        "Difficulty"
    )
            

    # -----------------------------
    # Cognitive
    # -----------------------------

    validate_distribution(
        generated_cognitive,
        expected.get("cognitive_distribution", {}),
        report,
        "Cognitive"
    )

    # -----------------------------
    # Question Type
    # -----------------------------

    expected_types= expected.get(
        "question_type_distribution",
        {}
    )

    validate_distribution(
        generated_types,
        expected_types,
        report,
        "Question Type"
    )

    return report