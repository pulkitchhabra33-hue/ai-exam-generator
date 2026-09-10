import json
from backend.exam_patterns import get_exam_prompt, get_blueprint
from backend.exam_patterns.blueprints import get_cognitive_blueprint
from backend.services.question_allocator import allocate_questions
from backend.prompt_engine.prompt_builder import build_prompt
from backend.core.ai_client import client
from backend.utils.logger import logger
import tiktoken


def format_instructions(text):

    default_instruction = "Attempt all questions."

    if not text or not text.strip():
        return [default_instruction]

    lines = text.split("\n")
    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = line.replace("..", ".")

        line = (
            line[0].upper() + line[1:]
            if len(line) > 1
            else line.upper()
        )

        if not line.endswith((".", "?", "!")):
            line += "."

        cleaned.append(line)

    lower_cleaned = [x.lower() for x in cleaned]

    if "attempt all questions." not in lower_cleaned:
        cleaned.append(default_instruction)

    return cleaned


def instructions_to_text(instructions_list):
    return "\n".join(f"- {i}" for i in instructions_list)


json_format = """
Return ONLY valid JSON in this structure:

{
    "title": "Exam Paper Title",
    "sections": [
        {
            "section_name": "Section A",
            "questions": [
                {
                    "question": "Question text",
                    "question_type": "MCQ",
                    "marks": 1,
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "options": [
                        "Option 1",
                        "Option 2",
                        "Option 3",
                        "Option 4"
                    ],
                    "answer": "A",
                    "solution": "Explanation of the answer"
                }
            ]
        }
    ]
}

Question-type rules:

MCQ:
- Include exactly four options.
- The answer must identify one option using A, B, C, or D.
- Include question, question_type, marks, difficulty, cognitive, options, answer and solution.

True/False:
- Include question, question_type, marks, difficulty, cognitive, answer and solution.
- Do NOT include options.
- Answer must be "True" or "False".

Fill in the Blanks:
- Include the blank directly in the question using ______.
- Do NOT include MCQ options.
- Include question, question_type, marks, difficulty, cognitive, answer and solution.

Assertion-Reason:
- Include:
  "question": "Read the following Assertion and Reason.",
  "assertion": "...",
  "reason": "...",
  "question_type": "Assertion-Reason",
  "marks": 1,
  "difficulty": "Medium",
  "cognitive": "Understanding",
  "answer": "...",
  "solution": "..."
- Assertion and Reason must be separate fields.
- Do NOT put Assertion and Reason together in one field.

Match the Following:
- Include:
  "question": "...",
  "left_column": ["..."],
  "right_column": ["..."],
  "question_type": "Match the Following",
  "marks": 1,
  "difficulty": "Medium",
  "cognitive": "Understanding",
  "answer": "...",
  "solution": "..."
- left_column and right_column must both be non-empty.
- Both columns must contain the same number of items.
- Do NOT use MCQ options for Match the Following.

Source-Based:
- Include:
  "question": "...",
  "source": "...",
  "question_type": "Source-Based Questions",
  "marks": 1,
  "difficulty": "Medium",
  "cognitive": "Understanding",
  "answer": "...",
  "solution": "..."
- The source/passage must be meaningful and relevant to the question.

Diagram-Based:
- Include:
  "question": "...",
  "diagram": "...",
  "question_type": "Diagram-Based Questions",
  "marks": 1,
  "difficulty": "Medium",
  "cognitive": "Application",
  "answer": "...",
  "solution": "..."
- The diagram field must describe the required diagram clearly.

Case Study:
- Include:
  "question": "...",
  "case": "...",
  "question_type": "Case Study",
  "marks": 1,
  "difficulty": "Medium",
  "cognitive": "Application",
  "answer": "...",
  "solution": "..."
- The case must be meaningful and relevant to the questions.

General rules:

- Generate exactly the requested number of questions.
- Generate exactly the requested question type for each group.
- Preserve the order of the question groups.
- Do not merge different question types.
- Do not add extra questions.
- Every question must contain a non-empty "question" field.
- Every question must contain "question_type".
- Every question must contain "marks".
- Every question must contain "difficulty".
- Every question must contain "cognitive".
- Every question must contain "answer".
- Every question must contain "solution".
- difficulty must be exactly "Easy", "Medium", or "Hard".
- cognitive must be exactly "Recall", "Understanding", "Application", or "Analysis".
- Follow the requested difficulty distribution.
- Follow the requested cognitive distribution.
"""


