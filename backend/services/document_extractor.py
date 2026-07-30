from pathlib import Path
import fitz
from docx import Document

def extract_pdf_text(file_path: Path):
    document= fitz.open(file_path)

    pages= []
    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages)

def extract_docx_text(file_path: Path):
    document= Document(file_path)

    paragraphs= []

    for paragraph in document:
        paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)

def extract_text(file_path: Path):
    extension= file_path().suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError(
        "Unsupported document format."
    )