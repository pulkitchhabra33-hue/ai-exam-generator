from backend.services.retrieval_ranker import (
    calculate_rank_score
)

question = {
    "chapter": "Electricity",
    "difficulty": "Medium",
    "marks": 5,
    "question_type": "Numerical",
    "cognitive_level": "Application"
}

teacher_requirements = {
    "chapter": "Electricity",
    "difficulty": "Medium",
    "marks": 5,
    "question_type": "Numerical",
    "cognitive_level": "Application"
}

score = calculate_rank_score(
    similarity=0.87,
    question=question,
    teacher_requirements=teacher_requirements
)

print("=" * 60)
print("RETRIEVAL RANKER TEST")
print("=" * 60)
print()
print(score)