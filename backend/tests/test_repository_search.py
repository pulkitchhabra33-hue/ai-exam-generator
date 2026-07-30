from pathlib import Path

from backend.services.repository_search import (
    load_repository,
    search_questions
)

repository = load_repository(

    Path(
        "backend/generated_repository/science_repository.json"
    )

)

results = search_questions(

    repository,

    chapter="Electricity"

)

print("=" * 60)
print("REPOSITORY SEARCH TEST")
print("=" * 60)

print()

print("Questions Found:")

print(len(results))

print()

for question in results:

    print(question["question"])