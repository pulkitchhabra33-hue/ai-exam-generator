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
    rules={
        "MCQ":"""
MCQ RULES
- Generate exactly one clear multiple-choice question.
- Provide exactly 4 answer options.
- Every option must be a complete, meaningful and plausible answer.
- Only one option must be correct unless the teacher explicitly requested otherwise.
- The options must be labeled A, B, C and D through the options array.
- The answer field must contain only A, B, C or D.
- Do not place the correct answer outside the options.
- Do not create duplicate or nearly identical options.
- Distractors must be plausible but objectively incorrect.
- Avoid clues such as noticeably longer correct options or grammatical mismatch.
""",

        "True/False":"""
TRUE/FALSE RULES
- Generate exactly one objectively true or false statement.
- The statement must be unambiguous.
- Avoid statements that depend on opinion, interpretation or incomplete context.
- The answer field must contain exactly True or False.
- Do not provide multiple statements in one question.
- Do not use double negatives unless absolutely necessary.
- The statement must be factually consistent with the requested syllabus.
""",

        "Fill in the Blanks":"""
FILL IN THE BLANKS RULES
- Generate exactly one sentence or statement containing a meaningful blank.
- The question text must contain a visible blank represented by "______".
- The blank must test a specific concept, fact, term, formula, value or relationship.
- The expected answer must be clearly identifiable.
- Do not create multiple possible answers unless the question explicitly allows them.
- Do not put the answer directly into the blank.
- The answer field must contain the expected missing word, phrase, value or expression.
""",

        "Assertion-Reason":"""
ASSERTION-REASON RULES
- Generate one Assertion and one Reason.
- The assertion and reason must be written as separate fields.
- Both must be clear, academically meaningful and related to the same concept.
- The question must allow evaluation of both the truth of the Assertion and the truth of the Reason, as well as their logical relationship.
- Do not combine Assertion and Reason into a single question string.
- Avoid trivial or obviously unrelated assertion-reason pairs.
- The answer must identify the correct assertion-reason relationship according to the provided answer convention.
- The reason should explain or logically relate to the assertion rather than merely repeat it.
""",

        "Match the Following":"""
MATCH THE FOLLOWING RULES
- Generate a genuine matching question with at least 2 items.
- Provide a left column and a right column as separate lists.
- left_column and right_column must both be non-empty.
- Both columns must contain the same number of items.
- Each left-column item must have one logically correct corresponding right-column item.
- Items must be clearly distinguishable.
- Do not provide a malformed or incomplete matching structure.
- The answer must clearly indicate the correct matching pairs.
- Distractors may be used only when they remain logically valid and unambiguous.
""",

        "Source-Based Questions":"""
SOURCE-BASED QUESTION RULES
- Provide a meaningful source, passage, data extract, quotation, table or other source material.
- The source must be relevant to the requested subject, topic and syllabus.
- Generate the question from the supplied source rather than asking an unrelated textbook question.
- The source must contain enough information to answer the question.
- Do not invent unsupported facts that are not reasonably inferable from the source.
- The source field and question field must be separate.
- The answer must be directly supported by or logically derived from the source.
""",

        "Case Study":"""
CASE STUDY RULES
- Provide a meaningful case, scenario, passage, experiment, situation or real-world context.
- The case field must be separate from the question field.
- The question must genuinely depend on the case.
- The case must contain enough information for the student to reason toward the answer.
- Do not create a generic textbook question and merely attach an unrelated case.
- The case must be appropriate for the requested class, subject and syllabus.
- The answer must be supported by the case and relevant subject knowledge.
""",

        "Application-based":"""
APPLICATION-BASED RULES
- Generate a question that requires the student to apply a learned concept, principle, formula, method or rule to a new situation.
- Do not merely ask the student to recall or define a fact.
- Use a realistic numerical, experimental, practical, contextual or unfamiliar scenario when appropriate.
- The student must determine how to apply the relevant concept to reach the answer.
- The situation should be different from a direct textbook definition or memorized example.
- The answer and solution must show the relevant application.
- Ensure the difficulty is appropriate for the requested class and marks.
""",

        "HOTS":"""
HOTS RULES
- Generate a genuinely higher-order thinking question.
- The question should require reasoning, analysis, evaluation, comparison, interpretation, synthesis or multi-step thinking.
- Do not classify a simple recall or direct formula-substitution question as HOTS.
- Avoid questions that can be answered by memorizing a single fact.
- When appropriate, provide data, conditions, competing explanations, constraints or a non-routine situation.
- The student should need to reason through the problem before reaching the answer.
- The solution must explain the reasoning, not only provide the final answer.
""",

        "One Word Answer":"""
ONE WORD ANSWER RULES
- Generate a question whose correct response is one word or a single concise term.
- The answer must be specific and objectively verifiable.
- Do not require a sentence, paragraph, derivation or explanation.
- Avoid questions with multiple equally valid one-word answers.
- The question should test a meaningful syllabus-based concept rather than trivial wording.
- The answer field must contain the expected single word or term.
""",

        "Very Short Answer":"""
VERY SHORT ANSWER RULES
- Generate a concise conceptual or factual question suitable for a very short response.
- The expected answer should normally require only a few words or a very short statement.
- Do not require lengthy explanation, derivation or multi-step analysis.
- The question must still test a meaningful syllabus concept.
- Avoid questions whose correct answer is ambiguous.
- The solution may briefly explain the answer but must remain consistent with the requested difficulty and marks.
""",

        "Short Answer":"""
SHORT ANSWER RULES
- Generate a question requiring a concise explanation, calculation, derivation, comparison or reasoning appropriate to the marks.
- The question should require more than a one-word or one-line response.
- Do not turn it into a long essay question.
- The expected answer should be proportional to the marks assigned.
- Include all necessary information, values and conditions needed to answer the question.
- The solution should show the essential reasoning or calculation.
""",

        "Long Answer":"""
LONG ANSWER RULES
- Generate a question requiring a detailed explanation, derivation, multi-step calculation, analysis or structured response.
- The question should justify the marks assigned.
- Include sufficient context, data and conditions for a complete answer.
- The expected answer should require multiple logically connected steps or points.
- Do not generate a simple one-line factual question as a Long Answer.
- The solution must provide the major reasoning steps, derivation or explanation needed for a complete response.
"""
    }

    return rules.get(
        question_type,
        f"""
QUESTION TYPE RULES
- Generate exactly the requested question type: {question_type}.
- The question must genuinely behave as that question type.
- Do not substitute another question type.
- Ensure the question is appropriate for the requested subject, class, syllabus, difficulty and marks.
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

    if question_type == "Diagram-Based Questions":
        return {
            "error": "Diagram-Based Questions are no longer supported."
        }

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
COGNITIVE GUIDANCE FOR THIS GROUP
==================================================

The complete examination paper has a target cognitive distribution.

For this question group, use the following distribution as a strong generation
guideline:

Recall: {cognitive_allocation.get("Recall", 0)}
Understanding: {cognitive_allocation.get("Understanding", 0)}
Application: {cognitive_allocation.get("Application", 0)}
Analysis: {cognitive_allocation.get("Analysis", 0)}

Prefer these cognitive levels when creating the questions.

IMPORTANT:
- These values guide the generation of this group.
- Do not sacrifice question quality just to force an unnatural cognitive label.
- Choose the cognitive level that genuinely matches what the question requires.
- The final examination paper will be checked against the overall cognitive blueprint.

==================================================
DIFFICULTY GUIDANCE FOR THIS GROUP
==================================================

Target difficulty distribution for this group:

Easy: {difficulty_allocation.get("Easy", 0)}
Medium: {difficulty_allocation.get("Medium", 0)}
Hard: {difficulty_allocation.get("Hard", 0)}

Use these values as strong guidance while generating the group.

IMPORTANT:
- Easy questions should test straightforward knowledge or simple application.
- Medium questions should require understanding or moderate application.
- Hard questions should require deeper reasoning, multi-step work, or analysis.
- Do not artificially label a question Easy/Medium/Hard merely to satisfy a number.

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
QUESTION TYPE IS LOCKED
==================================================

You are generating ONLY this question type:

"{question_type}"

You must understand the meaning of this question type before generating.

Do not confuse it with another question type.

The question_type field MUST be exactly:
"{question_type}"

Generate exactly {question_count} questions of this type.

Each question must genuinely behave like a "{question_type}" question,
not merely have "{question_type}" written in its question_type field.

Follow the specific structure and requirements given below for this type.

==================================================
QUESTION TYPE RULES
==================================================

{question_type_rules}

==================================================
ACADEMIC QUALITY LOCK
==================================================

- Every question must directly belong to the requested subject and syllabus.
- Do not introduce concepts from another subject unless the teacher explicitly requests interdisciplinary content.
- Match the question demand to the assigned marks.
- A one-mark question must have a concise, objectively gradable response.
- Multi-step calculations, derivations, comparisons or extended reasoning must receive enough marks to justify the work.
- Verify the answer independently before returning the question.
- The solution MUST support the answer and MUST NOT contradict it.
- Recalculate every numerical answer before returning it.
- Keep wording clear, grammatical and unambiguous.
- Source-Based Questions must be answerable from their source material.
- Case Study questions must genuinely depend on their case.

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
                marks_per_question
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
You are an expert examination-paper correction engine.

The complete regeneration context, including the existing examination paper,
teacher requirements and validation feedback, is provided below.

Your task is to REPAIR the existing examination paper according to that
validation feedback.

This is a REPAIR operation, not a random regeneration operation.

Preserve everything that is already valid.

Only make changes that are necessary to resolve the identified validation
errors.

Do not randomly rewrite valid questions.

Do not weaken or ignore any validation requirement.

==================================================
REGENERATION CONTEXT
==================================================

{regeneration_prompt}

==================================================
REQUIRED QUESTION FIELDS
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

Easy
Medium
Hard

cognitive must be exactly one of:

Recall
Understanding
Application
Analysis

==================================================
QUESTION TYPE REQUIREMENTS
==================================================

MCQ:

- Include exactly four options.
- All four options must be non-empty.
- Only one option should be correct.
- The answer must be A, B, C or D.
- The answer must correspond to one of the four options.
- Options must be meaningful and plausible.
- Do not create duplicate options.

True/False:

- The question must be a clear factual statement.
- The answer must be exactly True or False.
- Do not create ambiguous statements.

Fill in the Blanks:

- The question MUST contain "______".
- The blank must test a meaningful concept.
- The answer must provide the missing word, phrase, value or expression.

Assertion-Reason:

- Include assertion.
- Include reason.
- Keep assertion and reason as separate fields.
- The assertion and reason must be logically related.
- The answer must correctly represent their relationship.

Match the Following:

- Include left_column.
- Include right_column.
- Both columns must be non-empty.
- Both columns must contain the same number of items.
- The answer must identify the correct matching pairs.

Source-Based Questions:

- Include source.
- The question must genuinely depend on the provided source.
- The source must contain sufficient information to answer the question.

Case Study:

- Include case.
- The question must genuinely depend on the case.
- The case must contain sufficient information for reasoning.

Application-based:

- The question must require application of a learned concept, principle,
  formula or method to a new situation.
- Do not turn it into a simple recall or definition question.
- The student must actually apply the concept to solve the problem.

HOTS:

- The question must require genuine higher-order reasoning.
- It should involve analysis, evaluation, interpretation, comparison,
  synthesis or non-routine reasoning.
- Do not use a simple recall or direct formula-substitution question as HOTS.

One Word Answer:

- The expected answer must be one word or one concise term.
- The answer must be specific and objectively verifiable.
- Do not require a sentence or explanation as the answer.

Very Short Answer:

- The question must require a very short response.
- Do not require lengthy explanation, derivation or multi-step analysis.

Short Answer:

- The question must require a concise explanation, calculation,
  derivation, comparison or reasoning appropriate to the assigned marks.
- Do not make it a one-word question.
- Do not make it an unnecessarily long essay.

Long Answer:

- The question must require a detailed explanation, derivation,
  multi-step calculation, analysis or structured response.
- The expected response must be appropriate for the assigned marks.

==================================================
STRUCTURE PRESERVATION
==================================================

Do not change the number of sections.

Do not change section order.

Do not change section names.

Do not add sections.

Do not remove sections.

Do not add questions.

Do not remove questions.

Do not move questions between sections.

Do not change the total number of questions.

Preserve the existing question grouping.

Do not change question types unless the validation feedback explicitly
identifies a wrong question type.

Do not change valid marks.

Do not change valid section marks.

Do not change the total marks.

==================================================
VALIDATION REPAIR INSTRUCTIONS
==================================================

The previous paper failed validation.

Repair ONLY the problems identified in the validation feedback contained
in the regeneration context.

For every validation error:

1. Identify exactly what is wrong.
2. Determine the smallest necessary correction.
3. Preserve everything that is already valid.
4. Do not rewrite the entire paper unnecessarily.
5. Do not change valid section structure.
6. Do not change valid question types.
7. Do not change valid marks.
8. Do not remove valid questions.
9. Do not add extra questions.
10. Do not move questions between sections.
11. Do not unnecessarily change syllabus coverage.
12. Do not introduce new validation problems while fixing an existing problem.

==================================================
COGNITIVE BLUEPRINT REPAIR
==================================================

The cognitive distribution is validated across the COMPLETE examination paper.

Use the expected cognitive counts explicitly stated in the validation
feedback contained in the regeneration context.

For example, if validation says:

"Cognitive 'Application' mismatch: expected 8 questions, got 9"

then the final complete paper MUST contain exactly 8 Application questions.

If validation says:

"Cognitive 'Analysis' mismatch: expected 4 questions, got 5"

then the final complete paper MUST contain exactly 4 Analysis questions.

Apply the same rule to:

- Recall
- Understanding
- Application
- Analysis

Do NOT invent target counts.

Do NOT use different target counts.

Do NOT simply change cognitive labels only to manipulate the count.

The cognitive level must genuinely match the question.

When repairing the cognitive distribution:

- Prefer changing an existing suitable question when possible.
- Only change its cognitive level when the question genuinely supports it.
- If necessary, rewrite the smallest number of questions.
- Keep question type unchanged.
- Keep marks unchanged.
- Keep section unchanged.
- Keep total question count unchanged.
- Preserve syllabus relevance.

The final COMPLETE paper must satisfy the cognitive distribution required
by the validation feedback.

==================================================
DIFFICULTY REPAIR
==================================================

If validation feedback identifies a difficulty distribution problem:

- Repair the difficulty distribution across the COMPLETE paper.
- Preserve question type.
- Preserve marks.
- Preserve section.
- Do not change difficulty merely to manipulate counts.
- The assigned difficulty must genuinely match the question.
- Use the expected counts explicitly stated in the validation feedback.
- Do not invent target counts.

==================================================
DUPLICATE REPAIR
==================================================

If duplicate validation identifies a duplicate question:

- Replace only the duplicated question.
- Generate a genuinely different question.
- Preserve the same section.
- Preserve the same question type.
- Preserve the same marks.
- Preserve syllabus relevance.
- Preserve the intended learning objective.
- Do not merely change names, values or wording while keeping essentially
  the same question.

==================================================
SIMILARITY REPAIR
==================================================

If similarity validation identifies excessive similarity:

- Rewrite or replace only the affected question.
- Preserve the same section.
- Preserve the same question type.
- Preserve the same marks.
- Preserve the intended learning objective.
- Use substantially different wording and question construction.
- Do not copy the structure of the reference question.

==================================================
CONTENT AND QUALITY REPAIR
==================================================

For every question that is modified:

- Ensure it is factually correct.
- Ensure it is grammatically correct.
- Ensure it is clear and unambiguous.
- Ensure it is appropriate for the subject and class.
- Ensure it is syllabus relevant.
- Ensure the answer is correct.
- Ensure the solution matches the answer.
- Ensure the question type is genuine.
- Ensure the difficulty is appropriate.
- Ensure the cognitive level genuinely matches the question.

==================================================
FINAL VALIDATION CHECK
==================================================

Before returning the paper, internally verify all of the following:

1. A complete "sections" array exists.

2. The number of sections is unchanged.

3. Section order is unchanged.

4. Section names are unchanged.

5. Every section contains the correct number of questions.

6. The total number of questions is unchanged.

7. Every question has the correct question_type.

8. Every question has the correct marks.

9. Section marks are correct.

10. Total marks are correct.

11. Every question has a valid difficulty:
    Easy
    Medium
    Hard

12. Every question has a valid cognitive level:
    Recall
    Understanding
    Application
    Analysis

13. The COMPLETE paper satisfies the cognitive counts required by the
    validation feedback.

14. If difficulty-count errors were reported, the COMPLETE paper satisfies
    the required difficulty counts.

15. MCQs contain exactly four options.

16. MCQ answers are A, B, C or D.

17. True/False answers are True or False.

18. Fill in the Blanks contain "______".

19. Assertion-Reason contains separate assertion and reason fields.

20. Match the Following contains non-empty equal-length columns.

21. Source-Based Questions contain source.

22. Case Study questions contain case.

23. Application-based questions genuinely require application.

24. HOTS questions genuinely require higher-order reasoning.

25. One Word Answer questions have concise one-word or one-term answers.

26. Very Short Answer questions are appropriately concise.

27. Short Answer questions are appropriate for their marks.

28. Long Answer questions are appropriate for their marks.

29. No duplicate questions remain.

30. No unresolved validation problems remain.

31. Every question has a valid answer.

32. Every question has a valid solution.

33. The complete paper remains academically correct.

34. The complete paper remains syllabus relevant.

==================================================
FINAL OUTPUT
==================================================

Repair the paper according to the validation feedback.

Preserve all valid content.

Make the smallest necessary corrections.

Do not reduce validation requirements.

Do not fabricate a successful result.

The final paper must be a COMPLETE repaired examination paper.

Return ONLY valid JSON.

Do not return explanations.

Do not return comments.

Do not return markdown.

Do not return validation messages.

Do not return analysis.

Do not return apologies.

Return ONLY the complete repaired examination paper as JSON.
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