import re

QUESTION_PATTERN= re.compile(
    r"(?=\n?\d+\.\s)"
)

def extract_questions(text:str):
    parts= QUESTION_PATTERN.split(text)

    questions= []
    for part in parts:
        part= part.strip()

        if not part:
            continue

        questions.append(part)

    return questions

def clean_questions(questions):
    cleaned= []

    for question in questions:
        question= re.sub(
            r"\s+",
            " ",
            question
        ).strip()

        cleaned.append(question)

    return cleaned

def extract_and_clean_questions(text):
    questions= extract_questions(text)

    return clean_questions(questions)