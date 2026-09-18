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
    left_column = question.get("left_column")
    right_column = question.get("right_column")

    if not isinstance(left_column, list):
        errors.append(f"Question {index}: Match-the-Following left_column must be a list.")

    if not isinstance(right_column, list):
        errors.append(f"Question {index}: Match-the-Following right_column must be a list.")

    if isinstance(left_column, list) and isinstance(right_column, list):
        if not left_column:
            errors.append(f"Question {index}: Match-the-Following left column is empty.")
        if not right_column:
            errors.append(f"Question {index}: Match-the-Following right column is empty.")

        if len(left_column) != len(right_column):
            errors.append(
                f"Question {index}: Match-the-Following left and right columns must have the same number of items."
            )

    answer = question.get("answer")
    if not _clean(answer):
        errors.append(f"Question {index}: Match-the-Following answer is missing.")

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
        "left_column": question.get("left_column"),
        "right_column": question.get("right_column"),
        "answer": question.get("answer"),
        "solution": question.get("solution"),
        "explanation": question.get("explanation")
    }


def _ai_validate_questions(questions: list[dict], exam_type: str, subject: str, class_name: str = "") -> list[str]:
    if not questions:
        return []

    payload = {
        "exam_type": exam_type,
        "subject": subject,
        "class_name": class_name,
        "questions": [
            _build_ai_question(question, index)
            for index, question in enumerate(questions, start=1)
        ]
    }

    prompt = f"""
You are a strict exam-question correctness verifier.

Verify every question independently and mathematically/logically.

For each question check:

1. Whether the question itself is factually correct.
2. Whether the supplied answer is objectively correct.
3. For MCQs, whether the answer letter maps to the correct option.
4. Whether distractor options are valid and not accidentally correct.
5. Whether the question is ambiguous or has multiple genuinely plausible answers.
6. Whether the solution/explanation agrees with the supplied answer.
7. Whether all numerical calculations are correct.
8. Whether True/False answers are correct.
9. Whether Fill-in-the-Blank answers correctly answer the blank.
10. Whether Assertion-Reason answers correctly represent the relationship.
11. Whether Match-the-Following answers are internally consistent.
12. Whether the question contains a serious factual, logical, or mathematical error.
13. Whether the question meets the academic quality expected for the requested class.
14. Whether the question is too trivial for the requested class, subject, difficulty and marks.

ACADEMIC QUALITY FLOOR:

- Generate and verify questions at the level expected for the requested class, not at elementary-school level.
- For Class 10 and above, reject toy questions such as single-step arithmetic like 7 + 5, counting, direct substitution with no meaningful concept, or similarly trivial tasks when they do not test a syllabus concept.
- A question may be Easy, but Easy does NOT mean childish or content-free.
- Easy questions should still test a meaningful syllabus concept appropriate to the class.
- Medium questions should require genuine understanding or application.
- Hard questions should require substantial reasoning, interpretation, multi-step work, or analysis where appropriate.
- Do not judge quality by wording length alone. Judge the cognitive demand and syllabus relevance.
- Do not reject a legitimate foundational syllabus question merely because it is easy.
- For One Word Answer and True/False, concise recall may be appropriate, but it must still be syllabus-relevant and class-appropriate.
- Flag a question only when it clearly falls below the expected academic level, is trivial relative to the requested class/difficulty/marks, or is essentially a toy exercise.

IMPORTANT ANSWER-CONSISTENCY RULES:

- You MUST independently determine the correct answer before deciding whether the supplied answer is correct.
- If the supplied answer and your calculated/correct answer are the same, answer_correct MUST be true.
- Never mark an answer incorrect when your own stated correct answer is identical to the supplied answer.
- Never describe an answer as incorrect using wording such as "not X" when the supplied answer is also X.
- If your reasoning contradicts your answer_correct flag, resolve the contradiction before returning the result.
- Do not invent a difference between two numerically or factually identical answers.
- For numerical questions, perform the calculation explicitly before judging the answer.
- For MCQs, identify the actual option text corresponding to the supplied answer letter before judging it.
- If the answer is correct but the explanation contains a minor wording issue, do not mark answer_correct as false.
- Only mark ambiguous=true when there are genuinely multiple plausible correct answers.
- Do not reject a question merely because its wording could be stylistically improved.

Return ONLY valid JSON in this exact format:

{{
  "results": [
    {{
      "index": 1,
      "correct": true,
      "ambiguous": false,
      "answer_correct": true,
      "solution_consistent": true,
      "quality_ok": true,
      "correct_answer": "",
      "reason": ""
    }}
  ]
}}

For every question:
- "correct" means the question and its content are objectively valid.
- "answer_correct" means the supplied answer is actually correct.
- "solution_consistent" means the supplied solution/explanation agrees with the supplied answer.
- "quality_ok" means the question meets the academic quality floor for the requested class, subject, difficulty and marks.
- "correct_answer" must contain the answer you independently determined to be correct. For MCQ use A/B/C/D. For Assertion-Reason use A/B/C/D. For Match-the-Following use the complete mapping such as "1-A, 2-B, 3-D, 4-C". For other questions use the actual correct answer/value.
- "reason" must contain a concrete explanation ONLY when one of these checks fails.
- If all checks pass, use an empty string for "reason".
- If all checks pass, use an empty string for "reason".

Exam type:
{exam_type}

Subject:
{subject}

Class:
{class_name}

Questions:
{json.dumps(payload, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a strict exam correctness verifier. Perform calculations carefully and return JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=1,
        timeout=60
    )

    content = response.choices[0].message.content
    data = json.loads(content)
    results = data.get("results", [])

    errors = []

    question_map = {
        index: question
        for index, question in enumerate(questions, start=1)
    }

    returned_indexes = set()

    for result in results:
        index = result.get("index")
        if not isinstance(index, int) or index not in question_map:
            continue

        returned_indexes.add(index)
        question = question_map[index]
        supplied_answer = _clean(question.get("answer"))
        question_type = _clean(question.get("question_type")).lower()
        correct_answer = _clean(result.get("correct_answer"))
        reason = _clean(result.get("reason"))

        answer_correct = result.get("answer_correct", True)
        if isinstance(answer_correct, str):
            answer_correct = answer_correct.strip().lower() == "true"

        if correct_answer and question_type in {"mcq", "assertion-reason", "assertion & reason", "assertion and reason"}:
            if correct_answer.upper() == supplied_answer.upper():
                answer_correct = True

        if correct_answer and question_type in {"match the following", "match-the-following", "match_the_following"}:
            supplied_map = _normalize(supplied_answer).replace(" ", "")
            correct_map = _normalize(correct_answer).replace(" ", "")
            if supplied_map == correct_map:
                answer_correct = True

        if not result.get("correct", True):
            errors.append(
                f"Question {index}: {reason or 'Question is not correct.'}"
            )

        if result.get("ambiguous", False):
            errors.append(
                f"Question {index}: {reason or 'Question is ambiguous.'}"
            )

        if not answer_correct:
            errors.append(
                f"Question {index}: supplied answer is incorrect. "
                f"{reason or 'The supplied answer does not match the independently determined correct answer.'}"
            )

        if not result.get("solution_consistent", True):
            errors.append(
                f"Question {index}: solution/explanation is inconsistent with the answer. "
                f"{reason or 'The explanation does not support the supplied answer.'}"
            )

        if not result.get("quality_ok", True):
            errors.append(
                f"Question {index}: question quality is below the expected academic level. "
                f"{reason or 'The question is too trivial for the requested class, difficulty or marks.'}"
            )

    missing_indexes = set(question_map) - returned_indexes
    for index in sorted(missing_indexes):
        errors.append(
            f"Question {index}: correctness verifier did not return a result."
        )

    return errors

def validate_question_correctness(
    generated_paper: dict,
    exam_type: str = "",
    subject: str = "",
    teacher_data: Any = None
) -> dict:

    questions = _get_questions(generated_paper)

    if isinstance(teacher_data, dict):
        class_name = _clean(teacher_data.get("class_name") or teacher_data.get("class"))
    else:
        class_name = _clean(getattr(teacher_data, "class_name", "") or getattr(teacher_data, "class", ""))

    if not questions:
        return {
            "valid": False,
            "errors": [
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
            subject,
            class_name
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