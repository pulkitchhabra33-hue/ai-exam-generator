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

• marks

• answer

• solution

JSON Structure:

{json_format}

--------------------------------------------------
FINAL VERIFICATION
--------------------------------------------------

Before returning the paper verify:

• Total marks

• Section marks

• Question count

• Cognitive distribution

Recall:
{cognitive_blueprint["recall"]}%

Understanding:
{cognitive_blueprint["understanding"]}%

Application:
{cognitive_blueprint["application"]}%

Analysis:
{cognitive_blueprint["analysis"]}%

Return only JSON.
"""