import json
import re
from typing import Any
from backend.core.ai_client import client

OPTION_KEYS = ("A", "B", "C", "D")

ASSERTION_REASON_OPTIONS = [
    "Both Assertion (A) and Reason (R) are true and Reason (R) is the correct explanation of the Assertion (A).",
    "Both Assertion (A) and Reason (R) are true, but Reason (R) is not the correct explanation of the Assertion (A).",
    "Assertion (A) is true, but Reason (R) is false.",
    "Assertion (A) is false, but Reason (R) is true."
]


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", _clean(value)).strip().lower()


def _get_questions(generated_paper: dict) -> list[dict]:
    questions = []

    for section in generated_paper.get("sections", []):
        for question in section.get("questions", []):
            if isinstance(question, dict):
                questions.append(question)

    return questions


def _validate_required_fields(question: dict, index: int) -> list[str]:
    errors = []

    question_text = _clean(question.get("question"))

    if not question_text:
        errors.append(
            f"Question {index}: question text is missing."
        )

    answer = _clean(question.get("answer"))

    if not answer:
        errors.append(
            f"Question {index}: answer is missing."
        )

    return errors


def _validate_mcq(question: dict, index: int) -> list[str]:
    errors = []

    options = question.get("options")

    if not isinstance(options, list):
        errors.append(
            f"Question {index}: MCQ options must be a list."
        )
        return errors

    if len(options) != 4:
        errors.append(
            f"Question {index}: MCQ must contain exactly 4 options."
        )
        return errors

    for option in options:
        if not _clean(option):
            errors.append(
                f"Question {index}: MCQ contains an empty option."
            )

    normalized_options = [_normalize(option) for option in options]

    if len(set(normalized_options)) != 4:
        errors.append(
            f"Question {index}: MCQ contains duplicate options."
        )

    answer = _clean(question.get("answer")).upper()

    if answer not in OPTION_KEYS:
        errors.append(
            f"Question {index}: MCQ answer must be A, B, C or D."
        )
        return errors

    answer_index = OPTION_KEYS.index(answer)

    if not _clean(options[answer_index]):
        errors.append(
            f"Question {index}: MCQ answer points to an empty option."
        )

    return errors


def _validate_true_false(question: dict, index: int) -> list[str]:
    errors = []

    answer = _normalize(question.get("answer"))

    valid_answers = {
        "true",
        "false",
        "t",
        "f"
    }

    if answer not in valid_answers:
        errors.append(
            f"Question {index}: True/False answer must be True or False."
        )

    return errors


def _validate_fill_blank(question: dict, index: int) -> list[str]:
    errors = []

    question_text = _clean(question.get("question"))
    answer = _clean(question.get("answer"))

    if not answer:
        errors.append(
            f"Question {index}: Fill-in-the-Blank answer is missing."
        )

    has_blank = (
        "___" in question_text
        or "____" in question_text
        or "_____" in question_text
        or "[blank]" in question_text.lower()
        or "[answer]" in question_text.lower()
    )

    if not has_blank:
        errors.append(
            f"Question {index}: Fill-in-the-Blank question has no blank marker."
        )

    return errors


def _validate_assertion_reason(question: dict, index: int) -> list[str]:
    errors = []

    assertion = _clean(question.get("assertion"))
    reason = _clean(question.get("reason"))
    options = question.get("options")
    answer = _clean(question.get("answer")).upper()

    if not assertion:
        errors.append(
            f"Question {index}: Assertion is missing."
        )

    if not reason:
        errors.append(
            f"Question {index}: Reason is missing."
        )

    if not isinstance(options, list):
        errors.append(
            f"Question {index}: Assertion-Reason options must be a list."
        )
    elif options != ASSERTION_REASON_OPTIONS:
        errors.append(
            f"Question {index}: Assertion-Reason options are invalid."
        )

    if answer not in OPTION_KEYS:
        errors.append(
            f"Question {index}: Assertion-Reason answer must be A, B, C or D."
        )

    return errors


def _validate_match_following(question: dict, index: int) -> list[str]:
    errors = []

    column_a = question.get("column_a")
    column_b = question.get("column_b")

    if not isinstance(column_a, list):
        errors.append(
            f"Question {index}: Match-the-Following column_a must be a list."
        )

    if not isinstance(column_b, list):
        errors.append(
            f"Question {index}: Match-the-Following column_b must be a list."
        )

    if isinstance(column_a, list) and isinstance(column_b, list):
        if not column_a:
            errors.append(
                f"Question {index}: Match-the-Following column A is empty."
            )

        if not column_b:
            errors.append(
                f"Question {index}: Match-the-Following column B is empty."
            )

    answer = question.get("answer")

    if not _clean(answer):
        errors.append(
            f"Question {index}: Match-the-Following answer is missing."
        )

    return errors


def _validate_answer_option_mapping(question: dict, index: int) -> list[str]:
    errors = []

    options = question.get("options")
    answer = _clean(question.get("answer")).upper()

    if not isinstance(options, list):
        return errors

    if answer in OPTION_KEYS and len(options) == 4:
        selected_option = options[OPTION_KEYS.index(answer)]

        if not _clean(selected_option):
            errors.append(
                f"Question {index}: answer points to an empty option."
            )

    return errors


