from backend.prompt_engine.regeneration_rules import get_regeneration_rules
import json


def build_locked_blueprint(
        teacher_data
):

    blueprint = []

    for section_index, section in enumerate(
        teacher_data.get(
            "sections",
            []
        ),
        start=1
    ):

        section_name = section.get(
            "section_name"
        ) or f"Section {section_index}"

        section_data = {
            "section_name": section_name,
            "question_count": int(
                section.get(
                    "question_count",
                    0
                )
            ),
            "marks": int(
                section.get(
                    "marks",
                    0
                )
            ),
            "question_groups": []
        }

        for group in section.get(
            "question_groups",
            []
        ):

            section_data[
                "question_groups"
            ].append(
                {
                    "question_type": group.get(
                        "question_type"
                    ),
                    "question_count": int(
                        group.get(
                            "question_count",
                            0
                        )
                    ),
                    "marks_per_question": int(
                        group.get(
                            "marks_per_question",
                            0
                        )
                    ),
                    "marks": int(
                        group.get(
                            "marks",
                            0
                        )
                    )
                }
            )

        blueprint.append(
            section_data
        )

    return blueprint


def build_regeneration_prompt(
        teacher_data,
        generated_paper,
        feedback
):

    teacher_requirements = (
        f"Exam Type: "
        f"{teacher_data.get('exam_type')}\n"
        f"Subject: "
        f"{teacher_data.get('subject')}\n"
        f"Class: "
        f"{teacher_data.get('class_name')}\n"
        f"Total Marks: "
        f"{teacher_data.get('total_marks')}"
    )

    locked_blueprint = build_locked_blueprint(
        teacher_data
    )

    blueprint_json = json.dumps(
        locked_blueprint,
        indent=4,
        ensure_ascii=False
    )

    paper_json = json.dumps(
        generated_paper,
        indent=4,
        ensure_ascii=False
    )

    feedback_text = "\n".join(
        f"- {item}"
        for item in feedback
    )

    rules = get_regeneration_rules()

    prompt = f"""
You are repairing an already generated examination paper.

You MUST repair the existing paper.

You are NOT allowed to redesign the paper.

==================================================
TEACHER REQUIREMENTS
==================================================

{teacher_requirements}

==================================================
LOCKED EXAM BLUEPRINT
==================================================

The following blueprint is authoritative.

It comes directly from the teacher's requested paper structure.

{blueprint_json}

The final paper MUST match this blueprint exactly.

==================================================
EXISTING PAPER
==================================================

{paper_json}

==================================================
VALIDATION FEEDBACK
==================================================

{feedback_text}

==================================================
ABSOLUTE STRUCTURE RULES
==================================================

The locked blueprint has priority over the generated paper.

The final paper MUST have:

- Exactly the specified number of sections.
- Exactly the specified section names.
- Exactly the specified section order.
- Exactly the specified number of questions in every section.
- Exactly the specified number of questions for every question type.
- Exactly the specified marks per question.
- Exactly the specified section marks.
- Exactly the specified total marks.

Do NOT:

- Add questions.
- Remove questions.
- Merge questions.
- Split questions.
- Move questions between sections.
- Invent new question groups.
- Remove question groups.
- Change question counts.
- Change section names.

If the existing paper contains an incorrect question type, replace that question with the required question type while keeping the same position.

If the existing paper contains incorrect content, rewrite that question.

==================================================
QUESTION METADATA
==================================================

Every question MUST contain:

- question
- question_type
- marks
- difficulty
- cognitive
- answer
- solution

difficulty must be one of:

- Easy
- Medium
- Hard

cognitive must be one of:

- Recall
- Understanding
- Application
- Analysis

==================================================
SPECIAL QUESTION TYPES
==================================================

MCQ:
- Exactly four options.
- Answer must be A, B, C, or D.

True/False:
- No MCQ options.
- Answer must be True or False.

Fill in the Blanks:
- Question must contain ______.

Assertion-Reason:
- assertion must be a separate non-empty field.
- reason must be a separate non-empty field.

Match the Following:
- left_column must be a non-empty list.
- right_column must be a non-empty list.
- Both columns must have equal length.

Source-Based Questions:
- source must be present and meaningful.

Diagram-Based Questions:
- diagram must be present and meaningful.

Case Study:
- case must be present and meaningful.

==================================================
VALIDATION REPAIR
==================================================

Fix every validation error.

However, fixing an error MUST NOT violate the locked blueprint.

If question-type counts are wrong:

- Correct existing questions.
- Do not add or remove questions.

If marks are wrong:

- Correct existing question marks.
- Do not add or remove questions.

If difficulty or cognitive values are wrong:

- Correct the metadata of existing questions.

If a special field is missing:

- Add it to the affected existing question.

If a question is duplicated or too similar:

- Rewrite its content while preserving its required type, position and marks.

==================================================
FINAL VERIFICATION
==================================================

Before returning JSON verify:

- Section count exactly matches the locked blueprint.
- Section names exactly match.
- Section order exactly matches.
- Question count exactly matches.
- Every question-type count exactly matches.
- Every question has the required marks.
- Every section has the required marks.
- Total marks exactly match.
- Every question has difficulty.
- Every question has cognitive.
- Every question has answer.
- Every question has solution.
- All special question-type fields are valid.

Return the COMPLETE repaired paper.

Return ONLY valid JSON.

==================================================
EXISTING REGENERATION RULES
==================================================

{rules}
"""

    return prompt