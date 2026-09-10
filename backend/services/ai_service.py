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
    return "\n".join(
        f"- {i}"
        for i in instructions_list
    )


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
"""


def get_question_type_rules(question_type):

    rules = {
        "MCQ": """
- question_type must be "MCQ".
- Generate exactly four non-empty options.
- answer must be A, B, C, or D.
- Do not omit options.
""",

        "True/False": """
- question_type must be "True/False".
- Do not include MCQ options.
- answer must be "True" or "False".
""",

        "Fill in the Blanks": """
- question_type must be "Fill in the Blanks".
- The question must contain ______.
- Do not include MCQ options.
""",

        "Assertion-Reason": """
- question_type must be "Assertion-Reason".
- Include a separate non-empty "assertion" field.
- Include a separate non-empty "reason" field.
- Do not combine assertion and reason into the question field.
""",

        "Match the Following": """
- question_type must be "Match the Following".
- Include non-empty "left_column".
- Include non-empty "right_column".
- Both columns must contain the same number of items.
- Do not use MCQ options.
""",

        "Source-Based Questions": """
- question_type must be "Source-Based Questions".
- Include a meaningful non-empty "source" field.
""",

        "Diagram-Based Questions": """
- question_type must be "Diagram-Based Questions".
- Include a meaningful non-empty "diagram" field.
""",

        "Case Study": """
- question_type must be "Case Study".
- Include a meaningful non-empty "case" field.
""",

        "Application-based": """
- question_type must be "Application-based".
""",

        "HOTS": """
- question_type must be "HOTS".
""",

        "One Word Answer": """
- question_type must be "One Word Answer".
""",

        "Very Short Answer": """
- question_type must be "Very Short Answer".
""",

        "Short Answer": """
- question_type must be "Short Answer".
""",

        "Long Answer": """
- question_type must be "Long Answer".
"""
    }

    return rules.get(
        question_type,
        f"""
- question_type must be "{question_type}".
"""
    )


def build_group_prompt(
        data,
        section,
        group,
        exam_prompt,
        exam_blueprint,
        cognitive_blueprint,
        instructions,
        reference_paper
):

    section_name = section.get(
        "section_name",
        "Section A"
    )

    question_type = group["question_type"]
    question_count = int(
        group["question_count"]
    )

    marks_per_question = int(
        group["marks_per_question"]
    )

    allocation = allocate_questions(
        data.get(
            "exam_type",
            "General Exam Paper"
        ),
        question_count
    )

    question_type_rules = get_question_type_rules(
        question_type
    )

    prompt = f"""
You are generating one question-type group for an examination paper.

You are NOT generating the complete examination paper.

You are generating ONLY the requested question group below.

==================================================
EXAMINATION
==================================================

Exam Type: {data.get("exam_type")}
Subject: {data.get("subject")}
Class: {data.get("class_name")}
Topics: {data.get("topics")}
Overall Difficulty: {data.get("difficulty")}

==================================================
SECTION
==================================================

Section Name: {section_name}

==================================================
LOCKED QUESTION GROUP
==================================================

Question Type: {question_type}
Question Count: {question_count}
Marks Per Question: {marks_per_question}
Group Total Marks: {group.get("marks")}

THE FOLLOWING VALUES ARE ABSOLUTE:

- Generate EXACTLY {question_count} questions.
- Every generated question MUST have question_type "{question_type}".
- Every generated question MUST have exactly {marks_per_question} marks.
- Do NOT generate any other question type.
- Do NOT generate fewer questions.
- Do NOT generate additional questions.
- Do NOT create sections.
- Do NOT return questions belonging to another group.

==================================================
COGNITIVE ALLOCATION
==================================================

Recall: {allocation["recall"]}
Understanding: {allocation["understanding"]}
Application: {allocation["application"]}
Analysis: {allocation["analysis"]}

Use these integer allocations when assigning the cognitive field.

==================================================
REQUIRED METADATA
==================================================

Every question MUST contain:

- question
- question_type
- marks
- difficulty
- cognitive
- answer
- solution

difficulty must be exactly one of:

- Easy
- Medium
- Hard

cognitive must be exactly one of:

- Recall
- Understanding
- Application
- Analysis

==================================================
QUESTION TYPE RULES
==================================================

{question_type_rules}

==================================================
EXAM REQUIREMENTS
==================================================

{exam_prompt}

==================================================
EXAM BLUEPRINT
==================================================

{exam_blueprint}

==================================================
INSTRUCTIONS
==================================================

{instructions}

