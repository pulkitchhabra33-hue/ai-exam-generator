from backend.services.pattern_analyzer import analyze_patterns
from backend.services.reference_retriever import retrieve_questions
from backend.services.knowledge_builder import build_knowledge

def format_list(title, items):
    if not items:
        return f"{title}: None\n"
    
    text= f"{title}\n"
    for item in items:
        text+= f"- {item}\n"
    
    text+= "\n"
    return text

def format_distribution(title, data):
    text= f"{title}\n"

    if not data:
        text += "None\n\n"
        return text
    
    for key, value in data.items():
        text+= f"- {key}: {value}\n"
    text+= "\n"
    return text

def format_reference_questions(questions):
    text= ""

    if not questions:
        return "No reference questions available.\n"
    
    for index, question in enumerate(questions, 1):
        text += f"""
Reference {index}

Question:
{question["question_text"]}

Type:
{question["question_type"]}

Difficulty:
{question["difficulty"]}

Cognitive:
{question["cognitive"]}

-------------------------

"""
    return text


def build_generation_context(
        exam_type,
        subject,
        filters
):
    
    analysis= analyze_patterns(
        exam_type,
        subject
    )

    knowledge= build_knowledge(
        exam_type,
        subject
    )

    references= retrieve_questions(
        exam_type,
        subject,
        filters
    )

    context= f"""
REFERENCE PAPER ANALYSIS

Repository Papers

{knowledge["papers"]}
"""
    
    context+= format_list(
        "Most Common Question Types",
        analysis["top_question_types"]
    )

    context+= format_list(
        "Most Common Chapters",
        analysis["top_chapters"]
    )

    context+= format_list(
        "Most Common Concepts",
        analysis["top_concepts"]
    )

    context+= format_distribution(
        "Difficulty Distribution",
        analysis["difficulty_distribution"]
    )

    context+= format_distribution(
        "Cognitive Distribution",
        analysis["cognitive_distribution"]
    )

    context += "\nReference Questions\n"

    context+= format_reference_questions(
        references
    )

    context += """

Instructions

Generate NEW questions.

Do NOT copy wording.

Do NOT copy numerical values.

Follow the style.

Follow the cognitive level.

Maintain similar difficulty.

"""

    return context