def _deterministic_validation(question: dict, index: int) -> list[str]:
    errors = []

    errors.extend(
        _validate_required_fields(question, index)
    )

    question_type = _clean(
        question.get("question_type")
    ).lower()

    if question_type == "mcq":
        errors.extend(
            _validate_mcq(question, index)
        )

    elif question_type in {
        "true/false",
        "true false",
        "true_false"
    }:
        errors.extend(
            _validate_true_false(question, index)
        )

    elif question_type in {
        "fill in the blanks",
        "fill-in-the-blank",
        "fill in the blank",
        "fill_in_the_blank"
    }:
        errors.extend(
            _validate_fill_blank(question, index)
        )

    elif question_type in {
        "assertion-reason",
        "assertion & reason",
        "assertion and reason"
    }:
        errors.extend(
            _validate_assertion_reason(question, index)
        )

    elif question_type in {
        "match the following",
        "match-the-following",
        "match_the_following"
    }:
        errors.extend(
            _validate_match_following(question, index)
        )

    errors.extend(
        _validate_answer_option_mapping(question, index)
    )

    return errors


def _build_ai_question(question: dict, index: int) -> dict:
    return {
        "index": index,
        "question_type": question.get("question_type"),
        "question": question.get("question"),
        "options": question.get("options"),
        "assertion": question.get("assertion"),
        "reason": question.get("reason"),
        "column_a": question.get("column_a"),
        "column_b": question.get("column_b"),
        "answer": question.get("answer"),
        "solution": question.get("solution"),
        "explanation": question.get("explanation")
    }


def _ai_validate_questions(
    questions: list[dict],
    exam_type: str,
    subject: str
) -> list[str]:

    if not questions:
        return []

    payload = {
        "exam_type": exam_type,
        "subject": subject,
        "questions": [
            _build_ai_question(question, index)
            for index, question in enumerate(questions, start=1)
        ]
    }

    prompt = f"""
You are a strict exam-question correctness verifier.

Verify each question independently.

Check:

1. Whether the question is factually correct.
2. Whether the supplied answer is actually correct.
3. For MCQs, whether the selected answer letter maps to the correct option.
4. Whether distractor options are logically valid and not accidentally correct.
5. Whether the question is ambiguous or has multiple plausible answers.
6. Whether the solution/explanation agrees with the answer.
7. Whether numerical calculations are correct.
8. Whether True/False answers are correct.
9. Whether Fill-in-the-Blank answers correctly answer the blank.
10. Whether Assertion-Reason answers correctly represent the relationship.
11. Whether Match-the-Following answers are internally consistent.
12. Whether the question contains a serious factual, logical or mathematical error.

Do not reject a question merely because its wording could be stylistically improved.

Return ONLY valid JSON in this exact format:

{{
  "results": [
    {{
      "index": 1,
      "correct": true,
      "ambiguous": false,
      "answer_correct": true,
      "solution_consistent": true,
      "reason": ""
    }}
  ]
}}

If a question has a correctness problem, explain the concrete problem in "reason".

Exam type:
{exam_type}

Subject:
{subject}

Questions:
{json.dumps(payload, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a strict exam correctness verifier. Return JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
        timeout=60
    )

    content = response.choices[0].message.content

    data = json.loads(content)

    results = data.get("results", [])

    errors = []

    for result in results:
        index = result.get("index")

        if not result.get("correct", True):
            errors.append(
                f"Question {index}: {result.get('reason', 'Question is not correct.')}"
            )

        if result.get("ambiguous", False):
            errors.append(
                f"Question {index}: {result.get('reason', 'Question is ambiguous.')}"
            )

        if not result.get("answer_correct", True):
            errors.append(
                f"Question {index}: supplied answer is incorrect. {result.get('reason', '')}".strip()
            )

        if not result.get("solution_consistent", True):
            errors.append(
                f"Question {index}: solution/explanation is inconsistent with the answer. {result.get('reason', '')}".strip()
            )

    return errors


def validate_question_correctness(
    generated_paper: dict,
    exam_type: str = "",
    subject: str = ""
) -> dict:

    questions = _get_questions(generated_paper)

    if not questions:
        return {
            "valid": False,
            "error": [
                "Question correctness validator: no questions found."
            ],
            "warnings": []
        }

    errors = []

    for index, question in enumerate(questions, start=1):
        if index in (21, 22):
            print(
                f"[CORRECTNESS DEBUG] Question {index}: "
                f"{json.dumps(question, ensure_ascii=False)}",
                flush=True
            )
        errors.extend(
            _deterministic_validation(question, index)
        )
    try:
        ai_errors = _ai_validate_questions(
            questions,
            exam_type,
            subject
        )
        errors.extend(ai_errors)

    except Exception as error:
        return {
            "valid": False,
            "errors": [
                f"Question correctness AI validation failed: {error}"
            ],
            "warnings": []
        }
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": []
    }