==================================================
REFERENCE INFORMATION
==================================================

{reference_paper}

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Return exactly this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "question_type": "{question_type}",
            "marks": {marks_per_question},
            "difficulty": "Medium",
            "cognitive": "Application",
            "answer": "Answer",
            "solution": "Solution"
        }}
    ]
}}

The questions array MUST contain exactly {question_count} items.

Every item MUST have question_type exactly "{question_type}".

Every item MUST have marks exactly {marks_per_question}.

Do not return a title.

Do not return sections.

Do not return explanations outside JSON.

Return ONLY JSON.
"""

    return prompt


def call_openai_json(prompt):

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
            "OpenAI API call failed."
        )

        return {
            "error": "AI request failed.",
            "details": str(e)
        }

    try:

        content = response.choices[0].message.content

    except Exception as e:

        return {
            "error": "AI response structure issue.",
            "details": str(e),
            "raw": str(response)
        }

    try:

        return json.loads(content)

    except Exception as e:

        return {
            "error": "Invalid JSON from AI.",
            "details": str(e),
            "raw_response": content
        }


def validate_group_output(
        result,
        question_type,
        question_count,
        marks_per_question
):

    if not isinstance(result, dict):

        return False

    questions = result.get(
        "questions",
        []
    )

    if not isinstance(
        questions,
        list
    ):

        return False

    if len(questions) != question_count:

        return False

    for question in questions:

        if not isinstance(
            question,
            dict
        ):

            return False

        if question.get(
            "question_type"
        ) != question_type:

            return False

        if question.get(
            "marks"
        ) != marks_per_question:

            return False

        if not str(
            question.get(
                "question",
                ""
            )
        ).strip():

            return False

        if not str(
            question.get(
                "difficulty",
                ""
            )
        ).strip():

            return False

        if question.get(
            "difficulty"
        ) not in (
            "Easy",
            "Medium",
            "Hard"
        ):

            return False

        if question.get(
            "cognitive"
        ) not in (
            "Recall",
            "Understanding",
            "Application",
            "Analysis"
        ):

            return False

        if not str(
            question.get(
                "answer",
                ""
            )
        ).strip():

            return False

        if not str(
            question.get(
                "solution",
                ""
            )
        ).strip():

            return False

    return True


def generate_question_group(
        data,
        section,
        group,
        exam_prompt,
        exam_blueprint,
        cognitive_blueprint,
        instructions,
        reference_paper
):

    question_type = group["question_type"]

    question_count = int(
        group["question_count"]
    )

    marks_per_question = int(
        group["marks_per_question"]
    )

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1
    ):

        logger.info(
            f"Generating group: "
            f"{question_type} | "
            f"Attempt {attempt}/{max_attempts}"
        )

        prompt = build_group_prompt(
            data=data,
            section=section,
            group=group,
            exam_prompt=exam_prompt,
            exam_blueprint=exam_blueprint,
            cognitive_blueprint=cognitive_blueprint,
            instructions=instructions,
            reference_paper=reference_paper
        )

        encoding = tiktoken.get_encoding(
            "cl100k_base"
        )

        logger.info(
            f"GROUP PROMPT TOKENS: "
            f"{len(encoding.encode(prompt))}"
        )

        result = call_openai_json(
            prompt
        )

        if (
            "error" not in result
            and validate_group_output(
                result,
                question_type,
                question_count,
                marks_per_question
            )
        ):

            logger.info(
                f"Group generated successfully: "
                f"{question_type}"
            )

            return result["questions"]

        logger.warning(
            f"Invalid group output for "
            f"{question_type} on attempt {attempt}."
        )

    return {
        "error": (
            f"Unable to generate exactly "
            f"{question_count} questions of type "
            f"{question_type}."
        )
    }


def generate_paper(
        data,
        uploaded_content="",
        pattern_summary=""
):

    logger.info(
        "Received paper generation request."
    )

    exam_type = data.get(
        "exam_type",
        "General Exam Paper"
    )

    exam_prompt = get_exam_prompt(
        exam_type
    )

    exam_blueprint = get_blueprint(
        exam_type
    )

    cognitive_blueprint = get_cognitive_blueprint(
        exam_type
    )

    instructions_list = format_instructions(
        data.get(
            "instructions",
            ""
        )
    )

    instructions = instructions_to_text(
        instructions_list
    )

    reference_paper = ""

    if pattern_summary.strip():

        reference_paper = f"""
REFERENCE PAPER ANALYSIS

{pattern_summary}

Use this information for:

