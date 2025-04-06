from app.memory.session_store import get_chat_history, append_to_history
from app.services.llm import ask_gemini

from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route("/<chat_id>", methods=['POST'])
def chat(chat_id):
   

    data = request.get_json()
    user_msg = data.get("message")


    if not user_msg:
        return jsonify({"error": "Missing 'message' in request body"}), 400
    

    append_to_history(chat_id, "user", user_msg)
    history = get_chat_history(chat_id)
    response = ask_gemini(history)
    append_to_history(chat_id, "model", response)
    return jsonify({"response": response})
