import os
import json

REFERENCE_FOLDER= "backend/reference_papers"
MAX_REFERENCE_QUESTIONS = 20

def load_repository(exam_type, subject):

    papers= []

    folder= os.path.join(
        REFERENCE_FOLDER,
        exam_type,
        subject
    )

    print("Repository Folder:", folder)

    #If folder doesn't exist
    if not os.path.exists(folder):
        return papers
    
    for file in os.listdir(folder):
        print("Found File:", file)
        if not file.endswith(".json"):
            continue

        path= os.path.join(folder, file)

        with open(path, "r", encoding= "utf-8") as f:
            papers.append(json.load(f))
            

    return papers

def retrieve_questions(exam_type, subject, filters):
    papers= load_repository(exam_type, subject)

    results= []

    for paper in papers:
        for question in paper["questions"]:
            match= True

            if filters.get("chapter"):
                if question.get("chapter") != filters["chapter"]:
                    match= False

            if filters.get("concept"):
                if question.get("concept") != filters["concept"]:
                    match= False

            if filters.get("difficulty"):
                if question.get("difficulty") != filters["difficulty"]:
                    match= False

            if filters.get("cognitive"):
                if question.get("cognitive") != filters["cognitive"]:
                    match= False

            if filters.get("question_type"):
                if question.get("question_type") != filters["question_type"]:
                    match= False

            if match:
                results.append(question)

    return results[:MAX_REFERENCE_QUESTIONS]           