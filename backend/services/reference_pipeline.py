from backend.services.pdf_parser import extract_text_from_pdf
from backend.services.question_blueprint import create_question_blueprint
from backend.services.question_intelligence import enrich_blueprint
from backend.services.style_extractor import extract_style
from backend.services.reference_repository import save_blueprint
from backend.metadata_engine.metadata_engine import generate_metadata


def process_reference_paper(pdf_path, exam_type, subject):
    
    #Extracting Text
    text= extract_text_from_pdf(pdf_path)

    #Creating Question Blueprint
    blueprint= create_question_blueprint(text)

    #Question Intelligence
    blueprint= enrich_blueprint(blueprint)

    #Metadata Engine
    blueprint= generate_metadata(blueprint)

    #Style Extraction
    for question in blueprint["questions"]:
        extract_style(question)

    #Saving Blueprint/Repository
    save_blueprint(
        blueprint,
        exam_type,
        subject
    )

    return blueprint
