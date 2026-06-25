from backend.prompt_engine.system_prompt import get_system_prompt
from backend.prompt_engine.exam_context import get_exam_context
from backend.prompt_engine.generation_rules import get_generation_rules
from backend.prompt_engine.output_rules import get_output_rules

def build_prompt(
        data,
        exam_type,
        section_data,
        instructions,
        reference_paper,
        json_format,
        cognitive_blueprint,
        exam_prompt,
        exam_blueprint
):
    prompt= f"""

{get_system_prompt()}

{exam_prompt}

{exam_blueprint}

{get_exam_context(
    data,
    exam_type,
    section_data,
    instructions,
    reference_paper
)}

{get_generation_rules}

{get_output_rules(
    json_format,
    cognitive_blueprint
)}
"""
    
    return prompt