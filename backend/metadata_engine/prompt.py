import json

def build_metadata_prompt(blueprint):
    questions= []

    for question in blueprint['questions']:
        questions.append({
            "question_no": question['question_no'],
            "question_text": question['question_text']
        })

    prompt= prompt = f"""
You are an expert curriculum analyst.

For every question identify:

- Subject
- Chapter
- Concept
- Difficulty
- Cognitive Level

Difficulty must be one of:

Easy
Medium
Hard

Cognitive level must be one of:

Recall
Understanding
Application
Analysis

Identify the MOST SPECIFIC chapter.

Identify the MOST SPECIFIC concept.

Do NOT leave any field empty.

Return ONLY valid JSON.

Return format:

{{
    "questions":[
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

Questions:

{json.dumps(questions, indent= 4)}
"""
    
    return prompt