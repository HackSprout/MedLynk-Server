# In-memory chat store: chat_id -> list of messages
chat_sessions = {}

def get_chat_history(chat_id: str) -> list:
    return chat_sessions.get(chat_id, [])

def append_to_history(chat_id: str, role: str, content: str):
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []
    chat_sessions[chat_id].append({"role": role, "parts": [content]})
