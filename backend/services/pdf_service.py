from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import datetime

def generate_pdf(data, filename= "paper.pdf", include_answers= True):

    # Creating unique filename
    if not filename:
        timestamp= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename= f"paper_{timestamp}.pdf"

    # Create folder
    folder= "backend/pdfs"
    os.makedirs(folder, exist_ok= True)

    filepath= os.path.join(folder, filename)
    doc= SimpleDocTemplate(filepath)

    styles= getSampleStyleSheet()

    # Custom style for better spacing
    question_style= ParagraphStyle(
        'QuestionStyle',
        parent= styles['Normal'],
        spaceAfter= 8,
    )

    elements= []

    # Title
    elements.append(Paragraph(data.get("title", "Exam Paper"), styles["Title"]))
    elements.append(Spacer(1,12))

    # Instructions
    elements.append(Paragraph("Instructions:", styles["Heading2"]))
    for inst in data.get("instructions", []):
        elements.append(Paragraph(f"• {inst}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Sections + Questions (GLOBAL numbering)
    question_counter = 1
    for section in data.get("sections", []):
        elements.append(Paragraph(section.get("name", ""), styles["Heading2"]))
        elements.append(Spacer(1, 8))

        for q in section.get("questions", []):
            question_text= f"<b>{question_counter}.</b> {q.get('question')} ({q.get('marks')} marks)"
            elements.append(Paragraph(question_text, question_style))

            # MCQ options support
            options= q.get("options", [])
            
            if options:
                for opt in options:
                    elements.append(Paragraph(f"- {opt}", styles["Normal"]))
                elements.append(Spacer(1, 6))

            question_counter += 1
        
        elements.append(Spacer(1, 12))

    # Answer Key (Optional)
    if include_answers:
        elements.append(Paragraph("Answer Key:", styles["Heading2"]))

        counter = 1
        for section in data.get("sections", []):
            for q in section.get("questions", []):
                ans= q.get("answer", "")
                elements.append(Paragraph(f"{counter}. {ans}", styles["Normal"]))
                counter += 1

        elements.append(Spacer(1, 12))
    
    # Solutions (OPTIONAL)

    if include_answers:
        elements.append(Paragraph("Solutions:", styles["Heading2"]))

        counter = 1
        for section in data.get("sections", []):
            for q in section.get("questions", []):
                sol = q.get("solution", "")
                elements.append(Paragraph(f"{counter}. {sol}", styles["Normal"]))
                elements.append(Spacer(1, 6))
                counter += 1

    doc.build(elements)

    

    try:
        doc.build(elements)
    except Exception as e:
        print("Error building PDF:", e)
        raise

    return filepath