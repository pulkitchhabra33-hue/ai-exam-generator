from backend.services.repository_builder import (
    build_repository
)

sample_metadata = [

    {
        "question": "Explain Ohm's Law.",
        "marks": 2,
        "question_type": "Short Answer",
        "difficulty": "Easy",
        "cognitive_level": "Understanding",
        "chapter": "Electricity",
        "topic": "Ohm's Law"
    },

    {
        "question": "State Newton's Second Law.",
        "marks": 3,
        "question_type": "Short Answer",
        "difficulty": "Medium",
        "cognitive_level": "Recall",
        "chapter": "Force",
        "topic": "Newton's Laws"
    }

]

path = build_repository(
    sample_metadata,
    "science_repository"
)

print("=" * 60)
print("REPOSITORY BUILDER TEST")
print("=" * 60)

print()

print("Repository Saved At:")

print(path)