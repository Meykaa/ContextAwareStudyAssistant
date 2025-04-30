from docx import Document

def extract_text_from_docx(file_path):
    """Extract text from a Word document (.docx)."""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"
