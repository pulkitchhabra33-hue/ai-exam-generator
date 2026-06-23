from fileinput import filename
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse

from typing import List
import json
from pydantic import BaseModel

from backend.services.ai_service import generate_paper
from backend.services.pdf_service import generate_pdf
from backend.services.pdf_parser import extract_text_from_pdf
from backend.services.pattern_analyzer import analyze_reference_paper
from backend.auth import get_current_user
from backend.database import SessionLocal
from backend.models import User, PaperHistory

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

    sections: list | None= None

    instructions: str | None= None
    student_performance: str | None= None


@router.post("/generate-paper")
def generate_exam_paper(data: str = Form(...), 
    files: List[UploadFile] = File([]), 
    include_answers: bool = True,
    current_user= Depends(get_current_user)):
    
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

    uploaded_content= ""
    for file_path in saved_files:
        if file_path.lower().endswith(".pdf"):
            uploaded_content += (
                extract_text_from_pdf(file_path) + "\n\n"
            )

            pattern_summary= ""

            if uploaded_content.strip():
                pattern_summary= (
                    analyze_reference_paper
                    (uploaded_content)
                    )
                
                print("Pattern Summary:", pattern_summary)
                

    print("\n========== PDF CONTENT ==========\n")
    print(uploaded_content[:1000])
    print("\n===============================\n")


    paper= generate_paper(
        data, 
        uploaded_content= uploaded_content,
        pattern_summary= pattern_summary
        )
    
    print("Saved Files:", saved_files)
    
    # Check free generation limit for the user
    db = SessionLocal()
    db_user= db.query(User).filter(User.id == current_user.id).first()

    if db_user.credits_remaining <= 0:
        raise HTTPException(status_code= 403, detail= "No credits remaining. Please upgrade your plan.")
    
    # Generate paper using AI
    # paper= generate_paper(data)


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

    #Decrease user credits
    db_user.credits_remaining -= 1
    db.commit()
    db.refresh(db_user)

    print("Generated PDF:", file_path)

    filename = file_path.split("/")[-1]

    #Save Paper History
    history= PaperHistory(
        user_id= current_user.id,
        exam_name= data.exam_name,
        subject= data.subject,
        exam_type= data.exam_type,
        pdf_path= filename
    )

    db.add(history)
    db.commit()

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