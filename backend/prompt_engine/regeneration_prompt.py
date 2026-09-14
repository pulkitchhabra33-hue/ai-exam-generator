from backend.prompt_engine.regeneration_rules import get_regeneration_rules
import json
import re
from collections import Counter


def get_cognitive_counts(generated_paper):
    counts = Counter()

    for section in generated_paper.get(
        "sections",
        []
    ):
        for question in section.get(
            "questions",
            []
        ):
            cognitive = question.get(
                "cognitive"
            )

            if cognitive:
                counts[cognitive] += 1

    return counts


def get_difficulty_counts(generated_paper):
    counts = Counter()

    for section in generated_paper.get(
        "sections",
        []
    ):
        for question in section.get(
            "questions",
            []
        ):
            difficulty = question.get(
                "difficulty"
            )

            if difficulty:
                counts[difficulty] += 1

    return counts


def extract_distribution_targets(
        feedback,
        label
):

    targets = {}

    pattern = re.compile(
        rf"{re.escape(label)}\s+'?([^']+?)'?\s+mismatch:\s+"
        r"expected\s+(\d+)\s+questions?,\s+got\s+(\d+)",
        re.IGNORECASE
    )

    for item in feedback:

        match = pattern.search(
            str(item)
        )

        if match:

            level = match.group(1).strip()

            expected = int(
                match.group(2)
            )

            actual = int(
                match.group(3)
            )

            targets[level] = {
                "expected": expected,
                "actual": actual
            }

    return targets


