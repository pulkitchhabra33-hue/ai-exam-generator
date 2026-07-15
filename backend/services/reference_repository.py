import json
import os

def save_blueprint(blueprint, exam_type, subject):
    folder = os.path.join(
        "backend",
        "reference_papers",
        exam_type.lower(),
        subject.lower()
    )

    os.makedirs(folder, exist_ok= True)

    paper_number= len(os.listdir(folder)) + 1

    file_path= os.path.join(
        folder,
        f"paper_{paper_number}.json"
    )

    with open(file_path, "w", encoding= "utf-8") as file:
        json.dump(
            blueprint,
            file, 
            indent= 4,
            ensure_ascii= False
        )

    return file_path


def load_blueprints(exam_type, subject):
    folder= os.path.join(
        "backend",
        "reference_papers",
        exam_type.lower(),
        subject.lower()
    )

    if not os.path.exists(folder):
        return []
    
    papers= []

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path= os.path.join(folder, filename)
            
            with open(path, encoding= "utf-8") as file:
                papers.append(json.load(file))

    return papers