import json
from pathlib import Path

def load_repository(repository_path: Path):
    with repository_path.open("r", encoding="utf-8") as file:
        return json.load(file)

def search_questions(repository, **filters):
    questions= repository["questions"]

    results= []

    for question in questions:
        matched= True

        for key, value in filters.items():
            if question.get(key) != value:
                matched= False
                break

        if matched:
            results.append(question)

    return results