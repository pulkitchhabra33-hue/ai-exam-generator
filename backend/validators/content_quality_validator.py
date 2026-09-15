import json
import re
from backend.core.ai_client import client
from backend.utils.logger import logger

ALLOWED_REPAIR_FIELDS = {
    "question",
    "options",
    "assertion",
    "reason",
    "left_column",
    "right_column",
    "source",
    "case",
    "answer",
    "solution",
    "difficulty",
    "cognitive"
}


def flatten_questions(paper):
    questions = []
    number = 1
    for section in paper.get("sections", []):
        for question in section.get("questions", []):
            questions.append((number, section, question))
            number += 1
    return questions


def audit_paper(paper, teacher_data):
    payload = json.dumps(
        paper,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are the final academic quality auditor for an AI exam paper.

Teacher requirements:
- Exam type: {teacher_data.get('exam_type')}
- Subject: {teacher_data.get('subject')}
- Class: {teacher_data.get('class_name')}
- Total marks: {teacher_data.get('total_marks')}

Audit the complete paper below.

You MUST verify every question for:
1. Correctness of the answer.
2. Answer and solution consistency.
3. Mathematical or logical calculations.
4. MCQ answer letter matching the actual correct option.
5. True/False correctness.
6. Fill-in-the-blank answer correctness.
7. Assertion-Reason relationship correctness.
8. Match-the-Following answer correctness.
9. Source-Based question genuinely depending on its source.
10. Case Study question genuinely depending on its case.
11. Subject relevance.
12. Class-level appropriateness.
13. Marks appropriateness. A question requiring substantial reasoning must not be treated as an appropriate one-mark question.
14. Question-type authenticity.
15. Clear, unambiguous and grammatically sound wording.

Treat these as HARD errors:
- Wrong answer.
- Answer contradicts solution.
- Incorrect calculation.
- Wrong MCQ option/answer mapping.
- Wrong True/False answer.
- Wrong Assertion-Reason relationship.
- Wrong Match-the-Following mapping.
- Subject irrelevance.
- Missing or insufficient source/case dependency.
- Question is clearly inappropriate for the class.
- Question is clearly inappropriate for its marks.
- Ambiguous or malformed question.

Treat minor style preferences as warnings only.
Do not report cognitive-distribution differences as errors.
Do not report difficulty-distribution differences as errors.

Return ONLY JSON:
{{
  "valid": true,
  "errors": [],
  "warnings": [],
  "issues": []
}}

For every hard issue, use this structure in issues:
{{
  "question_number": 1,
  "category": "answer_correctness",
  "message": "Exact problem"
}}

If there are no hard issues, valid must be true.

PAPER:
{payload}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=60.0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        if not isinstance(result, dict):
            return {
                "valid": False,
                "errors": ["Quality audit returned invalid data."],
                "warnings": [],
                "issues": []
            }
        result.setdefault("valid", False)
        result.setdefault("errors", [])
        result.setdefault("warnings", [])
        result.setdefault("issues", [])
        return result
    except Exception as error:
        logger.exception("Content quality audit failed.")
        return {
            "valid": False,
            "errors": [f"Content quality audit failed: {error}"],
            "warnings": [],
            "issues": []
        }


def repair_paper(paper, teacher_data, audit_report):
    issues = audit_report.get("issues", [])
    if not issues:
        return paper

    question_map = {
        number: question
        for number, _, question in flatten_questions(paper)
    }

    selected = []
    for issue in issues:
        number = issue.get("question_number")
        if number in question_map:
            selected.append({
                "question_number": number,
                "problem": issue.get("message", "")
            })

    if not selected:
        return paper

    selected_json = json.dumps(
        selected,
        ensure_ascii=False,
        indent=2
    )

    questions_json = json.dumps(
        [
            {
                "question_number": number,
                "question": question
            }
            for number, _, question in flatten_questions(paper)
            if number in {item["question_number"] for item in selected}
        ],
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are repairing specific academic-quality problems in an examination paper.

Teacher requirements:
- Exam type: {teacher_data.get('exam_type')}
- Subject: {teacher_data.get('subject')}
- Class: {teacher_data.get('class_name')}

Only repair the listed questions.
Preserve section, question type, marks, difficulty intent and cognitive intent unless changing the question is necessary to fix the reported problem.
Do not add or remove questions.
Do not change question numbers.
Do not introduce a new question type.
Do not create Diagram-Based Questions.
Ensure every repaired answer is correct and every repaired solution agrees with the answer.
Ensure the repaired question remains appropriate for the requested subject, class and marks.

Return ONLY JSON:
{{
  "repairs": [
    {{
      "question_number": 1,
      "changes": {{
        "question": "...",
        "answer": "...",
        "solution": "..."
      }}
    }}
  ]
}}

Only use these change keys when needed:
{sorted(ALLOWED_REPAIR_FIELDS)}

REPORTED PROBLEMS:
{selected_json}

QUESTIONS TO REPAIR:
{questions_json}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=60.0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        result = json.loads(
            response.choices[0].message.content
        )
    except Exception as error:
        logger.exception("Content quality repair failed.")
        return paper

    repairs = result.get("repairs", [])

    for repair in repairs:
        number = repair.get("question_number")
        question = question_map.get(number)
        changes = repair.get("changes", {})

        if not question or not isinstance(changes, dict):
            continue

        for key, value in changes.items():
            if key in ALLOWED_REPAIR_FIELDS:
                question[key] = value

    return paper


def validate_and_repair_paper(paper, teacher_data):
    audit = audit_paper(
        paper,
        teacher_data
    )

    if audit.get("valid"):
        return paper, audit

    repaired_paper = repair_paper(
        paper,
        teacher_data,
        audit
    )

    final_audit = audit_paper(
        repaired_paper,
        teacher_data
    )

    return repaired_paper, final_audit
