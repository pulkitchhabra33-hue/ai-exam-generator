import json
from backend.core.ai_client import client

def build_rewrite_prompt(
    question,
    teacher_requirements
):
    return f"""
You are an expert examination paper setter.

Rewrite the following question.

Requirements:

- Preserve the concept.
- Preserve the marks.
- Preserve the difficulty.
- Preserve the cognitive level.
- Do NOT copy wording.
- Produce a completely fresh question.

Teacher Requirements:

{teacher_requirements}

Question:

{question}

Return ONLY valid JSON.

{{
    "question": ""
}}
"""

def rewrite_question(
    question,
    teacher_requirements
):
    prompt= build_rewrite_prompt(
        question,
        teacher_requirements
    )

    response= client.chat.completions.create(
        model= "gpt-4o-mini",
        response_format= {
            "type": "json_object"
        },
        messages= [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return json.loads(
        response.choices[0]
        .message.content
    )