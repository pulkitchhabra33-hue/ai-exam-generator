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

SOFT_CATEGORIES = {
    "style",
    "formatting",
    "grammar",
    "explanation",
    "context",
    "wording",
    "difficulty",
    "cognitive"
}

SOFT_MESSAGE_PATTERNS = [
    r"\bmarkdown\b",
    r"\bformat(?:ting)?\b",
    r"\blacks context\b",
    r"\bmore explanation\b",
    r"\bneeds explanation\b",
    r"\bneeds more detail\b",
    r"\bshould explain\b",
    r"\bbrief(?:ly)? stated\b",
    r"\btoo brief\b",
    r"\bwording\b",
    r"\bstyle\b",
    r"\bgrammar\b",
    r"\bawkward\b",
    r"\bclarity\b"
]

def flatten_questions(paper):
    questions = []
    number = 1

    for section in paper.get(
        "sections",
        []
    ):
        for question in section.get(
            "questions",
            []
        ):
            questions.append(
                (
                    number,
                    section,
                    question
                )
            )
            number += 1

    return questions

def normalize_audit_result(result):
    if not isinstance(result, dict):
        return {
            "valid": False,
            "errors": [
                "Quality audit returned invalid data."
            ],
            "warnings": [],
            "issues": []
        }

    result.setdefault(
        "valid",
        True
    )
    result.setdefault(
        "errors",
        []
    )
    result.setdefault(
        "warnings",
        []
    )
    result.setdefault(
        "issues",
        []
    )

    hard_issues = []
    soft_issues = []

    for issue in result.get(
        "issues",
        []
    ):
        if not isinstance(
            issue,
            dict
        ):
            continue

        category = str(
            issue.get(
                "category",
                ""
            )
        ).strip().lower()

        message = str(
            issue.get(
                "message",
                ""
            )
        ).strip()

        is_soft = (
            category in SOFT_CATEGORIES
        )

        if not is_soft:
            for pattern in SOFT_MESSAGE_PATTERNS:
                if re.search(
                    pattern,
                    message,
                    re.IGNORECASE
                ):
                    is_soft = True
                    break

        if is_soft:
            soft_issues.append(issue)
        else:
            hard_issues.append(issue)

    result["issues"] = (
        hard_issues +
        soft_issues
    )

    result["errors"] = [
        issue.get(
            "message",
            ""
        )
        for issue in hard_issues
        if issue.get(
            "message"
        )
    ]

    result["warnings"] = [
        issue.get(
            "message",
            ""
        )
        for issue in soft_issues
        if issue.get(
            "message"
        )
    ]

    result["valid"] = (
        len(hard_issues) == 0
    )

    return result

def audit_paper(
        paper,
        teacher_data
):
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
13. Marks appropriateness.
14. Question-type authenticity.
15. Clear, unambiguous and grammatically sound wording.

HARD ERRORS:

Only report a HARD error when the problem is objectively significant and would make the question or answer academically unreliable.

Examples:

- The answer is factually wrong.
- A numerical calculation is wrong.
- The answer contradicts the actual question.
- The answer contradicts the solution.
- The MCQ answer letter points to the wrong option.
- The True/False answer is wrong.
- The Assertion-Reason relationship is wrong.
- The Match-the-Following mapping is wrong.
- A required answer is missing.
- A required solution is missing.
- The question is clearly unrelated to the requested subject.
- The question is clearly inappropriate for the requested class.
- The question is clearly inappropriate for its marks.
- The question is genuinely ambiguous or malformed.
- A Source-Based question cannot be answered from its supplied source.
- A Case Study question cannot be answered from its supplied case.

IMPORTANT:

Do NOT classify an issue as HARD merely because:

- The answer is brief.
- The answer could contain more explanation.
- The solution could contain more steps even though the answer is correct.
- The answer uses Markdown or formatting.
- The wording could be improved.
- The response lacks additional context but still answers the question correctly.
- The style is not ideal.
- The question could be phrased more elegantly.
- The question has a minor grammar issue.
- Difficulty distribution is imperfect.
- Cognitive distribution is imperfect.

For answer_correctness, mark HARD only when the actual answer is demonstrably incorrect.

For mathematical or numerical questions, verify the calculation carefully before reporting a HARD error.

If an answer is correct but could be explained better, report it as a WARNING.

If formatting is the only problem, report it as a WARNING.

