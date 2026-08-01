import json
from backend.core.ai_client import client

def build_batch_prompt(
    questions,
    teacher_requirements
):
    return f"""
You are an expert examination paper setter.

Rewrite ALL of the following questions.

Requirements:

- Preserve the concept.
- Preserve the marks.
- Preserve the difficulty.
- Preserve the cognitive level.
- Do NOT copy wording.
- Create fresh questions.
- Keep the same order.

Teacher Requirements:

{teacher_requirements}

Questions:

{json.dumps(questions, indent=2)}

Return ONLY valid JSON.

{{
    "questions":[
        {{
            "question":"..."
        }}
    ]
}}
"""

def rewrite_questions(
    questions,
    teacher_requirements
):
    prompt= build_batch_prompt(
        questions,
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

    result= json.loads(
        response.choices[0]
        .message.content
    )

    return result["questions"]