def generate_paper(data, uploaded_content="", pattern_summary=""):

    logger.info("Received paper generation request.")

    exam_prompt = get_exam_prompt(data["exam_type"])
    exam_blueprint = get_blueprint(data["exam_type"])

    section_data = ""
    exam_type = data.get(
        "exam_type",
        "General Exam Paper"
    )

    if data.get("sections"):

        for index, section in enumerate(data["sections"]):

            section_name = (
                section.get("section_name")
                or f"Section {chr(65 + index)}"
            )

            total_marks = section["marks"]
            total_questions = section["question_count"]

            section_data += f"""
{section_name}:
Total Marks: {total_marks}
Total Questions: {total_questions}

QUESTION TYPE GROUPS:
"""

            for group in section.get("question_groups", []):

                question_type = group["question_type"]
                question_count = group["question_count"]
                marks_per_question = group["marks_per_question"]
                group_marks = group["marks"]

                allocation = allocate_questions(
                    exam_type,
                    question_count
                )

                logger.info(
                    f"{section_name} - {question_type} Allocation: {allocation}"
                )

                section_data += f"""
- Question Type: {question_type}
  Question Count: {question_count}
  Marks Per Question: {marks_per_question}
  Total Marks: {group_marks}

  COGNITIVE DISTRIBUTION:
  - Recall Questions: {allocation["recall"]}
  - Understanding Questions: {allocation["understanding"]}
  - Application Questions: {allocation["application"]}
  - Analysis Questions: {allocation["analysis"]}

  IMPORTANT:
  Generate EXACTLY {question_count} questions of type {question_type}.
  Each question must carry exactly {marks_per_question} marks.
"""

            section_data += f"""
IMPORTANT:
- Generate EXACTLY {total_questions} questions in {section_name}.
- Generate EXACTLY the specified question count for every question type group.
- Do NOT move questions between question type groups.
- Preserve the exact order of the question type groups.
"""

    else:

        section_data = "Use standard exam pattern"

    instructions_list = format_instructions(
        data.get("instructions", "")
    )

    instructions = instructions_to_text(
        instructions_list
    )

    cognitive_blueprint = get_cognitive_blueprint(
        exam_type
    )

    reference_paper = ""

    if pattern_summary.strip():

        reference_paper = f"""
REFERENCE PAPER ANALYSIS

{pattern_summary}

IMPORTANT:

Use this analysis to generate a NEW examination paper.

Follow:
- The same pattern
- Similar difficulty
- Similar structure
- Similar assessment style

Do NOT copy any question.

Create completely original questions.
"""

    prompt = build_prompt(
        data=data,
        exam_type=exam_type,
        section_data=section_data,
        instructions=instructions,
        reference_paper=reference_paper,
        json_format=json_format,
        cognitive_blueprint=cognitive_blueprint,
        exam_prompt=exam_prompt,
        exam_blueprint=exam_blueprint
    )

    encoding = tiktoken.get_encoding(
        "cl100k_base"
    )

    prompt_tokens = len(
        encoding.encode(prompt)
    )

    logger.info(
        f"PROMPT TOKENS: {prompt_tokens}"
    )

    logger.info(
        f"REFERENCE PAPER LENGTH: {len(reference_paper)}"
    )

    print(
        "[GEN] Calling OpenAI now",
        flush=True
    )

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

    except Exception as e:

        logger.exception(
            "Generation OpenAI API call failed."
        )

        return {
            "error": "Generation AI request failed.",
            "details": str(e)
        }

    print(
        "[GEN] OpenAI returned",
        flush=True
    )

    print(
        "[GEN] Parsing OpenAI response",
        flush=True
    )

    try:

        content = response.choices[0].message.content

        print(
            "[GEN] Response content received",
            flush=True
        )

    except Exception as e:

        return {
            "error": "AI response structure issue",
            "details": str(e),
            "raw": str(response)
        }

    try:

        parsed = json.loads(content)

        print(
            "[GEN] JSON parsed successfully",
            flush=True
        )

        return parsed

    except Exception as e:

        return {
            "error": "Invalid JSON from AI",
            "details": str(e),
            "raw_response": content
        }


