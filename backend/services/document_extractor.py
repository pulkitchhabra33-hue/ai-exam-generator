from pathlib import Path
import fitz
from docx import Document
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

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

def extract_image_text(file_path: Path):
    image= Image.open(file_path)

    text= pytesseract.image_to_string(
        image,
        lang= "eng"
    ).strip()

    if not text:
        raise ValueError(
            "No readable text was found in the image."
        )

    return text

def extract_image_text(file_path: Path):

    image = Image.open(file_path)

    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return text

def extract_text(file_path: Path):
    extension= file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    elif extension in [".jpg", ".jpeg", ".png"]:
        return extract_image_text(file_path)

    raise ValueError(
        "Unsupported document format."
    )