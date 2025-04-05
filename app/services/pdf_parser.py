import os
import fitz  # PyMuPDF

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_all_pdfs(directory="static"):
    full_text = ""
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            print(f"Parsing {file_path}...")
            full_text += parse_pdf(file_path) + "\n\n"
    return full_text
