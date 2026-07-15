def get_regeneration_rules():
    return """
Regenerate ONLY the necessary questions.

Do not rewrite the entire paper.

Preserve:

- Total marks
- Section structure
- Marks per question
- Blueprint

Only fix the issues mentioned in the feedback.

Do not introduce new issues.

Return valid JSON only.
"""