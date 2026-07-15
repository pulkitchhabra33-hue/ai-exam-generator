from backend.prompt_engine.system_prompt import get_system_prompt
from backend.prompt_engine.exam_context import get_exam_context
from backend.prompt_engine.generation_rules import get_generation_rules
from backend.prompt_engine.output_rules import get_output_rules
from backend.services.generation_context import build_generation_context

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
    
    filters= {
            "subject": data.get("subject"),
            "chapter": data.get("chapter"),
            "concept": data.get("concept"),
            "difficulty": data.get("difficulty"),
            "question_type": data.get("question_type")
        }
    
    repository_context= build_generation_context(
        exam_type,
        data["subject"],
        filters
    )
    
    prompt= f"""

{get_system_prompt()}

=================================================
GENERATION RULES
=================================================

{get_generation_rules()}

=================================================
REFERENCE PAPER INTELLIGENCE
=================================================

{repository_context}

=================================================
TEACHER REQUIREMENTS
=================================================

{get_exam_context(
    data,
    exam_type,
    section_data,
    instructions,
    reference_paper
)}

=================================================
EXAM CONFIGURATION
=================================================

{exam_prompt}

=================================================
EXAM BLUEPRINT
=================================================

{exam_blueprint}

=================================================
OUTPUT FORMAT
=================================================

{get_output_rules(
    json_format,
    cognitive_blueprint
)}
"""
    
    return prompt