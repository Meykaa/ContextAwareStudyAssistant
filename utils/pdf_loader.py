from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    return text.strip()
