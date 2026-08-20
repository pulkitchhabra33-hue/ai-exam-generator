from pathlib import Path
import shutil
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_FOLDER= Path("backend/uploads/temp")

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS= {
    ".pdf", 
    ".docx",
    ".jpg",
    ".jpeg",
    ".png"
}

MAX_FILE_SIZE= 10*1024*1024   # 10 MB

def validate_file(file: UploadFile):
    extension= Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"{file.filename}: Unsupported file type."
        )

def save_uploaded_file(file: UploadFile):
    validate_file(file)

    extension= Path(
        file.filename or ""
    ).suffix.lower()

    unique_name= (f"{uuid4()}{extension}")
    destination= (
        UPLOAD_FOLDER/
        unique_name
    )

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    path= destination
    check_file_size(path)

    return path

def check_file_size(path: Path):
    size= path.stat().st_size

    if size > MAX_FILE_SIZE:
        path.unlink(missing_ok=True)

        raise ValueError("File exceeds 10 MB.")