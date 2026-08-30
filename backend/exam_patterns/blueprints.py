CBSE_BLUEPRINT = """
CBSE QUESTION DESIGN RULES

PREFER:

- Competency-based questions
- Application-based questions
- Real-life contexts
- Case-study questions
- Source-based questions
- Analytical thinking

AVOID:

- Excessive direct recall
- Pure definition questions
- Repetitive textbook exercises

QUESTION STYLE:

- Similar to recent CBSE board papers
- NCERT aligned
- Student-friendly language
"""


JEE_BLUEPRINT = """
JEE QUESTION DESIGN RULES

PREFER:

- Multi-concept problems
- Concept integration
- Non-routine thinking
- Higher-order reasoning
- Mathematical insight

AVOID:

- Direct formula substitution
- One-step solutions
- Basic textbook exercises
- Memorization-focused questions

QUESTION STYLE:

- Similar to JEE Main and JEE Advanced
- Analytical
- Reasoning-heavy
- Concept-driven
"""


NEET_BLUEPRINT = """
NEET QUESTION DESIGN RULES

PREFER:

- NCERT language
- Assertion-reason
- Concept application
- Scientific reasoning

AVOID:

- Out-of-syllabus content
- Ambiguous biology terminology

QUESTION STYLE:

- Medical entrance pattern
- NCERT-centered
"""


ICSE_BLUEPRINT = """
ICSE QUESTION DESIGN RULES

PREFER:

- Detailed explanations
- Interpretation
- Analytical writing

AVOID:

- One-line answers
- Oversimplified questions

QUESTION STYLE:

- Academic
- Descriptive
- Formal
"""


SSC_BLUEPRINT = """
SSC QUESTION DESIGN RULES

PREFER:

- Fast solving
- Objective assessment
- Practical reasoning

AVOID:

- Long descriptive questions
- Excessive theory

QUESTION STYLE:

- Government exam pattern
- Time-efficient
"""


def get_blueprint(exam_type):
    if not exam_type:
        return ""
    
    exam_type= exam_type.lower()

    if "cbse" in exam_type:
        return CBSE_BLUEPRINT
    
    elif "jee" in exam_type:
        return JEE_BLUEPRINT
    
    elif "neet" in exam_type:
        return NEET_BLUEPRINT
    
    elif "icse" in exam_type:
        return ICSE_BLUEPRINT
    
    elif "ssc" in exam_type:
        return SSC_BLUEPRINT
    
    return ""


CBSE_COGNITIVE_BLUEPRINT = {
    "recall": 20,
    "understanding": 30,
    "application": 35,
    "analysis": 15
}

JEE_COGNITIVE_BLUEPRINT = {
    "recall": 5,
    "understanding": 25,
    "application": 40,
    "analysis": 30
}

NEET_COGNITIVE_BLUEPRINT = {
    "recall": 25,
    "understanding": 35,
    "application": 25,
    "analysis": 15
}

ICSE_COGNITIVE_BLUEPRINT = {
    "recall": 15,
    "understanding": 35,
    "application": 30,
    "analysis": 20
}

SSC_COGNITIVE_BLUEPRINT = {
    "recall": 30,
    "understanding": 25,
    "application": 30,
    "analysis": 15
}

DEFAULT_COGNITIVE_BLUEPRINT = {
    "recall": 25,
    "understanding": 30,
    "application": 30,
    "analysis": 15
}


def get_cognitive_blueprint(exam_type):
    if not exam_type:
        return DEFAULT_COGNITIVE_BLUEPRINT
    
    exam_type= exam_type.lower()

    if "cbse" in exam_type:
        return CBSE_COGNITIVE_BLUEPRINT
    elif "icse" in exam_type:
        return ICSE_COGNITIVE_BLUEPRINT
    elif "jee" in exam_type:
        return JEE_COGNITIVE_BLUEPRINT
    elif "ssc" in exam_type:
        return SSC_COGNITIVE_BLUEPRINT
    elif "neet" in exam_type:
        return NEET_COGNITIVE_BLUEPRINT

    return DEFAULT_COGNITIVE_BLUEPRINT