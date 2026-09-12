import json
from backend.exam_patterns import get_exam_prompt, get_blueprint
from backend.exam_patterns.blueprints import get_cognitive_blueprint
from backend.services.expected_blueprint import get_expected_blueprint
from backend.prompt_engine.prompt_builder import build_prompt
from backend.core.ai_client import client
from backend.utils.logger import logger
from collections import Counter
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


def allocate_integer_counts(total_questions, distribution):

    if total_questions <= 0 or not distribution:
        return {}

    total_distribution = sum(distribution.values())

    if total_distribution <= 0:
        return {}

    normalized = {
        key: value / total_distribution
        for key, value in distribution.items()
    }

    raw = {
        key: total_questions * value
        for key, value in normalized.items()
    }

    counts = {
        key: int(value)
        for key, value in raw.items()
    }

    remaining = total_questions - sum(counts.values())

    remainders = sorted(
        normalized.keys(),
        key=lambda key: raw[key] - counts[key],
        reverse=True
    )

    for key in remainders[:remaining]:
        counts[key] += 1

    return counts


def distribute_targets(total_targets, group_sizes):

    remaining_targets = dict(total_targets)

    remaining_questions = sum(group_sizes)

    allocations = []

    for index, group_size in enumerate(group_sizes):

        if index == len(group_sizes) - 1:

            allocation = dict(remaining_targets)

        else:

            raw = {}

            for key, target in remaining_targets.items():

                raw[key] = (
                    target * group_size
                    / remaining_questions
                )

            allocation = {
                key: int(value)
                for key, value in raw.items()
            }

            remaining = group_size - sum(
                allocation.values()
            )

            remainders = sorted(
                raw.keys(),
                key=lambda key: (
                    raw[key] - allocation[key]
                ),
                reverse=True
            )

            for key in remainders[:remaining]:
                allocation[key] += 1

        allocations.append(allocation)

        for key, value in allocation.items():

            remaining_targets[key] = (
                remaining_targets.get(key, 0) - value
            )

        remaining_questions -= group_size

    return allocations


