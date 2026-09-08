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
        line = line[0].upper() + line[1:] if len(line) > 1 else line.upper()

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
- Include question, options, answer and solution.

True/False:
- Include the question.
- Do NOT include options.
- Answer must be "True" or "False".
- Include a solution.

Fill in the Blanks:
- Include the blank directly in the question using ______.
- Do NOT include MCQ options.
- Include the correct answer and solution.

Assertion-Reason:
- Include:
  "question": "Read the following Assertion and Reason.",
  "assertion": "...",
  "reason": "...",
  "answer": "...",
  "solution": "..."
- Assertion and Reason must be separate fields.
- Do NOT put Assertion and Reason together in one field.

Match the Following:
- Include:
  "question": "...",
  "left_column": ["..."],
  "right_column": ["..."],
  "answer": "...",
  "solution": "..."
- left_column and right_column must both be non-empty.
- Both columns must contain the same number of items.
- Do NOT use MCQ options for Match the Following.

Source-Based:
- Include:
  "question": "...",
  "source": "...",
  "answer": "...",
  "solution": "..."
- The source/passage must be meaningful and relevant to the question.

Diagram-Based:
- Include:
  "question": "...",
  "diagram": "...",
  "answer": "...",
  "solution": "..."
- The diagram field must describe the required diagram clearly.

Case Study:
- Include:
  "question": "...",
  "case": "...",
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
"""

def generate_paper(data, uploaded_content="", pattern_summary=""):
    logger.info("Received paper generation request.")

    exam_prompt = get_exam_prompt(data["exam_type"])
    exam_blueprint = get_blueprint(data["exam_type"])

    section_data = ""
    exam_type = data.get("exam_type", "General Exam Paper")

    if data.get("sections"):
        for index, section in enumerate(data["sections"]):
            section_name = section.get("section_name") or f"Section {chr(65 + index)}"
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

                allocation = allocate_questions(exam_type, question_count)

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

    instructions_list = format_instructions(data.get("instructions", ""))
    instructions = instructions_to_text(instructions_list)

    cognitive_blueprint = get_cognitive_blueprint(exam_type)

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

    encoding = tiktoken.get_encoding("cl100k_base")
    prompt_tokens = len(encoding.encode(prompt))

    logger.info(f"PROMPT TOKENS: {prompt_tokens}")
    logger.info(f"REFERENCE PAPER LENGTH: {len(reference_paper)}")

    print("[GEN] Calling OpenAI now", flush=True)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        timeout=60.0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    print("[GEN] OpenAI returned", flush=True)
    print("[GEN] Parsing OpenAI response", flush=True)

    try:
        content = response.choices[0].message.content
        print("[GEN] Response content received", flush=True)
    except Exception as e:
        return {
            "error": "AI response structure issue",
            "details": str(e),
            "raw": str(response)
        }

    try:
        parsed = json.loads(content)
        print("[GEN] JSON parsed successfully", flush=True)
        return parsed
    except Exception as e:
        return {
            "error": "Invalid JSON from AI",
            "details": str(e),
            "raw_response": content
        }

def regenerate_paper(regeneration_prompt):
    encoding = tiktoken.get_encoding("cl100k_base")

    prompt_tokens = len(
        encoding.encode(regeneration_prompt)
    )

    logger.info(
        f"REGENERATION PROMPT TOKENS: {prompt_tokens}"
    )

    print("[REGEN] Before OpenAI call", flush=True)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        timeout=60.0,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "user",
                "content": regeneration_prompt
            }
        ]
    )

    print("[REGEN] OpenAI returned", flush=True)

    print_usage(response)

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