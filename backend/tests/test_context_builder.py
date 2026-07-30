import json
from pathlib import Path

from backend.services.context_builder import (
    build_generation_context
)

repository = json.loads(
    Path(
        "backend/generated_repository/science_repository.json"
    ).read_text(
        encoding="utf-8"
    )
)

context = build_generation_context(
    query="Electricity",
    repository=repository,
    teacher_requirements="""
CBSE Class 10
Difficulty: Medium
Marks: 5
"""
)

print("=" * 60)
print("CONTEXT BUILDER TEST")
print("=" * 60)

print()

for item in context:
    print(item)