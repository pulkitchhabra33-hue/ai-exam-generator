from fastapi import APIRouter, HTTPException
from backend.services.paper_service import create_exam_paper
from backend.schemas.request_models import TeacherRequest
from backend.schemas.response_models import GenerationResponse
from backend.api.response_builder import (
    success_response, error_response
)

router= APIRouter()

@router.post("/generate-paper", 
    response_model= GenerationResponse, 
    response_model_exclude_none=True,
    summary= "Generate AI Exam Paper",
    description= """
Generate a complete exam paper using the AI Generation Pipeline.

The pipeline automatically:

- Builds prompts
- Retrieves reference papers
- Generates questions
- Validates the paper
- Performs regeneration if required
- Calculates quality score
- Returns the final paper
""",
    tags= ["Exam Generator"],
    responses= {
        200: {
            "description": "Paper generated successfully."
        },

        422: {
            "description": "Invalid teacher request."
        },

        500: {
            "description": "Internal generation error."
        }
    }
)

def generate(teacher_data: TeacherRequest):
    result= create_exam_paper(teacher_data.model_dump())

    if not result["success"]:
        raise HTTPException(
            status_code= 500,
            detail= error_response(
                "Paper generation failed."
            )
        )
    
    return success_response(
        result,
        "Paper generated successfully."
    )