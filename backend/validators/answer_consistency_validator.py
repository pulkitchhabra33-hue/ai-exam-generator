import json

from backend.core.ai_client import client
from backend.utils.logger import logger


def validate_answer_consistency(paper):
    """
    Check whether each generated question has:
    - a correct answer
    - an answer consistent with its options where applicable
    - a solution consistent with the answer
    - no obvious mathematical/factual contradiction

    Returns:
        (True, []) when no critical problems are found.

        (False, [
            "Question 2: ...",
            "Question 12: ..."
        ])
        when problems are found.
    """

    prompt = f"""
You are an examination-paper answer consistency validator.

Your ONLY job is to find critical correctness problems in the
provided examination paper.

Do NOT judge:
- writing style
- difficulty
- creativity
- question quality unless it affects correctness
- formatting
- whether a question could be improved stylistically

Focus ONLY on:

1. Whether the answer actually answers the question.
2. Whether an MCQ answer points to the correct option.
3. Whether the solution agrees with the answer.
4. Whether numerical calculations are mathematically correct.
5. Whether factual answers are correct.
6. Whether the answer key and solution contradict each other.
7. Whether the question itself contains enough information to determine
   the stated answer.
8. Whether the final answer contradicts an intermediate calculation
   shown in the solution.

IMPORTANT:
- Do not flag harmless wording differences.
- Do not flag an answer merely because the solution gives additional
  explanation.
- Only report a problem when there is a real correctness issue.
- Be especially careful with numerical calculations.
- Recalculate numerical answers independently.

For MCQs:
- Determine the correct option independently.
- Compare it with the answer field.
- Report an error if they disagree.

Return ONLY valid JSON:

{{
    "valid": true,
    "errors": []
}}

OR:

{{
    "valid": false,
    "errors": [
        {{
            "question_number": 2,
            "problem": "The answer field says A, but option C is correct because 3x + 5 = 20 gives x = 5."
        }}
    ]
}}

EXAMINATION PAPER:
{json.dumps(paper, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=60.0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content

        result = json.loads(content)

    except Exception as e:
        logger.exception(
            "Answer consistency validation failed."
        )

        return False, [
            f"Answer consistency validation could not be completed: {str(e)}"
        ]

    if not isinstance(result, dict):
        return False, [
            "Answer consistency validator returned an invalid result."
        ]

    valid = result.get("valid")

    errors = result.get("errors", [])

    if valid is True and not errors:
        return True, []

    if not isinstance(errors, list):
        return False, [
            "Answer consistency validator returned invalid error data."
        ]

    cleaned_errors = []

    for error in errors:

        if isinstance(error, dict):

            question_number = error.get(
                "question_number",
                "Unknown"
            )

            problem = str(
                error.get(
                    "problem",
                    ""
                )
            ).strip()

            if problem:
                cleaned_errors.append(
                    f"Question {question_number}: {problem}"
                )

        elif str(error).strip():

            cleaned_errors.append(
                str(error).strip()
            )

    if cleaned_errors:
        return False, cleaned_errors

    return False, [
        "Answer consistency validation failed."
    ]