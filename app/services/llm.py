import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def ask_gemini(messages: list[dict]) -> str:
    chat = model.start_chat(history=messages)
    response = chat.send_message(messages[-1]['parts'][0])
    return response.text
