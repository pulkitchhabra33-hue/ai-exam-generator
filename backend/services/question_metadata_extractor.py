import json
from backend.core.ai_client import client

def build_metadata_prompt(
        question
):
    return f"""
Analyze the following exam question.

Question:

{question}

Return ONLY valid JSON.

Required format:

{{
    "question": "",
    "marks": 0,
    "question_type": "",
    "difficulty": "",
    "cognitive_level": "",
    "chapter": "",
    "topic": ""
}}
"""

def extract_question_metadata(
        question
):
    prompt= build_metadata_prompt(question)

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
        response.choices[0].message.content
    )