- Similar difficulty.
- Similar assessment style.
- Similar structure.

Do NOT copy questions.

Generate completely original questions.
"""

    sections = []

    for section in data.get(
        "sections",
        []
    ):

        section_name = (
            section.get(
                "section_name"
            )
            or "Section A"
        )

        expected_questions = int(
            section["question_count"]
        )

        expected_marks = int(
            section["marks"]
        )

        groups = section.get(
            "question_groups",
            []
        )

        generated_questions = []

        for group in groups:

            questions = generate_question_group(
                data=data,
                section=section,
                group=group,
                exam_prompt=exam_prompt,
                exam_blueprint=exam_blueprint,
                cognitive_blueprint=cognitive_blueprint,
                instructions=instructions,
                reference_paper=reference_paper
            )

            if isinstance(
                questions,
                dict
            ) and "error" in questions:

                return questions

            generated_questions.extend(
                questions
            )

        actual_question_count = len(
            generated_questions
        )

        actual_marks = sum(
            int(
                question.get(
                    "marks",
                    0
                )
            )
            for question in generated_questions
        )

        if actual_question_count != expected_questions:

            return {
                "error": (
                    f"{section_name} generation failed: "
                    f"expected {expected_questions} "
                    f"questions, got "
                    f"{actual_question_count}."
                )
            }

        if actual_marks != expected_marks:

            return {
                "error": (
                    f"{section_name} generation failed: "
                    f"expected {expected_marks} marks, "
                    f"got {actual_marks}."
                )
            }

        sections.append(
            {
                "section_name": section_name,
                "questions": generated_questions
            }
        )

    total_questions = sum(
        len(
            section["questions"]
        )
        for section in sections
    )

    total_marks = sum(
        sum(
            int(
                question.get(
                    "marks",
                    0
                )
            )
            for question in section["questions"]
        )
        for section in sections
    )

    if total_questions != sum(
        int(
            section["question_count"]
        )
        for section in data.get(
            "sections",
            []
        )
    ):

        return {
            "error": (
                "Final generation failed: "
                "total question count mismatch."
            )
        }

    if total_marks != int(
        data.get(
            "total_marks",
            0
        )
    ):

        return {
            "error": (
                "Final generation failed: "
                "total marks mismatch."
            )
        }

    return {
        "title": data.get(
            "exam_name",
            "Exam Paper"
        ),
        "sections": sections
    }


def regenerate_paper(
        regeneration_prompt
):

    encoding = tiktoken.get_encoding(
        "cl100k_base"
    )

    prompt_tokens = len(
        encoding.encode(
            regeneration_prompt
        )
    )

    logger.info(
        f"REGENERATION PROMPT TOKENS: "
        f"{prompt_tokens}"
    )

    print(
        "[REGEN] Before OpenAI call",
        flush=True
    )

    full_regeneration_prompt = f"""
{regeneration_prompt}

==================================================
REGENERATION OUTPUT RULES
==================================================

Repair the existing examination paper.

Return ONLY valid JSON.

Every question MUST contain:

- question
- question_type
- marks
- difficulty
- cognitive
- answer
- solution

difficulty must be exactly:

Easy
Medium
Hard

cognitive must be exactly:

Recall
Understanding
Application
Analysis

For Assertion-Reason questions:

- Include assertion.
- Include reason.
- Keep them as separate fields.

For Match the Following questions:

- Include left_column.
- Include right_column.
- Both must be non-empty.
- Both must have equal length.

For MCQ:

- Include exactly four options.
- Answer must be A, B, C, or D.

For True/False:

- Answer must be True or False.

For Fill in the Blanks:

- Include ______ in the question.

For Source-Based Questions:

- Include source.

For Diagram-Based Questions:

- Include diagram.

For Case Study:

- Include case.

MOST IMPORTANT:

Do not change the number of sections.

Do not change section order.

Do not change section names.

Do not add questions.

Do not remove questions.

Do not move questions between sections.

Do not change question types unless the validation feedback explicitly identifies a wrong question type.

Do not change valid marks.

Return the complete repaired paper.

Return ONLY JSON.
"""

    result = call_openai_json(
        full_regeneration_prompt
    )

    return result


def print_usage(response):

    usage = response.usage

    print()

    logger.info(
        f"Prompt Tokens: "
        f"{usage.prompt_tokens}"
    )

    logger.info(
        f"Completion Tokens: "
        f"{usage.completion_tokens}"
    )

    logger.info(
        f"Total Tokens: "
        f"{usage.total_tokens}"
    )