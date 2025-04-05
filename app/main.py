from fastapi import FastAPI
from app.routes import chat, upload

app = FastAPI()

app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