def build_transfer_plan(
        feedback,
        generated_paper
):

    cognitive_targets = extract_distribution_targets(
        feedback,
        "Cognitive"
    )

    if not cognitive_targets:
        return ""

    current_counts = get_cognitive_counts(
        generated_paper
    )

    deficits = []
    surpluses = []

    for level, data in cognitive_targets.items():

        expected = data["expected"]

        actual = current_counts.get(
            level,
            data["actual"]
        )

        difference = expected - actual

        if difference > 0:

            deficits.append(
                (level, difference)
            )

        elif difference < 0:

            surpluses.append(
                (level, -difference)
            )

    transfers = []

    for source_level, source_amount in surpluses:

        remaining_source = source_amount

        for index, (
            target_level,
            target_amount
        ) in enumerate(deficits):

            if remaining_source <= 0:
                break

            if target_amount <= 0:
                continue

            amount = min(
                remaining_source,
                target_amount
            )

            transfers.append(
                f"- Change exactly {amount} "
                f"question(s) from {source_level} "
                f"to {target_level}."
            )

            remaining_source -= amount

            deficits[index] = (
                target_level,
                target_amount - amount
            )

    if not transfers:
        return ""

    return "\n".join(
        transfers
    )


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

    cognitive_counts = get_cognitive_counts(
        generated_paper
    )

    difficulty_counts = get_difficulty_counts(
        generated_paper
    )

    cognitive_targets = extract_distribution_targets(
        feedback,
        "Cognitive"
    )

    difficulty_targets = extract_distribution_targets(
        feedback,
        "Difficulty"
    )

    cognitive_current_text = "\n".join(
        f"- {level}: {count}"
        for level, count in sorted(
            cognitive_counts.items()
        )
    )

    difficulty_current_text = "\n".join(
        f"- {level}: {count}"
        for level, count in sorted(
            difficulty_counts.items()
        )
    )

    cognitive_target_text = "\n".join(
        f"- {level}: exactly {data['expected']}"
        for level, data in cognitive_targets.items()
    )

    difficulty_target_text = "\n".join(
        f"- {level}: exactly {data['expected']}"
        for level, data in difficulty_targets.items()
    )

    transfer_plan = build_transfer_plan(
        feedback,
        generated_paper
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

If multiple validation errors are present, repair the existing paper in place.

When there are two or more validation errors, identify the smallest possible set of existing questions that can fix all reported errors and modify only those questions.

Do not replace the complete examination paper when targeted repair is possible.

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
EXACT COGNITIVE REPAIR
==================================================

The cognitive distribution is validated across the COMPLETE examination paper.

The validator allows a maximum difference of one question from the calculated target.

Current cognitive counts:

{cognitive_current_text}

Required cognitive counts for the levels reported by validation:

{cognitive_target_text}

Use the validation targets as the source of truth when a cognitive mismatch is explicitly reported.

A difference of one question is acceptable and does not require repair.

DO NOT guess the target counts.

DO NOT use different target counts.

DO NOT change cognitive labels merely to manipulate the numbers.

The actual question must genuinely match its cognitive level.

EXACT REPAIR PLAN:

{transfer_plan if transfer_plan else "- Follow the exact cognitive mismatches in the validation feedback and make the smallest genuine corrections required."}

When changing a question's cognitive level:

- Keep its section unchanged.
- Keep its question type unchanged.
- Keep its marks unchanged.
- Keep its syllabus/topic relevance.
- Preserve its answer correctness.
- Preserve or rewrite its solution so it matches the revised question.
- Make the question genuinely appropriate for the new cognitive level.
- Do not change any other question's cognitive level unless required to satisfy
  the exact reported distribution.

After making the repair, count ALL questions again.

The final cognitive counts must be within the validator's allowed one-question tolerance.

==================================================
EXACT DIFFICULTY REPAIR
==================================================

Current difficulty counts:

{difficulty_current_text}

{difficulty_target_text if difficulty_target_text else "No difficulty-count repair is required unless explicitly reported in the validation feedback."}

If difficulty validation errors are reported:

- Use the exact expected counts from validation.
- Make the smallest genuine corrections.
- Keep section, question type and marks unchanged.
- Do not merely change the difficulty label.
- The question must genuinely match the assigned difficulty.
- Recalculate the complete-paper counts before returning.

==================================================
QUESTION TYPE RULES
==================================================

MCQ:

- Exactly 4 options.
- Only one correct option.
- Answer must be A, B, C or D.
- All options must be meaningful and plausible.

True/False:

- One clear factual statement.
- Answer must be True or False.

Fill in the Blanks:

- Question must contain ______.
- Answer must be the missing word, value, term or expression.

Assertion-Reason:

- assertion and reason must be separate fields.
- They must be logically related.
- Answer must correctly describe their relationship.

Match the Following:

- left_column and right_column must exist.
- Both must be non-empty.
- Both must have equal length.
- Answer must specify the correct matches.

Source-Based Questions:

- source must exist.
- The question must genuinely depend on the source.

Diagram-Based Questions:

- diagram must exist.
- The question must genuinely depend on the diagram.

Case Study:

- case must exist.
- The question must genuinely depend on the case.

Application-based:

- Must require genuine application of a concept, formula, principle or method
  to a new situation.
- Must not be simple recall.

HOTS:

- Must require genuine higher-order reasoning, analysis, evaluation,
  interpretation or non-routine problem solving.

One Word Answer:

- Answer must be one word or one concise term.

Very Short Answer:

- Must require a concise response appropriate to its marks.

Short Answer:

- Must require explanation, calculation, comparison, derivation or reasoning
  appropriate to its marks.

Long Answer:

- Must require detailed explanation, derivation, multi-step calculation,
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
- Introduce duplicates.
- Introduce similarity problems.
- Introduce structural problems.

==================================================
QUALITY REQUIREMENTS
==================================================

For every question that is modified:

- It must remain factually correct.
- It must remain grammatically correct.
- It must remain clear and unambiguous.
- It must remain appropriate for the subject and class.
- It must remain syllabus relevant.
- The answer must be correct.
- The solution must match the answer.
- The question type must remain genuine.
- The difficulty must genuinely match.
- The cognitive level must genuinely match.
- Do not sacrifice academic quality merely to satisfy a numerical distribution.

==================================================
FINAL SELF-CHECK
==================================================

Before returning the repaired paper, internally verify:

1. Correct number of sections.
2. Correct section order.
3. Correct section names.
4. Correct number of questions.
5. Correct question grouping.
6. Correct question types.
7. Correct marks.
8. Correct section totals.
9. Correct total marks.
10. Cognitive distribution within the allowed one-question tolerance.
11. Difficulty distribution within the allowed one-question tolerance if required.
12. Correct special fields for every question type.
13. No duplicate questions.
14. No new similarity problems.
15. No structural problems.
16. Every answer is correct.
17. Every solution matches its answer.
18. Every question is syllabus relevant.
19. Every question genuinely matches its question type.
20. Every cognitive level genuinely matches its question.
21. Every difficulty level genuinely matches its question.

If a validation error was reported, it MUST be fixed before returning.

Do not return a candidate with the same or a greater number of validation errors than the input paper.

Preserve unaffected questions exactly whenever possible.

Return the COMPLETE repaired examination paper.

Return ONLY valid JSON.

==================================================
ADDITIONAL REGENERATION RULES
==================================================

{rules}
"""

    return prompt