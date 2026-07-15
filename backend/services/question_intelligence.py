import re


DESCRIPTIVE_VERBS = [
    "explain",
    "describe",
    "discuss",
    "justify",
    "compare",
    "differentiate",
    "draw",
    "give reasons",
    "comment",
    "state with reason"
]


MCQ_OPTION_PATTERN = re.compile(
    r"\b[A-D][\).]"
    r"|\([A-D]\)"
    r"|Option\s+[A-D]",
    re.IGNORECASE
    )


def is_mcq(question_text):
    option_count= len(
        MCQ_OPTION_PATTERN.findall(question_text)
    )

    if option_count < 4:
        return False
    
    lower= question_text.lower()

    for verb in DESCRIPTIVE_VERBS:
        if verb in lower:
            return False
    
    return True


def enrich_question(question):
    text= question["question_text"].lower()

    # ---------- Diagram ----------

    if any(word in text for word in[
        "diagram",
        "figure",
        "graph",
        "flowchart",
        "table"
    ]):
        question["diagram"] = True

    case_words = [
        "read the following",
        "study the following",
        "case study",
        "passage",
        "based on the following",
        "observe the following"
    ]

    # ---------- Question Type ----------

    # ---------- Assertion Reason ----------

    if "assertion" in text and "reason" in text:
        question["question_type"] = "Assertion-Reason"
        question["assertion_reason"] = True

    # ---------- Case Study ----------

    elif any(word in text for word in case_words):
        question["question_type"] = "Case Study"
        question["case_based"] = True

    # ---------- MCQ ----------

    elif is_mcq(question["question_text"]):
        question["question_type"] = "MCQ"
    
    # ---------- VERY SHORT ANSWER ----------

    elif len(text.split()) < 15:
        question["question_type"] = "Very Short Answer"

    # ---------- SHORT ANSWER ----------

    elif len(text.split()) < 40:
        question["question_type"] = "Short Answer"

    # ---------- LONG ANSWER ----------

    else:
        question["question_type"] = "Long Answer"

    return question

def enrich_blueprint(blueprint):

    enriched_questions= []

    stats= blueprint["statistics"]

    for question in blueprint["questions"]:
        question= enrich_question(question)
        enriched_questions.append(question)
        qtype= question["question_type"]

        if qtype == "MCQ":
            stats["mcq"] += 1

        elif qtype == "Very Short Answer":
            stats["short_answer"] += 1

        elif qtype == "Short Answer":
            stats["short_answer"] += 1
        
        elif qtype == "Long Answer":
            stats["long_answer"] += 1
        
        elif qtype == "Case Study":
            stats["case_based"] += 1
        
        elif qtype == "Assertion-Reason":
            stats["assertion_reason"] += 1

    blueprint["questions"] = enriched_questions

    return blueprint