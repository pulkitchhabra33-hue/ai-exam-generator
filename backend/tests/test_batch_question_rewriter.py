from backend.services.batch_question_rewriter import (
    rewrite_questions
)

questions = [

    {
        "question":"Explain Ohm's Law."
    },

    {
        "question":"State Kirchhoff's Voltage Law."
    },

    {
        "question":"What is electric current?"
    }

]

result = rewrite_questions(

    questions,

    """
CBSE Class 10

Difficulty: Medium

Marks: 5
"""

)

print("="*60)

print("BATCH REWRITER TEST")

print("="*60)

print()

for question in result:

    print(question)

    print()