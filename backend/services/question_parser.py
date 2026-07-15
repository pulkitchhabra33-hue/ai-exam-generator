import re

MAIN_QUESTION_PATTERNS = [

    r'^\s*(\d+)\.\s+',          # 1. Question

    r'^\s*(\d+)\)\s+',          # 1) Question

    r'^\s*Q\.?\s*(\d+)\s+',     # Q1  or Q.1

    r'^\s*Q\.?\s*(\d+)\)\s+',

    r'^\s*Question\s+(\d+)\s*[:.]?\s*'  # Question 1
]

def parse_questions(text):
    text= text.replace("\r", "")
    lines= text.splitlines()

    questions= []
    current_question= None

    compiled_patterns= [
        re.compile(pattern)
        for pattern in MAIN_QUESTION_PATTERNS
    ]

    for line in lines:
        line= line.strip()
        
        if not line:
            continue

        match= None
        for pattern in compiled_patterns:
            match= pattern.match(line)

            if match:
                break

        if match:
            if current_question:
                questions.append(current_question)

            current_question= {
                "question_no": int(match.group(1)),
                "question_text": line[match.end():].strip()
            }

        else:
            if current_question:
                current_question["question_text"] += (
                    "\n" + line
                )

    if current_question:
        questions.append(current_question)

    return questions