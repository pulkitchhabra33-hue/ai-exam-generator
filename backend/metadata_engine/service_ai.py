import json
from backend.core.ai_client import client
from backend.metadata_engine.prompt import build_metadata_prompt

def get_metadata(blueprint):
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
    
    return json.loads(content)