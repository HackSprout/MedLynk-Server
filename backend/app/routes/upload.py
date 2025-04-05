from fastapi import APIRouter, UploadFile, File
from app.services.pdf_parser import extract_text_from_pdf
import os

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"static/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)
    return {"parsed_text": text}
