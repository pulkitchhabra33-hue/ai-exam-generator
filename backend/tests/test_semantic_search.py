import json

from pathlib import Path

from backend.services.semantic_search import (
    semantic_search
)

repository = json.loads(

    Path(
        "backend/generated_repository/science_repository.json"
    ).read_text(
        encoding="utf-8"
    )

)

results = semantic_search(

    "Electricity",

    repository,
    top_k= 1

)

print("="*60)

print("SEMANTIC SEARCH TEST")

print("="*60)

print()

for score, question in results:

    print(

        round(score, 3),

        "-",

        question["question"]

    )