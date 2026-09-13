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
You are an expert examination-paper repair engine.

The examination paper below has already been generated.

Your task is to REPAIR the existing paper.

This is NOT a request to create a new examination paper.

Make the SMALLEST possible changes required to remove the validation errors.

==================================================
TEACHER REQUIREMENTS
==================================================

{teacher_requirements}

==================================================
EXISTING EXAMINATION PAPER
==================================================

{paper_json}

==================================================
VALIDATION ERRORS THAT MUST BE FIXED
==================================================

{feedback_text}

==================================================
CORE REPAIR PRINCIPLE
==================================================

Preserve everything that is already correct.

Only modify questions that are necessary to fix the validation errors.

Do not randomly rewrite the paper.

Do not regenerate the complete paper from scratch.

Do not change valid questions unnecessarily.

==================================================
STRUCTURE LOCK
==================================================

The following are LOCKED:

- Number of sections
- Section order
- Section names
- Number of questions
- Question grouping
- Question types
- Marks per question
- Section marks
- Total marks
- Subject
- Class
- Syllabus requirements

Do not change any of these unless the validation feedback explicitly reports
a problem with that specific item.

==================================================
COGNITIVE DISTRIBUTION REPAIR
==================================================

Cognitive levels are:

- Recall
- Understanding
- Application
- Analysis

The validation feedback contains the EXACT expected and generated counts.

Use those counts as the source of truth.

For example:

If the validator says:

Application expected 8, got 9

then the final paper must contain exactly:

Application = 8

Do not guess the target.

If the validator says:

Analysis expected 4, got 5

then the final paper must contain exactly:

Analysis = 4

Do not guess the target.

When a cognitive level is too high:

- Find a suitable existing question that can genuinely belong to the required
  lower cognitive level.
- Prefer modifying the smallest possible number of questions.
- Keep the question type unchanged.
- Keep the marks unchanged.
- Keep the section unchanged.
- Keep the topic and syllabus relevance.
- Rewrite the question only when necessary for the new cognitive level.

When a cognitive level is too low:

- Find a suitable existing question that can genuinely support the required
  higher cognitive level.
- Prefer modifying the smallest possible number of questions.
- Do not simply change the "cognitive" label.
- The actual question must support the assigned cognitive level.

After repairing the cognitive distribution, count ALL questions again.

==================================================
DIFFICULTY DISTRIBUTION REPAIR
==================================================

Difficulty levels are:

- Easy
- Medium
- Hard

If validation reports a difficulty mismatch:

- Use the exact expected counts from the validation feedback.
- Do not guess the target.
- Modify the smallest possible number of suitable questions.
- Keep question type unchanged.
- Keep marks unchanged.
- Keep section unchanged.
- The question must genuinely match the assigned difficulty.
- Do not merely change the difficulty label.

After repairing difficulty, count ALL questions again.

==================================================
QUESTION TYPE RULES
==================================================

MCQ:
- Exactly 4 options.
- Only one correct option.
- Answer must be A, B, C or D.

True/False:
- One clear factual statement.
- Answer must be True or False.

Fill in the Blanks:
- Question must contain ______.
- Answer must be the missing word, value, term or expression.

Assertion-Reason:
- assertion and reason must be separate fields.
- They must be logically related.
- The answer must correctly describe their relationship.

Match the Following:
- left_column and right_column must exist.
- Both must be non-empty.
- Both must have equal length.
- Answer must specify the correct matches.

Source-Based Questions:
- source must exist.
- The question must depend on the source.

Diagram-Based Questions:
- diagram must exist.
- The question must genuinely depend on the diagram.

Case Study:
- case must exist.
- The question must genuinely depend on the case.

Application-based:
- Must require application of a concept, formula, principle or method to a new
  situation.
- Must not be simple recall.

HOTS:
- Must require genuine higher-order reasoning, analysis, evaluation,
  interpretation or non-routine problem solving.

One Word Answer:
- Answer must be one word or one concise term.

Very Short Answer:
- Must require a concise response.

Short Answer:
- Must require an explanation, calculation, comparison, derivation or reasoning
  appropriate to the assigned marks.

Long Answer:
- Must require a detailed explanation, derivation, multi-step calculation,
  analysis or structured response.

==================================================
PRESERVE VALID CONTENT
==================================================

Do not:

- Add questions.
- Remove questions.
- Add sections.
- Remove sections.
- Move questions between sections.
- Change valid marks.
- Change valid question types.
- Change valid section names.
- Change valid section order.
- Change the total marks.
- Change syllabus coverage unnecessarily.
- Introduce new duplicates.
- Introduce new similarity problems.
- Introduce new structural problems.

==================================================
FINAL SELF-CHECK
==================================================

Before returning the repaired paper, internally verify:

1. Correct number of sections.
2. Correct section order.
3. Correct section names.
4. Correct number of questions.
5. Correct question types.
6. Correct marks.
7. Correct section totals.
8. Correct total marks.
9. Exact cognitive distribution.
10. Exact difficulty distribution if required.
11. Correct special fields for each question type.
12. No duplicate questions.
13. No new validation errors.
14. Every answer is correct.
15. Every solution matches its answer.
16. Every question is syllabus relevant.
17. Every question genuinely matches its question type.
18. Every cognitive label genuinely matches the question.
19. Every difficulty label genuinely matches the question.

If a validation error was reported, it MUST be fixed before returning.

Return the COMPLETE repaired examination paper.

Return ONLY valid JSON.

==================================================
ADDITIONAL REGENERATION RULES
==================================================

{rules}
"""

    return prompt