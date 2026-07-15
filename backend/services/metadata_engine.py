import json
from backend.core.ai_client import client

def build_metadata_prompt(blueprint):
    questions=  []

    for question in blueprint["questions"]:
        questions.append({
            "question_no": question["question_no"],
            "question_text": question["question_text"]
        })

    prompt = f"""
You are an expert curriculum analyst.

For every question identify:

1. Subject

2. Chapter

3. Concept

4. Difficulty

5. Cognitive Level

Difficulty must be one of:

Easy
Medium
Hard

Cognitive level must be one of:

Recall
Understanding
Application
Analysis

Return ONLY JSON.

Questions:

{json.dumps(questions, indent=4)}

Return format:

{{
    "questions": [
        {{
        "question_no":1,

        "subject":"",

        "chapter":"",

        "concept":"",

        "difficulty":"",

        "cognitive":""
        }}
    ]
}}
"""
    
    return prompt


def generate_metadata(blueprint):
    prompt= build_metadata_prompt(blueprint)

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

    content= response.choices[0].message.content
    metadata= json.loads(content)

    return merge_metadata(
        blueprint,
        metadata
    )


def merge_metadata(blueprint, metadata):
    metadata_map= {}

    for item in metadata["questions"]:
        metadata_map[item["question_no"]]= item

    for question in blueprint["questions"]:
        item= metadata_map.get(question["question_no"])

        if item:
            question["subject"] = item["subject"]
            question["chapter"] = item["chapter"]
            question["concept"] = item["concept"]
            question["difficulty"] = item["difficulty"]
            question["cognitive"] = item["cognitive"]

    return blueprint            