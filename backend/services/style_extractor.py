import re

COMMAND_VERBS = {

    "Recall": [

        "state",
        "define",
        "name",
        "list",
        "mention",
        "identify",
        "write"
    ],

    "Understanding": [

        "explain",
        "describe",
        "discuss",
        "comment",
        "give",
        "justify"
    ],

    "Analysis": [

        "compare",
        "differentiate",
        "distinguish",
        "analyse",
        "analyze",
        "interpret",
        "examine"
    ],

    "Application": [

        "calculate",
        "find",
        "determine",
        "evaluate",
        "solve",
        "draw",
        "sketch",
        "label",
        "construct"
    ]
}

SCENARIO_WORDS = [

    "student",

    "teacher",

    "experiment",

    "company",

    "person",

    "factory",

    "shop",

    "hospital"

]

DIAGRAM_WORDS = [

    "diagram",

    "figure",

    "graph",

    "chart",

    "table",

    "flowchart",

    "circuit",

    "illustration",

    "image",

    "picture",

    "map",

    "bar graph",

    "line graph",

    "pie chart",

    "histogram",

    "schematic"

]


def extract_command_verb(text):
    words = re.findall(
    r"[a-zA-Z]+",
    text.lower()
)

    for category, verbs in COMMAND_VERBS.items():
        for verb in verbs:
            if verb in words:
                return verb, category
    return None, None


def extract_style(question):
    text= question["question_text"]
    words= text.split()

    word_count= len(words)

    if word_count < 12:
        length_of_question= "Short"
    elif word_count < 30:
        length_of_question= "Medium"
    else:
        length_of_question= "Long"

    
    #For Numericals:
    numerical= bool(re.search(r"\d", text))

    #For scenario-based questions:
    scenario= any(
        word in text.lower() for word in SCENARIO_WORDS
    )

    #For diagram-based questions:
    diagram= any(
        word in text.lower() for word in DIAGRAM_WORDS
    )

    #For command verbs:
    verb, category= extract_command_verb(question["question_text"])

    question["command_verb"] = verb

    question["verb_category"] = category

    question["question_length"] = length_of_question

    question["word_count"] = word_count

    question["numerical"] = numerical

    question["scenario_based"] = scenario

    question["diagram_based"] = diagram

    return question