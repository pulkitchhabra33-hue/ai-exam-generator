from backend.services.question_parser import parse_questions

def create_question_blueprint(extracted_text: str):
    blueprint= {
        "exam_info": {
            "exam_type": "",
            "subject": ""
        },

    "statistics": {
        "total_questions": 0,
        "mcq": 0,
        "short_answer": 0,
        "long_answer": 0,
        "case_based": 0,
        "assertion_reason": 0
    },

    "questions": []
    }
    parsed_questions= parse_questions(extracted_text)
    
    blueprint["statistics"]["total_questions"] = len(parsed_questions)

    for item in parsed_questions:

        question= {
            "question_no": item["question_no"],
            "question_text": item["question_text"],
            "question_type": "",
            "marks": None,
            "chapter": None,
            "concept": None,
            "difficulty": None,
            "cognitive": None,
            "case_based": False,
            "assertion_reason": False,
            "diagram": False
        }

        blueprint["questions"].append(question)

    return blueprint