from openai import OpenAI
import os

client= OpenAI(
    api_key= os.getenv("OPENAI_API_KEY")
)

def analyze_reference_paper(pdf_text):
    prompt = f"""
You are an examination analyst.

Analyze this paper and return ONLY a structured summary.

Paper:

{pdf_text[:8000]}

Extract:

1. Exam Type
2. Section Structure
3. Question Types
4. Difficulty Distribution
5. Marks Distribution
6. Competency-Based Level
7. Case-Based Questions Present? (Yes/No)
8. Assertion-Reason Present? (Yes/No)
9. Language Style
10. Important Observations

Return concise text.
"""

    response= client.chat.completions.create(
        model= "gpt-4o-mini",
        messages= [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content 