def regenerate_paper(regeneration_prompt):

    encoding = tiktoken.get_encoding(
        "cl100k_base"
    )

    prompt_tokens = len(
        encoding.encode(regeneration_prompt)
    )

    logger.info(
        f"REGENERATION PROMPT TOKENS: {prompt_tokens}"
    )

    print(
        "[REGEN] Before OpenAI call",
        flush=True
    )

    full_regeneration_prompt = f"""
{regeneration_prompt}

============================================================
FINAL REGENERATION REQUIREMENTS
============================================================

You are repairing an already generated examination paper.

You MUST modify the existing paper rather than redesigning it.

The validation feedback identifies specific problems.
Fix those problems while preserving everything that is already valid.

============================================================
STRUCTURE PRESERVATION
============================================================

The regenerated paper MUST preserve:

- The exact number of sections.
- The exact section order.
- The exact section names.
- The exact number of questions in every section.
- The exact question order.
- The exact question-type distribution in every section.
- The exact question type of every existing question.
- The exact marks of every question unless the validation feedback explicitly identifies a marks error.
- The existing question group structure.

Do NOT:

- Add extra questions.
- Remove questions.
- Merge questions.
- Split questions.
- Move questions between sections.
- Change a question from one question type to another.
- Create a new section.
- Delete a section.
- Change section names.
- Change question counts merely to solve another validation error.

If a question is invalid, replace or rewrite the CONTENT of that question while keeping its position, question type, marks and required metadata.

============================================================
QUESTION METADATA
============================================================

EVERY question in the regenerated paper MUST contain:

- question
- question_type
- marks
- difficulty
- cognitive
- answer
- solution

difficulty MUST be exactly one of:

- Easy
- Medium
- Hard

cognitive MUST be exactly one of:

- Recall
- Understanding
- Application
- Analysis

Do NOT omit difficulty.

Do NOT omit cognitive.

Do NOT replace difficulty or cognitive with null, empty strings, or other values.

Preserve the existing difficulty and cognitive values when they are already valid.

Only change them when necessary to satisfy the validation feedback or the required blueprint.

============================================================
QUESTION-TYPE REQUIREMENTS
============================================================

MCQ:

- question must be non-empty.
- question_type must be "MCQ".
- Include exactly four options.
- options must contain four non-empty items.
- answer must be A, B, C, or D.
- Include solution.

True/False:

- question_type must be "True/False".
- Do not include MCQ options.
- answer must be "True" or "False".
- Include solution.

Fill in the Blanks:

- question_type must be "Fill in the Blanks".
- The question must contain a blank using ______.
- Do not include MCQ options.
- Include answer and solution.

Assertion-Reason:

- question_type must be "Assertion-Reason".
- Include a separate "assertion" field.
- Include a separate "reason" field.
- Assertion must be non-empty.
- Reason must be non-empty.
- Do NOT combine Assertion and Reason into the question field.
- Include answer and solution.

Match the Following:

- question_type must be "Match the Following".
- Include "left_column".
- Include "right_column".
- Both columns must be non-empty lists.
- Both columns must contain the same number of items.
- Do not use MCQ options.
- Include answer and solution.

Source-Based Questions:

- question_type must be "Source-Based Questions".
- Include a meaningful non-empty "source" field.
- Include answer and solution.

Diagram-Based Questions:

- question_type must be "Diagram-Based Questions".
- Include a meaningful non-empty "diagram" field.
- Include answer and solution.

Case Study:

- question_type must be "Case Study".
- Include a meaningful non-empty "case" field.
- Include answer and solution.

Other question types:

- Preserve their existing question_type.
- Preserve their position.
- Preserve their marks.
- Include question, question_type, marks, difficulty, cognitive, answer and solution.

============================================================
MARKS PRESERVATION
============================================================

Preserve the marks of every valid question.

The sum of question marks in each section MUST remain equal to the required section marks.

The total paper marks MUST remain equal to the required total marks.

Do not reduce the number of questions to solve a marks problem.

Do not increase the number of questions to solve a marks problem.

Correct the marks of existing questions only when the validation feedback explicitly identifies a marks mismatch.

============================================================
VALIDATION REPAIR
============================================================

Fix EVERY validation error supplied in the regeneration prompt.

When the feedback says that a question type count is wrong:

- Keep the total number of questions unchanged.
- Keep the section unchanged.
- Keep the required question positions.
- Correct the question type distribution by replacing the content/type of existing questions where necessary.

When the feedback identifies missing fields:

- Add the missing field to the affected question.
- Do not remove the question.
- Do not create an additional question.

When the feedback identifies difficulty or cognitive distribution problems:

- Correct the difficulty/cognitive values of existing questions.
- Do not change the number of questions.
- Keep the required question types and marks unchanged.

When the feedback identifies duplicate or similar questions:

- Rewrite the affected question content.
- Preserve its question type, marks, difficulty, cognitive level and position unless the validation feedback requires otherwise.

============================================================
FINAL SELF-CHECK
============================================================

Before returning the JSON, verify ALL of the following:

- Correct number of sections.
- Correct section names.
- Correct section order.
- Correct number of questions per section.
- Correct question order.
- Correct question-type counts.
- Correct marks per question.
- Correct section marks.
- Correct total marks.
- Every question has question.
- Every question has question_type.
- Every question has marks.
- Every question has difficulty.
- Every question has cognitive.
- Every question has answer.
- Every question has solution.
- Assertion-Reason questions have assertion and reason.
- Match the Following questions have valid left_column and right_column.
- MCQs have exactly four options.
- True/False questions have True or False answers.
- Fill in the Blanks questions contain a blank.
- Source-Based questions contain source.
- Diagram-Based questions contain diagram.
- Case Study questions contain case.

Return the COMPLETE repaired paper.

Return ONLY valid JSON.

============================================================
JSON STRUCTURE
============================================================

{{
    "title": "Exam Paper Title",
    "sections": [
        {{
            "section_name": "Section A",
            "questions": [
                {{
                    "question": "Question text",
                    "question_type": "MCQ",
                    "marks": 1,
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "options": [
                        "Option 1",
                        "Option 2",
                        "Option 3",
                        "Option 4"
                    ],
                    "answer": "A",
                    "solution": "Explanation of the answer"
                }}
            ]
        }}
    ]
}}

Return ONLY JSON.
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
                    "content": full_regeneration_prompt
                }
            ]
        )

    except Exception as e:

        logger.exception(
            "Regeneration OpenAI API call failed."
        )

        return {
            "error": "Regeneration AI request failed.",
            "details": str(e)
        }

    print(
        "[REGEN] OpenAI returned",
        flush=True
    )

    try:

        print_usage(response)

    except Exception as e:

        logger.error(
            f"Unable to read OpenAI usage data: {e}"
        )

    try:

        content = response.choices[0].message.content

    except Exception as e:

        return {
            "error": "AI response structure issue",
            "details": str(e),
            "raw": str(response)
        }

    try:

        parsed = json.loads(content)

        return parsed

    except Exception as e:

        return {
            "error": "Invalid JSON from AI",
            "details": str(e),
            "raw_response": content
        }


def print_usage(response):

    usage = response.usage

    print()

    logger.info(
        f"Prompt Tokens: {usage.prompt_tokens}"
    )

    logger.info(
        f"Completion Tokens: {usage.completion_tokens}"
    )

    logger.info(
        f"Total Tokens: {usage.total_tokens}"
    )