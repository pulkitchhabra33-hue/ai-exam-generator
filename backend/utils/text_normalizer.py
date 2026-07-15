import re

QUESTION_VERB_MAP = {

    "state": "define",

    "write": "define",

    "define": "define",

    "mention": "define",

    "name": "define",

    "list": "list",

    "enumerate": "list",

    "calculate": "calculate",

    "find": "calculate",

    "determine": "calculate",

    "describe": "explain",

    "explain": "explain"

}

def normalize_question(text):
    text= text.lower()

    for original, replacement in QUESTION_VERB_MAP.items():
        text= re.sub(
            rf"\b{re.escape(original)}\b",
            replacement,
            text
        )

    return text