If wording or explanation is the only problem, report it as a WARNING.

Do not invent an error merely because another answer style would be preferable.

Return ONLY JSON:

{{
  "valid": true,
  "errors": [],
  "warnings": [],
  "issues": []
}}

For every HARD issue, use:

{{
  "question_number": 1,
  "category": "answer_correctness",
  "message": "Exact objective problem"
}}

For every WARNING, use:

{{
  "question_number": 1,
  "category": "style",
  "message": "Minor issue that does not make the question academically invalid"
}}

If there are no HARD issues, valid MUST be true.

If there are only warnings, valid MUST be true.

PAPER:
{payload}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=60.0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        result = json.loads(
            content
        )

        return normalize_audit_result(
            result
        )

    except Exception as error:
        logger.exception(
            "Content quality audit failed."
        )

        return {
            "valid": False,
            "errors": [
                f"Content quality audit failed: {error}"
            ],
            "warnings": [],
            "issues": []
        }

def repair_paper(
        paper,
        teacher_data,
        audit_report
):
    issues = audit_report.get(
        "issues",
        []
    )

    hard_issues = []

    for issue in issues:
        if not isinstance(
            issue,
            dict
        ):
            continue

        category = str(
            issue.get(
                "category",
                ""
            )
        ).strip().lower()

        message = str(
            issue.get(
                "message",
                ""
            )
        ).strip()

        is_soft = (
            category in SOFT_CATEGORIES
        )

        if not is_soft:
            for pattern in SOFT_MESSAGE_PATTERNS:
                if re.search(
                    pattern,
                    message,
                    re.IGNORECASE
                ):
                    is_soft = True
                    break

        if not is_soft:
            hard_issues.append(
                issue
            )

    if not hard_issues:
        return paper

    question_map = {
        number: question
        for number, _, question in flatten_questions(
            paper
        )
    }

    selected = []

    for issue in hard_issues:
        number = issue.get(
            "question_number"
        )

        if number in question_map:
            selected.append(
                {
                    "question_number": number,
                    "problem": issue.get(
                        "message",
                        ""
                    )
                }
            )

    if not selected:
        return paper

    selected_json = json.dumps(
        selected,
        ensure_ascii=False,
        indent=2
    )

    selected_numbers = {
        item["question_number"]
        for item in selected
    }

    questions_json = json.dumps(
        [
            {
                "question_number": number,
                "question": question
            }
            for number, _, question
            in flatten_questions(
                paper
            )
            if number in selected_numbers
        ],
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are repairing specific HARD academic-quality problems in an examination paper.

Teacher requirements:
- Exam type: {teacher_data.get('exam_type')}
- Subject: {teacher_data.get('subject')}
- Class: {teacher_data.get('class_name')}

Only repair the listed HARD issues.

Preserve:

- Section
- Question type
- Marks
- Difficulty intent
- Cognitive intent
- Question count
- Question numbering

unless changing the question text is necessary to correct the reported HARD problem.

Do not add questions.

Do not remove questions.

Do not change question numbers.

Do not introduce a new question type.

Do not create Diagram-Based Questions.

Do not make stylistic changes unless they are necessary for the reported HARD problem.

Every repaired answer must be objectively correct.

Every repaired solution must agree with the repaired answer.

Every repaired question must remain appropriate for the requested subject, class and marks.

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

REPORTED HARD PROBLEMS:
{selected_json}

QUESTIONS TO REPAIR:
{questions_json}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            timeout=60.0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = json.loads(
            response
            .choices[0]
            .message
            .content
        )

    except Exception as error:
        logger.exception(
            "Content quality repair failed."
        )
        return paper

    repairs = result.get(
        "repairs",
        []
    )

    for repair in repairs:
        number = repair.get(
            "question_number"
        )

        question = question_map.get(
            number
        )

        changes = repair.get(
            "changes",
            {}
        )

        if (
            not question
            or not isinstance(
                changes,
                dict
            )
        ):
            continue

        for key, value in changes.items():
            if key in ALLOWED_REPAIR_FIELDS:
                question[key] = value

    return paper

def validate_and_repair_paper(
        paper,
        teacher_data
):
    audit = audit_paper(
        paper,
        teacher_data
    )

    if audit.get(
        "valid"
    ):
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

    return (
        repaired_paper,
        final_audit
    )