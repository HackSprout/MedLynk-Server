from fastapi import APIRouter
from app.memory.session_store import get_chat_history, append_to_history
from app.services.llm import ask_gemini

router = APIRouter()

@router.post("/chat/{chat_id}")
async def chat(chat_id: str, user_msg: str):
    append_to_history(chat_id, "user", user_msg)
    history = get_chat_history(chat_id)
    response = ask_gemini(history)
    append_to_history(chat_id, "model", response)
    return {"response": response}
