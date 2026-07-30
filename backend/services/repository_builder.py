import json
from pathlib import Path

REPOSITORY_FOLDER= Path("backend/generated_repository")

REPOSITORY_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

def build_repository(metadata_list, repository_name):
    repository= {
        "total_questions": len(metadata_list),
        "questions": metadata_list
    }

    path= (
        REPOSITORY_FOLDER /
        f"{repository_name}.json"
    )

    with path.open("w", encoding= "utf-8") as file:
        json.dump(
            repository,
            file,
            indent=4,
            ensure_ascii=False
        )

    return path