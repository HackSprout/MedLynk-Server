TOKEN_LIMIT = 1000000 
chat_sessions = {}

def get_token_length(message: dict) -> int:
    length = len(str(message)) // 4
    print(f"[DEBUG] Calculated token length: {length} for message: {message}")
    return length

def get_chat_history(chat_id: str) -> list:
    history = chat_sessions.get(chat_id, [])
    return history

def append_to_history(chat_id: str, role: str, content: str):
    
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []

    new_message = {"role": role, "parts": [content]}
    chat_sessions[chat_id].append(new_message)
    total_tokens = sum(get_token_length(msg) for msg in chat_sessions[chat_id])
    print(f"[DEBUG] Total tokens after append: {total_tokens} (limit: {TOKEN_LIMIT})")

    while total_tokens > TOKEN_LIMIT and len(chat_sessions[chat_id]) > 1:
        removed = chat_sessions[chat_id].pop(1)
        print(f"[DEBUG] Removed message due to token limit: {removed}")
        total_tokens = sum(get_token_length(msg) for msg in chat_sessions[chat_id])
        print(f"[DEBUG] New total tokens: {total_tokens}")
