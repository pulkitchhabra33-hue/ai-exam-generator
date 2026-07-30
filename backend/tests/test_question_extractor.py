from backend.services.question_extractor import (
    extract_and_clean_questions
)

sample_text = """
1. Define Ohm's Law.

2. Explain Photosynthesis.

3. What is Momentum?

4. Explain Newton's Second Law.
"""

questions = extract_and_clean_questions(
    sample_text
)

print("=" * 60)
print("QUESTION EXTRACTION TEST")
print("=" * 60)

print()

print("Questions Found:", len(questions))

print()

for index, question in enumerate(
        questions,
        start=1
):
    print(f"{index}. {question}")