def calculate_rank_score(
    similarity,
    question,
    teacher_requirements
):
    score= similarity

    if (
        question.get("difficulty")
        ==
        teacher_requirements.get("difficulty")
    ):
        score += 0.05

    if (
        question.get("marks")
        ==
        teacher_requirements.get("marks")
    ):
        score += 0.05

    if (
        question.get("chapter")
        ==
        teacher_requirements.get("chapter")
    ):
        score += 0.05

    if (
        question.get("question_type")
        ==
        teacher_requirements.get("question_type")
    ):
        score += 0.03

    if (
        question.get("cognitive_level")
        ==
        teacher_requirements.get("cognitive_level")
    ):
        score += 0.02

    return score