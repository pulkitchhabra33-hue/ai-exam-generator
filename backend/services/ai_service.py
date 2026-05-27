import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client= OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

def format_instructions(text):
    default_instruction= "Attempt all questions."
    
    if not text or not text.strip():
        return [default_instruction]

    lines= text.split("\n")
    cleaned= []

    for line in lines:
        line= line.strip()

        if not line:
            continue

        line= line.replace("..", ".")

        line= line[0].upper() + line[1:] if len(line) > 1 else line.upper()

        if not line.endswith((".", "?", "!")):
            line += "."

        cleaned.append(line)

    lower_cleaned= [x.lower() for x in cleaned]
        
    if "attempt all questions" not in lower_cleaned:
        cleaned.append(default_instruction)
    return cleaned

def instructions_to_text(instructions_list):
    return "\n".join(f"- {i}" for i in instructions_list)

json_format = """
{
  "title": "Exam Title",
  "instructions": ["point1", "point2"],
  "sections": [
    {
      "name": "Section A",
      "questions": [
        {
          "question": "text",
          "marks": 2,
          "answer": "text",
          "solution": "text"
        }
      ]
    }
  ]
}
"""

def generate_paper(data):

    warning= None
    print("Incoming Request:", data)

    if data.total_marks:
        total= data.total_marks

        if data.section_a or data.section_b or data.section_c:
            a= data.section_a or 0
            b= data.section_b or 0
            c= data.section_c or 0

            if (a+b) > total:
                return {
                    "error": "Section (A+B) marks exceed total marks",
                    "details": f"A({a}) + B({b}) > Total({total})"
                }
            
            # ✅ adjust C safely
            c= total - (a+b) 

            if (a+b+c) != total:
                warning= "Section marks adjusted to fit total marks."
        else:
            a= int(total * 0.3)
            b= int(total * 0.3)
            c= total - (a+b)

        qa= data.questions_a if data.questions_a and data.questions_a > 0 else 1
        qb= data.questions_b if data.questions_b and data.questions_b > 0 else 1
        qc= data.questions_c if data.questions_c and data.questions_c > 0 else 1

        marks_a= round(a / qa, 2) if data.total_marks else "auto"
        marks_b= round(b / qb, 2) if data.total_marks else "auto"
        marks_c= round(c / qc, 2) if data.total_marks else "auto"

        section_data= f"""
            Section A: {a} marks, {qa} questions, {marks_a} marks per question
            Section B: {b} marks, {qb} questions, {marks_b} marks per question
            Section C: {c} marks, {qc} questions, {marks_c} marks per question
        """
    else:
        section_data= "Use standard exam pattern"

    instructions_list= format_instructions(data.instructions)
    instructions= instructions_to_text(instructions_list)

    exam_type= data.exam_type if data.exam_type else "General Exam Paper"

    section_types = f'''
    Section A Type: {data.type_a}
    
    Section B Type: {data.type_b}
    
    Section C Type: {data.type_c}

'''
    prompt = f"""
    You are an expert academic exam paper setter and assessment designer.

    Your task is to create a highly professional, realistic, well-structured, and board-style exam paper in STRICT JSON format.

    You must behave like an experienced teacher and paper setter.

    --------------------------------------------------
    EXAM DETAILS
    --------------------------------------------------

    School Class:
    {data.class_name}

    Subject:
    {data.subject}

    Topics:
    {data.topics}

    Difficulty Level:
    {data.difficulty}

    Exam Type:
    {exam_type}

    Total Marks:
    {data.total_marks if data.total_marks else "Auto"}

    Section Distribution:
    {section_data}

    Section Question Types:
    {section_types}

    Instructions:
    {instructions}

    --------------------------------------------------
    EXAM GENERATION BEHAVIOR
    --------------------------------------------------

    If Exam Type is provided:

    - Generate the paper in the style, tone, structure, and difficulty level commonly seen in that examination.

    - Behave like a real exam paper setter for that exam.

    - Use realistic wording and professional educational language.

    - Follow common patterns used in official exams.

    Examples:

    CBSE:
    - Competency-based questions
    - Case-study questions
    - NCERT-oriented style
    - Balanced conceptual difficulty

    ICSE:
    - Theory-rich descriptive questions
    - Detailed analytical writing
    - Formal school-exam style

    JEE:
    - Conceptual and application-based problems
    - Multi-step problem solving
    - Higher-order thinking

    NEET:
    - Biology and science-oriented MCQs
    - Assertion-reason questions
    - Medical entrance style

    SSC:
    - Objective and direct questions
    - Practical and scoring-oriented pattern

    --------------------------------------------------
    IMPORTANT INTELLIGENCE RULES
    --------------------------------------------------

    If Previous Year Papers are NOT uploaded:

    - Infer the likely style of the selected exam type.
    - Generate questions similar to official papers.
    - Use realistic exam patterns.

    If Previous Year Papers ARE uploaded:

    - Use them as reference material.
    - Analyze:
    - question style
    - marks distribution
    - section structure
    - wording style
    - exam difficulty
    - question patterns

    - Then generate a paper inspired by those patterns.

    --------------------------------------------------
    QUESTION QUALITY RULES
    --------------------------------------------------

    IMPORTANT REALISM RULES:

    - Questions should feel like real school or competitive exam papers.

    - Avoid extremely direct textbook-definition questions unless necessary.

    - Prefer:
      - scenario-based wording
      - application-based thinking
      - competency-focused questions
      - analytical reasoning

    - Questions should test understanding, not memorization only.

    - Use natural teacher-style wording.

    - Make the paper feel human-created and professionally designed.

    Generate professional-quality questions.

    Avoid:
    - generic questions
    - repetitive wording
    - vague questions
    - extremely easy repeated textbook questions

    Prefer:
    - realistic exam language
    - meaningful concepts
    - application-based thinking
    - conceptual clarity

    --------------------------------------------------
    QUESTION TYPE RULES
    --------------------------------------------------

    Respect the selected section question types.

    Examples:

    - If section type is MCQ:
    generate objective questions with options.

    - If section type is Case Study:
    generate scenario-based questions.

    - If section type is Assertion-Reason:
    generate assertion and reasoning style questions.

    - If section type is Application Based:
    generate real-life application questions.

    - If section type is Long Answer:
    generate analytical descriptive questions.

    Use suitable combinations of:

    - MCQs
    - Short answer questions
    - Long answer questions
    - Assertion-reason questions
    - Case-study questions
    - HOTS questions
    - Application-based questions

    where appropriate.

    --------------------------------------------------
    DIFFICULTY DISTRIBUTION
    --------------------------------------------------

    Maintain balanced difficulty:

    - 30% Easy
    - 50% Medium
    - 20% Hard

    The paper should feel realistic and properly balanced.

    --------------------------------------------------
    STRICT STRUCTURE RULES
    --------------------------------------------------

    - Total marks MUST equal the sum of all question marks.
    - Section marks MUST match the provided section distribution.
    - Number of questions per section MUST match exactly.
    - Every question MUST contain:
    - question
    - marks
    - answer
    - solution

    - Do NOT skip sections.
    - Do NOT create extra sections.
    - Maintain consistent formatting.

    --------------------------------------------------
    OUTPUT FORMAT
    --------------------------------------------------

    Return ONLY valid JSON.

    JSON Structure:
    {json_format}

    Do NOT return explanations.
    Do NOT return markdown.
    Do NOT return plain text.
    Only return valid JSON.
"""
    response= client.chat.completions.create(
        model= "gpt-4o-mini",
        response_format= {"type": "json_object"},
        messages= [{"role": "user", "content": prompt}]
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

        if warning:
            parsed["warning"] = warning

        return parsed

    except Exception as e:
        return {
            "error": "Invalid JSON from AI",
            "details": str(e),
            "raw_response": content
        }