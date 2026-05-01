from fileinput import filename
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services.ai_service import generate_paper
from backend.services.pdf_service import generate_pdf
import os

router= APIRouter()
class PaperRequest(BaseModel):
    class_name: str
    subject: str
    topics: str
    difficulty: str

    total_marks: int | None= None

    section_a: int | None= None
    section_b: int | None= None
    section_c: int | None= None
    
    questions_a: int | None= None
    questions_b: int | None= None
    questions_c: int | None= None

    instructions: str | None= None
    student_performance: str | None= None


@router.post("/generate-paper")
def generate_exam_paper(data: PaperRequest, include_answers: bool = True):
    paper = generate_paper(data)

    if "error" in paper:
        return paper
    
    file_path = generate_pdf(paper, include_answers= include_answers)
    print("Generated PDF:", file_path)

    filename = file_path.split("/")[-1]

    

    return {
        "message" : "PDF generated successfully",
        "download_url": f"/download/{filename}"
    }
 

@router.post("/generate-pdf")
def create_pdf(data: PaperRequest):
    paper= generate_paper(data)
    
    if "error" in paper:
        return paper
    
    file_path= generate_pdf(paper)

    return {
        "message": "PDF generated successfully",
        "file": file_path
    }


@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"backend/pdfs/{filename}"

    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(file_path, media_type= 'application/pdf', filename= filename)