def build_group_prompt(
    data,
    section,
    group,
    exam_prompt,
    exam_blueprint,
    cognitive_blueprint,
    instructions,
    reference_paper,
    existing_questions=None,
    cognitive_allocation=None,
    difficulty_allocation=None
):

    if existing_questions is None:
        existing_questions = []

    if cognitive_allocation is None:
        cognitive_allocation = {
            "Recall": 0,
            "Understanding": 0,
            "Application": 0,
            "Analysis": 0
        }

    if difficulty_allocation is None:
        difficulty_allocation = {
            "Easy": 0,
            "Medium": 0,
            "Hard": 0
        }

    existing_question_text = "\n".join(
        f"- {question.get('question', '').strip()}"
        for question in existing_questions
        if question.get("question")
    )

    if not existing_question_text:
        existing_question_text = "No previous questions."

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

    question_type_rules = get_question_type_rules(
        question_type
    )

    if question_type == "MCQ":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "question_type": "MCQ",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "options": [
                        "Option 1",
                        "Option 2",
                        "Option 3",
                        "Option 4"
                    ],
                    "answer": "A",
                    "solution": "Explanation of the correct answer"
                }}
            ]
        }}
        """

    elif question_type == "True/False":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Statement that can be evaluated as true or false.",
                    "question_type": "True/False",
                    "marks": {marks_per_question},
                    "difficulty": "Easy",
                    "cognitive": "Recall",
                    "answer": "True",
                    "solution": "Explanation of why the statement is true or false."
                }}
            ]
        }}
        """

    elif question_type == "Fill in the Blanks":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "The SI unit of force is ______.",
                    "question_type": "Fill in the Blanks",
                    "marks": {marks_per_question},
                    "difficulty": "Easy",
                    "cognitive": "Recall",
                    "answer": "Newton",
                    "solution": "The SI unit of force is Newton."
                }}
            ]
        }}
        """

    elif question_type == "Assertion-Reason":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Select the correct relationship between the Assertion and Reason.",
                    "question_type": "Assertion-Reason",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Analysis",
                    "assertion": "A separate assertion statement.",
                    "reason": "A separate reason statement.",
                    "answer": "Both Assertion and Reason are true, and Reason correctly explains Assertion.",
                    "solution": "Explanation of the relationship between the assertion and reason."
                }}
            ]
        }}
        """

    elif question_type == "Match the Following":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Match Column I with Column II.",
                    "question_type": "Match the Following",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Understanding",
                    "left_column": [
                        "Item 1",
                        "Item 2",
                        "Item 3",
                        "Item 4"
                    ],
                    "right_column": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "1-A, 2-C, 3-D, 4-B",
                    "solution": "Explanation of each correct matching."
                }}
            ]
        }}
        """

    elif question_type == "Source-Based Questions":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Answer the question based on the given source.",
                    "question_type": "Source-Based Questions",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Analysis",
                    "source": "A meaningful source passage, data, statement, extract, or information related to the subject.",
                    "answer": "Answer based on the source.",
                    "solution": "Explanation using the information provided in the source."
                }}
            ]
        }}
        """

    elif question_type == "Diagram-Based Questions":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Study the diagram and answer the question.",
                    "question_type": "Diagram-Based Questions",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "diagram": "Description of the required diagram or visual representation.",
                    "answer": "Answer based on the diagram.",
                    "solution": "Explanation based on the diagram."
                }}
            ]
        }}
        """

    elif question_type == "Case Study":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Answer the question based on the case study.",
                    "question_type": "Case Study",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "case": "A detailed and meaningful case, scenario, experiment, passage, or real-world situation related to the subject.",
                    "answer": "Answer based on the case.",
                    "solution": "Explanation of the answer using the case information."
                }}
            ]
        }}
        """

    elif question_type == "Application-based":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "A real-world or practical situation is described. Apply the relevant concept, principle, formula, or method to solve the given problem.",
                    "question_type": "Application-based",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Application",
                    "answer": "Answer obtained by applying the relevant concept.",
                    "solution": "Step-by-step explanation showing how the relevant concept is applied to reach the answer."
                }}
            ]
        }}
        """

    elif question_type == "HOTS":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "A challenging higher-order question requiring deep reasoning, analysis, evaluation, or multi-step problem solving.",
                    "question_type": "HOTS",
                    "marks": {marks_per_question},
                    "difficulty": "Hard",
                    "cognitive": "Analysis",
                    "answer": "Final answer based on the reasoning.",
                    "solution": "Detailed step-by-step reasoning explaining how the answer is obtained."
                }}
            ]
        }}
        """

    elif question_type == "One Word Answer":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "What is the SI unit of force?",
                    "question_type": "One Word Answer",
                    "marks": {marks_per_question},
                    "difficulty": "Easy",
                    "cognitive": "Recall",
                    "answer": "Newton",
                    "solution": "The SI unit of force is Newton."
                }}
            ]
        }}
        """

    elif question_type == "Very Short Answer":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Define velocity.",
                    "question_type": "Very Short Answer",
                    "marks": {marks_per_question},
                    "difficulty": "Easy",
                    "cognitive": "Recall",
                    "answer": "Velocity is the rate of change of displacement with respect to time.",
                    "solution": "Velocity is defined as the rate of change of displacement with time."
                }}
            ]
        }}
        """

    elif question_type == "Short Answer":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Explain the relationship between force, mass, and acceleration.",
                    "question_type": "Short Answer",
                    "marks": {marks_per_question},
                    "difficulty": "Medium",
                    "cognitive": "Understanding",
                    "answer": "Force is equal to the product of mass and acceleration.",
                    "solution": "According to Newton's second law, force is proportional to the rate of change of momentum. For constant mass, this gives F = ma."
                }}
            ]
        }}
        """

    elif question_type == "Long Answer":
        output_example = f"""
        {{
            "questions": [
                {{
                    "question": "Explain Newton's laws of motion in detail with suitable examples.",
                    "question_type": "Long Answer",
                    "marks": {marks_per_question},
                    "difficulty": "Hard",
                    "cognitive": "Understanding",
                    "answer": "Newton's three laws describe the relationship between the motion of an object and the forces acting on it.",
                    "solution": "Provide a detailed explanation of all three laws, their mathematical expressions where applicable, and suitable examples demonstrating each law."
                }}
            ]
        }}
        """

    else:
        output_example = f"""
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
        """
        
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

Recall: {cognitive_allocation.get("Recall", 0)}
Understanding: {cognitive_allocation.get("Understanding", 0)}
Application: {cognitive_allocation.get("Application", 0)}
Analysis: {cognitive_allocation.get("Analysis", 0)}

These are exact integer targets for this group.

The total number of questions assigned across these cognitive
levels MUST equal {question_count}.

==================================================
EXACT DIFFICULTY ALLOCATION
==================================================

Easy: {difficulty_allocation.get("Easy", 0)}
Medium: {difficulty_allocation.get("Medium", 0)}
Hard: {difficulty_allocation.get("Hard", 0)}

The difficulty allocation above is an EXACT requirement.
The group MUST contain exactly these numbers of Easy, Medium and Hard questions.
The sum MUST equal exactly {question_count}.

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
QUESTIONS ALREADY GENERATED IN THIS PAPER
==================================================

{existing_question_text}

Every new question must be substantially different from every
question listed above.

Do not repeat:

- The same question wording.
- The same numerical values.
- The same scenario.
- The same concept using nearly identical wording.
- The same answer with only superficial wording changes.

Create genuinely different questions.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Return exactly this JSON structure:

{output_example}

The JSON structure above is mandatory.

For MCQ questions:
- The "options" field is REQUIRED.
- It MUST be a JSON array.
- It MUST contain exactly 4 non-empty strings.
- "answer" MUST be exactly one of "A", "B", "C", or "D".
- Never omit the "options" field.

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
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        logger.exception("OpenAI API call failed.")
        return {"error": "AI request failed.", "details": str(e)}

    try:
        content = response.choices[0].message.content
    except Exception as e:
        return {"error": "AI response structure issue.", "details": str(e), "raw": str(response)}

    try:
        return json.loads(content)
    except Exception as e:
        return {"error": "Invalid JSON from AI.", "details": str(e), "raw_response": content}


def validate_group_output(
        result,
        question_type,
        question_count,
        marks_per_question,
):

    if not isinstance(result, dict):
        return False, "Result is not a JSON object."

    questions = result.get("questions", [])

    if not isinstance(questions, list):
        return False, "questions is not a list."

    if len(questions) != question_count:
        return False, f"Expected {question_count} questions, got {len(questions)}."

    cognitive_counts = Counter()
    difficulty_counts = Counter()

    for index, question in enumerate(questions, 1):
        if not isinstance(question, dict):
            return False, f"Question {index} is not an object."

        if question.get("question_type") != question_type:
            return False, f"Question {index} has wrong question_type."
        
        if question.get("marks") != marks_per_question:
            return False, f"Question {index} has wrong marks."
        
        if not str(question.get("question", "")).strip():
            return False, f"Question {index} has empty question text."
        
        if question.get("difficulty") not in ("Easy", "Medium", "Hard"):
            return False, f"Question {index} has invalid difficulty."
        
        if question.get("cognitive") not in ("Recall", "Understanding", "Application", "Analysis"):
            return False, f"Question {index} has invalid cognitive level."
        
        if not str(question.get("answer", "")).strip():
            return False, f"Question {index} has empty answer."
        
        if not str(question.get("solution", "")).strip():
            return False, f"Question {index} has empty solution."

        if question_type == "MCQ":
            options = question.get("options")
            if not isinstance(options, list) or len(options) != 4:
                return False, f"Question {index} MCQ must have exactly 4 options."
            
            if any(not str(option).strip() for option in options):
                return False, f"Question {index} MCQ has an empty option."
            
            if question.get("answer") not in ("A", "B", "C", "D"):
                return False, f"Question {index} MCQ answer must be A/B/C/D."

        if question_type == "True/False":
            if str(question.get("answer", "")).strip().lower() not in ("true", "false"):
                return False, f"Question {index} True/False answer is invalid."

        if question_type == "Fill in the Blanks" and "______" not in str(question.get("question", "")):
            return False, f"Question {index} Fill in the Blanks is missing ______."

        if question_type == "Assertion-Reason":
            if not str(question.get("assertion", "")).strip() or not str(question.get("reason", "")).strip():
                return False, f"Question {index} Assertion-Reason is missing assertion or reason."

        if question_type == "Match the Following":
            left = question.get("left_column")
            right = question.get("right_column")
            if not isinstance(left, list) or not left:
                return False, f"Question {index} Match the Following is missing left_column."
            
            if not isinstance(right, list) or not right:
                return False, f"Question {index} Match the Following is missing right_column."
            
            if len(left) != len(right):
                return False, f"Question {index} Match the Following columns have different lengths."

        if question_type == "Source-Based Questions" and not str(question.get("source", "")).strip():
            return False, f"Question {index} Source-Based Questions is missing source."

        if question_type == "Diagram-Based Questions" and not str(question.get("diagram", "")).strip():
            return False, f"Question {index} Diagram-Based Questions is missing diagram."

        if question_type == "Case Study" and not str(question.get("case", "")).strip():
            return False, f"Question {index} Case Study is missing case."

        cognitive_counts[question["cognitive"]] += 1
        difficulty_counts[question["difficulty"]] += 1

    return True, "valid"


def generate_question_group(
    data,
    section,
    group,
    exam_prompt,
    exam_blueprint,
    cognitive_blueprint,
    instructions,
    reference_paper,
    existing_questions=None,
    cognitive_allocation=None,
    difficulty_allocation=None
):

    if existing_questions is None:
        existing_questions = []

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
            reference_paper=reference_paper,
            existing_questions=existing_questions,
            cognitive_allocation=cognitive_allocation,
            difficulty_allocation=difficulty_allocation
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
            isinstance(result, dict)
            and "error" not in result
            and validate_group_output(
                result,
                question_type,
                question_count,
                marks_per_question,
                cognitive_allocation,
                difficulty_allocation
            )[0]
        ):

            logger.info(
                f"Group generated successfully: "
                f"{question_type}"
            )

            return result["questions"]

        if isinstance(result, dict) and "error" in result:
            reason = result.get("error", "AI request failed.")
        else:
            _, reason = validate_group_output(
                result,
                question_type,
                question_count,
                marks_per_question
            )
        logger.warning(
            f"Invalid group output for {question_type} on attempt {attempt}: {reason}"
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

    all_groups = []

    for section in data.get(
        "sections",
        []
    ):

        for group in section.get(
            "question_groups",
            []
        ):

            all_groups.append(
                {
                    "section": section,
                    "group": group
                }
            )

    total_questions = sum(
        int(item["group"]["question_count"])
        for item in all_groups
    )

    expected_blueprint = get_expected_blueprint(
        exam_type,
        data.get("subject", "")
    )

    expected_cognitive_distribution = expected_blueprint.get(
        "cognitive_distribution",
        {}
    )

    if not expected_cognitive_distribution:
        expected_cognitive_distribution = {
            "Recall": cognitive_blueprint.get("recall", 0),
            "Understanding": cognitive_blueprint.get("understanding", 0),
            "Application": cognitive_blueprint.get("application", 0),
            "Analysis": cognitive_blueprint.get("analysis", 0)
        }

    global_cognitive = allocate_integer_counts(
        total_questions,
        expected_cognitive_distribution
    )

    global_difficulty = allocate_integer_counts(
        total_questions,
        expected_blueprint.get(
            "difficulty_distribution",
            {"Easy": 0.30, "Medium": 0.50, "Hard": 0.20}
        )
    )

    group_sizes = [
        int(item["group"]["question_count"])
        for item in all_groups
    ]

    group_cognitive_allocations = distribute_targets(
        global_cognitive,
        group_sizes
    )

    group_difficulty_allocations = distribute_targets(
        global_difficulty,
        group_sizes
    )

    sections = []

    generated_by_section = {}

    for index, item in enumerate(all_groups):

        section = item["section"]

        group = item["group"]

        section_name = (
            section.get("section_name")
            or "Section A"
        )

        if section_name not in generated_by_section:

            generated_by_section[section_name] = []

        generated_questions = generated_by_section[
            section_name
        ]

        questions = generate_question_group(
            data=data,
            section=section,
            group=group,
            exam_prompt=exam_prompt,
            exam_blueprint=exam_blueprint,
            cognitive_blueprint=cognitive_blueprint,
            instructions=instructions,
            reference_paper=reference_paper,
            existing_questions=generated_questions,
            cognitive_allocation=(
                group_cognitive_allocations[index]
            ),
            difficulty_allocation=(
                group_difficulty_allocations[index]
            )
        )

        if (
            isinstance(questions, dict)
            and "error" in questions
        ):

            return questions

        generated_questions.extend(
            questions
        )

    for section in data.get(
        "sections",
        []
    ):

        section_name = (
            section.get("section_name")
            or "Section A"
        )

        generated_questions = generated_by_section.get(
            section_name,
            []
        )

        expected_questions = int(
            section["question_count"]
        )

        expected_marks = int(
            section["marks"]
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

    final_question_count = sum(
        len(section["questions"])
        for section in sections
    )

    final_marks = sum(
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

    expected_total_questions = sum(
        int(
            section["question_count"]
        )
        for section in data.get(
            "sections",
            []
        )
    )

    if final_question_count != expected_total_questions:

        return {
            "error": (
                "Final generation failed: "
                "total question count mismatch."
            )
        }

    if final_marks != int(
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