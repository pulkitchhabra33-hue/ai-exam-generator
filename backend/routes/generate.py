from fileinput import filename
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
import json
from pydantic import BaseModel
from backend.services.ai_service import generate_paper
from backend.services.pdf_service import generate_pdf
import os

router= APIRouter()
class PaperRequest(BaseModel):

    exam_type: str | None = None
    school_name: str | None = None
    exam_name: str | None = None
    time_limit: str | None = None
    
    class_name: str
    subject: str
    topics: str
    difficulty: str

    total_marks: int | None= None

    section_a: int | None= None
    section_b: int | None= None
    section_c: int | None= None

    type_a: str | None = None
    type_b: str | None = None
    type_c: str | None = None
    
    questions_a: int | None= None
    questions_b: int | None= None
    questions_c: int | None= None

    instructions: str | None= None
    student_performance: str | None= None


@router.post("/generate-paper")
def generate_exam_paper(data: str = Form(...), files: List[UploadFile] = File([]), include_answers: bool = True):
    data_dict= json.loads(data)
    data= PaperRequest(**data_dict)
    upload_folder= "backend/uploads"

    os.makedirs(upload_folder, exist_ok= True)
    saved_files= []

    for file in files:
        file_path= os.path.join(upload_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        saved_files.append(file_path)
    
    print("Saved Files:", saved_files)

    paper = generate_paper(data)

    paper["school_name"]= data.school_name
    paper["exam_name"]= data.exam_name
    paper["class_name"]= data.class_name
    paper["subject"]= data.subject
    paper["time_limit"]= data.time_limit
    paper["total_marks"]= data.total_marks
    paper["exam_type"]= data.exam_type

    print("PAPER DATA:", paper)

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
    file_path = os.path.join("backend", "pdfs", filename)
    print("Download Path:", file_path)

    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(path= file_path, media_type= 'application/pdf', filename= filename)