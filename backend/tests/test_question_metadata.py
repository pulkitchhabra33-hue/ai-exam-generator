from backend.services.question_metadata_extractor import (
    extract_question_metadata
)

question = """
Explain Ohm's Law. (2)
"""

metadata = extract_question_metadata(
    question
)

print("=" * 60)
print("QUESTION METADATA TEST")
print("=" * 60)

print()

for key, value in metadata.items():

    print(f"{key}: {value}")