def get_output_rules(
        json_format,
        cognitive_blueprint
):
    return f"""
--------------------------------------------------
OUTPUT RULES
--------------------------------------------------

Return ONLY valid JSON.

Each question must contain:

• question
• question_type
• marks
• difficulty
• cognitive
• answer
• solution

difficulty must be exactly one of:

• Easy
• Medium
• Hard

cognitive must be exactly one of:

• Recall
• Understanding
• Application
• Analysis

The cognitive level must match the requested cognitive distribution.

JSON Structure:

{json_format}

--------------------------------------------------
FINAL VERIFICATION
--------------------------------------------------

Before returning the paper verify:

• Total marks
• Section marks
• Question count
• Question type distribution
• Difficulty distribution
• Cognitive distribution
• Every question has a non-empty question field
• Every question has question_type
• Every question has marks
• Every question has difficulty
• Every question has cognitive
• Every question has answer
• Every question has solution

Cognitive distribution:

Recall:
{cognitive_blueprint["recall"]}%

Understanding:
{cognitive_blueprint["understanding"]}%

Application:
{cognitive_blueprint["application"]}%

Analysis:
{cognitive_blueprint["analysis"]}%

Use the difficulty distribution specified by the exam blueprint and repository intelligence.

Return only JSON.
"""