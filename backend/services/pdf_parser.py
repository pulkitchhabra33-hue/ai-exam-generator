import fitz

def extract_text_from_pdf(file_path):
    text= ""

    try:     
        doc= fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()

    except Exception as e:
        print("PDF read error:", e)
        
    return text