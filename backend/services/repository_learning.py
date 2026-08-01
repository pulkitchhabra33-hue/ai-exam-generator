import json 
from pathlib import Path
from datetime import datetime

def add_generated_questions(
    repository_path,
    questions
):
    with open(
        repository_path,
        "r",
        encoding= "utf-8"
    ) as file:
        repository= json.load(file)

    for question in questions:
        question["times_used"]= 0
        question["last_used"]= None
        question["source"]= "generated"
        repository["questions"].append(question)

    repository["total_questions"]= len(repository["questions"])

    with open(
        repository_path,
        "w",
        encoding= "utf-8"
    ) as file:
        json.dump(
            repository,
            file,
            indent=4,
            ensure_ascii= False
        )