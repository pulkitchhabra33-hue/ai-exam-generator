from collections import Counter
from backend.services.expected_blueprint import (
    get_expected_blueprint
)


def allocate_integer_counts(
        total_questions,
        distribution
):

    if total_questions <= 0 or not distribution:
        return {}

    raw = {
        key: total_questions * value
        for key, value in distribution.items()
    }

    counts = {
        key: int(value)
        for key, value in raw.items()
    }

    remaining = (
        total_questions
        - sum(counts.values())
    )

    remainders = sorted(
        distribution.keys(),
        key=lambda key: (
            raw[key] - counts[key]
        ),
        reverse=True
    )

    for key in remainders[:remaining]:
        counts[key] += 1

    return counts


def validate_count_distribution(
        generated_counter,
        expected_distribution,
        report,
        title,
        total_questions
):

    expected_counts = allocate_integer_counts(
        total_questions,
        expected_distribution
    )

    all_keys = set(
        expected_counts
    ) | set(
        generated_counter
    )

    for key in all_keys:

        expected_count = expected_counts.get(
            key,
            0
        )

        actual_count = generated_counter.get(
            key,
            0
        )

        if actual_count != expected_count:

            report["valid"] = False

            report["errors"].append(
                f"{title} '{key}' mismatch: "
                f"expected {expected_count} questions, "
                f"got {actual_count}"
            )


def validate_blueprint(
        generated_paper,
        exam_type,
        subject
):

    report = {
        "valid": True,
        "errors": []
    }

    expected = get_expected_blueprint(
        exam_type,
        subject
    )

    generated_questions = []

    for section in generated_paper.get(
        "sections",
        []
    ):

        generated_questions.extend(
            section.get(
                "questions",
                []
            )
        )

    total_questions = len(
        generated_questions
    )

    if total_questions == 0:
        return report

    generated_difficulty = Counter()
    generated_cognitive = Counter()
    generated_types = Counter()

    for question in generated_questions:

        difficulty = question.get(
            "difficulty"
        )

        cognitive = question.get(
            "cognitive"
        )

        question_type = question.get(
            "question_type"
        )

        if difficulty:
            generated_difficulty[
                difficulty
            ] += 1

        if cognitive:
            generated_cognitive[
                cognitive
            ] += 1

        if question_type:
            generated_types[
                question_type
            ] += 1

    validate_count_distribution(
        generated_difficulty,
        expected.get(
            "difficulty_distribution",
            {}
        ),
        report,
        "Difficulty",
        total_questions
    )

    validate_count_distribution(
        generated_cognitive,
        expected.get(
            "cognitive_distribution",
            {}
        ),
        report,
        "Cognitive",
        total_questions
    )

    expected_types = expected.get(
        "question_type_distribution",
        {}
    )

    if expected_types:

        validate_count_distribution(
            generated_types,
            expected_types,
            report,
            "Question Type",
            total_questions
        )

    return report