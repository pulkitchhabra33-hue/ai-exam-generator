import re
from collections import Counter

MARKS_PATTERN= re.compile(r"\((\d+)\)")

def extract_marks(question):
    match= MARKS_PATTERN.search(question)

    if match:
        return int(match.group(1))

    return 0

def detect_question_type(question):
    text= question.lower()

    if "assertion" in text and "reason" in text:
        return "Assertion-Reason"

    if "(a)" in text and "(b)" in text:
        return "MCQ"

    if "calculate" in text:
        return "Numerical"

    if "explain" in text:
        return "Long Answer"

    return "Short Answer"

def build_blueprint(questions):
    marks_counter= Counter()
    type_counter= Counter()

    total_marks= 0

    for question in questions:

        marks= extract_marks(question)

        total_marks += marks

        marks_counter [marks] += 1

        question_type= detect_question_type(question)
        type_counter[question_type] += 1

    return {
        "total_questions": len(questions),
        "total_marks": total_marks,
        "marks_distribution": dict(marks_counter),
        "question_type_distribution": dict(type_counter)
    }