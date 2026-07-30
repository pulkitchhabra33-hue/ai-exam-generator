from backend.services.question_rewriter import (
    rewrite_question
)

question = """
Explain Ohm's Law.
"""

teacher_requirements = """
Class 10 CBSE

Difficulty: Medium

Marks: 5
"""

result = rewrite_question(

    question,

    teacher_requirements

)

print("="*60)

print("QUESTION REWRITER TEST")

print("="*60)

print()

print(result)