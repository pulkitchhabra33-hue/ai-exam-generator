from backend.services.semantic_search import semantic_search

repository = {
    "questions": [
        {
            "question": "Explain Ohm's Law.",
            "chapter": "Electricity",
            "difficulty": "Medium",
            "marks": 5,
            "question_type": "Long Answer",
            "cognitive_level": "Application",
            "embedding": [0.1] * 1536
        }
    ]
}

teacher_requirements = {
    "chapter": "Electricity",
    "difficulty": "Medium",
    "marks": 5,
    "question_type": "Long Answer",
    "cognitive_level": "Application"
}

results = semantic_search(
    query="Electricity",
    repository=repository,
    teacher_requirements=teacher_requirements,
    top_k=5
)

print("=" * 60)
print("INTELLIGENT RETRIEVAL TEST")
print("=" * 60)
print()

for score, question in results:
    print(score)
    print(question["question"])