import json
from pathlib import Path
from backend.services.semantic_search import generate_embedding

def cache_repository_embeddings(
    repository_path
):
    with open(
        repository_path,
        "r",
        encoding= "utf-8"
    ) as file:
        repository= json.load(file)

    print(repository["questions"][0]["embedding"][:5])

    for question in repository["questions"]:
        if "embedding" not in question:
            question["embedding"] = generate_embedding(
                question["question"]
            )

    with open(
        repository_path,
        "w",
        encoding= "utf-8"
    ) as file:
        
        json.dump(
            repository,
            file,
            indent=4,
            ensure_ascii=False
        )