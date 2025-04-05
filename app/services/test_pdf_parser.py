from app.services.pdf_parser import extract_text_from_pdf

# Path to the PDF you uploaded
pdf_path = "static/2024_ovrreport_jasonboenjamin.pdf"

parsed_text = extract_text_from_pdf(pdf_path)

# Print only part of it to avoid massive output
print(parsed_text[:2000])  # print first 2000 characters
