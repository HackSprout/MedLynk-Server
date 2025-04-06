from app.services.pdf_parser import extract_text_from_pdf

pdf_path = "static/2024_ovrreport_jasonboenjamin.pdf"

parsed_text = extract_text_from_pdf(pdf_path)

print(parsed_text[:2000])  