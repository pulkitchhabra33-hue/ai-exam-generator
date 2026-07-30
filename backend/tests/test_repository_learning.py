from pathlib import Path

from backend.services.repository_learning import (
    add_generated_questions
)

questions = [

    {
        "question":
        "Explain Kirchhoff's Current Law.",

        "chapter":
        "Electricity",

        "difficulty":
        "Medium",

        "cognitive_level":
        "Application"

    }

]

add_generated_questions(

    Path(
        "backend/generated_repository/science_repository.json"
    ),

    questions

)

print("=" * 60)

print("REPOSITORY LEARNING TEST")

print("=" * 60)

print()

print("Question added successfully.")