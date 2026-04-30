import json
from openai import OpenAI
import os

client= OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

def format_instructions(text):
    if not text or not text.strip():
        return ["No special instructions"]
    
    lines= text.split("\n")
    return [line.strip().capitalize() for line in lines if line.strip()]

def instructions_to_text(instructions_list):
    return "\n".join(f"- {i}" for i in instructions_list)

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

    prompt= f"""
    Generate a structured exam paper in JSON format.

    Class: {data.class_name}
    Subject: {data.subject}
    Topics: {data.topics}
    Difficulty Level: {data.difficulty}

    Total Marks: {data.total_marks if data.total_marks else "auto"}

    Section Distribution:
    {section_data}

    Instructions:
    {instructions}

    JSON Format:
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

    STRICT RULES:
    - Total marks MUST equal the sum of marks of all questions
    - Section marks MUST match the given distribution
    - Number of questions per section MUST match exactly
    - Each question MUST have the specified marks
    - Do NOT skip any section
    - Do NOT add extra sections
    - Ensure consistent formatting
    - Return ONLY valid JSON
    """

    response= client.chat.completions.create(
        model= "gpt-4o-mini",
        response_format= {"type": "json_object"},
        messages= [{"role": "user", "content": prompt}]
    )

    content= response.choices[0].message.content

    try:
        parsed= json.loads(content)

        if warning:
            parsed["warning"] = warning

        return parsed
    
    except Exception as e:
        return {
            "error": "Invalid JSON from AI",
            "details": str(e),
            "raw_response": content
        }