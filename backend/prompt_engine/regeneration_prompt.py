from backend.prompt_engine.regeneration_rules import get_regeneration_rules
import json

def build_regeneration_prompt(
        teacher_data,
        generated_paper,
        feedback
):
    teacher_requirements= (
        f"Exam Type: {teacher_data.get("exam_type")}\n"
        f"Subject: {teacher_data.get("subject")}\n"
        f"Class: {teacher_data.get("class")}\n"
        f"Total Marks: {teacher_data.get("total_marks")}"
    )
    
    paper_json= json.dumps(
        generated_paper,
        indent=4,
        ensure_ascii=False
    )

    feedback_text= "\n".join(
        f"- {item}"
        for item in feedback
    )

    rules= get_regeneration_rules()

    prompt = f"""
You are an expert examination paper setter.

The following exam paper has already been generated.

A validation engine analyzed the paper and identified several issues.

Your task is NOT to generate a completely new paper.

Instead, modify only the questions necessary to satisfy the validation feedback while preserving the original paper structure.

==============================
Teacher Requirements
==============================

{teacher_requirements}

==============================
Generated Paper
==============================

{paper_json}

==============================
Validation Feedback
==============================

{feedback_text}

==============================
Instructions
==============================

{rules}
"""
    
    return prompt