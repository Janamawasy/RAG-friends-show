from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file and return as a string.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    text = text.replace("\n", " ")
    return text