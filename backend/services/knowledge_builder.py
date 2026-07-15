from collections import Counter
from backend.services.reference_repository import load_blueprints

def build_knowledge(exam_type, subject):
    blueprints= load_blueprints(
        exam_type,
        subject
    )

    question_types= Counter()
    chapters= Counter()
    concepts= Counter()
    difficulty= Counter()
    cognitive= Counter()

    total_questions= 0

    for blueprint in blueprints:
        for question in blueprint["questions"]:

            total_questions += 1

            if question["question_type"]:
                question_types[
                    question["question_type"]
                    ] += 1
                
            if question["chapter"]:
                chapters[
                    question["chapter"]
                ] += 1

            if question["concept"]:
                concepts[
                    question["concept"]
                ] += 1

            if question["difficulty"]:
                difficulty[
                    question["difficulty"]
                ] += 1
            
            if question["cognitive"]:
                cognitive[
                    question["cognitive"]
                ] += 1

    knowledge= {
        "papers": len(blueprints),

        "total_questions": total_questions,

        "question_types": dict(question_types),

        "chapters": dict(chapters),

        "concepts": dict(concepts),

        "difficulty": dict(difficulty),

        "cognitive": dict(cognitive)
    }

    return knowledge