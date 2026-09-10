from backend.prompt_engine.regeneration_rules import get_regeneration_rules
import json


def build_regeneration_prompt(
        teacher_data,
        generated_paper,
        feedback
):

    teacher_requirements = (
        f"Exam Type: {teacher_data.get('exam_type')}\n"
        f"Subject: {teacher_data.get('subject')}\n"
        f"Class: {teacher_data.get('class')}\n"
        f"Total Marks: {teacher_data.get('total_marks')}"
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
You are an expert examination paper setter repairing an already generated examination paper.

The paper below has already been generated.

A validation engine has identified specific problems.

Your task is to repair the existing paper.

DO NOT generate a completely new paper.

DO NOT redesign the paper.

DO NOT change the paper structure.

==================================================
TEACHER REQUIREMENTS
==================================================

{teacher_requirements}

==================================================
EXISTING GENERATED PAPER
==================================================

{paper_json}

==================================================
VALIDATION FEEDBACK
==================================================

{feedback_text}

==================================================
MANDATORY STRUCTURE PRESERVATION
==================================================

The existing generated paper is the base paper.

You MUST preserve:

- The exact number of sections.
- The exact section order.
- The exact section names.
- The exact number of questions in every section.
- The exact question order.
- The exact number of questions for every question type.
- The position of every question.
- The marks of every question unless a validation error explicitly requires correcting marks.

DO NOT:

- Add questions.
- Remove questions.
- Merge questions.
- Split questions.
- Move questions between sections.
- Add sections.
- Remove sections.
- Change section names.
- Change the total number of questions.
- Change question types merely to make the paper easier to generate.

If a question is invalid, repair or replace the CONTENT of that existing question while keeping its position and required structure.

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

difficulty MUST be exactly:

- Easy
- Medium
- Hard

cognitive MUST be exactly:

- Recall
- Understanding
- Application
- Analysis

NEVER omit difficulty.

NEVER omit cognitive.

If the existing question already has valid difficulty and cognitive values, preserve them.

Only change them when the validation feedback requires a correction.

==================================================
QUESTION TYPE STRUCTURE
==================================================

MCQ:

- Exactly four options.
- Options must be non-empty.
- Answer must be A, B, C, or D.

True/False:

- No MCQ options.
- Answer must be True or False.

Fill in the Blanks:

- Question must contain ______.
- No MCQ options.

Assertion-Reason:

- Keep "assertion" as a separate field.
- Keep "reason" as a separate field.
- Both must be non-empty.
- Do not combine them into the question field.

Match the Following:

- Include "left_column".
- Include "right_column".
- Both must be lists.
- Both must be non-empty.
- Both must contain the same number of items.
- Do not use MCQ options.

Source-Based Questions:

- Include a meaningful "source" field.

Diagram-Based Questions:

- Include a meaningful "diagram" field.

Case Study:

- Include a meaningful "case" field.

==================================================
MARKS
==================================================

Preserve valid question marks.

The section marks must remain correct.

The total paper marks must remain correct.

If the validation feedback identifies a marks mismatch, correct the marks of the existing questions rather than adding or removing questions.

==================================================
QUESTION COUNTS
==================================================

The regenerated paper MUST contain exactly the same number of questions as the existing generated paper.

The regenerated paper MUST satisfy the requested question counts in teacher_data.

If a question type count is wrong, repair the type/content of existing questions.

Do not create additional questions.

Do not delete questions.

==================================================
VALIDATION REPAIR
==================================================

Fix every validation error in the feedback.

For missing fields:

- Add the missing field to the existing affected question.

For Assertion-Reason errors:

- Add or repair assertion and reason fields.

For Match the Following errors:

- Add or repair left_column and right_column.

For question-type errors:

- Correct the affected existing question while preserving its position.

For marks errors:

- Correct existing question marks without changing the number of questions.

For difficulty errors:

- Correct the difficulty values of existing questions.

For cognitive errors:

- Correct the cognitive values of existing questions.

For duplicate/similarity errors:

- Rewrite only the affected question content while preserving its type, marks, difficulty, cognitive level and position.

==================================================
FINAL CHECK
==================================================

Before returning the paper, verify:

- Section count.
- Section names.
- Section order.
- Question count.
- Question order.
- Question-type distribution.
- Marks per question.
- Section marks.
- Total marks.
- Difficulty distribution.
- Cognitive distribution.
- Every question has question.
- Every question has question_type.
- Every question has marks.
- Every question has difficulty.
- Every question has cognitive.
- Every question has answer.
- Every question has solution.
- Special question-type fields are present and valid.

Return the complete repaired paper.

Return ONLY valid JSON.

==================================================
REGENERATION RULES
==================================================

{rules}
"""

    return prompt