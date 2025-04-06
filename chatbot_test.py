# chatbot_test.py

import os
from dotenv import load_dotenv
from app.services.llm import ask_gemini
from app.services.pdf_parser import parse_all_pdfs
from app.services.calendly import create_scheduling_link

load_dotenv()

def extract_time_from_text(text):
    if "3" in text:
        return "3:00 PM"
    elif "4" in text:
        return "4:00 PM"
    elif "5" in text:
        return "5:00 PM"
    else:
        return None

available_times = ["3:00 PM", "4:00 PM", "5:00 PM"]

if __name__ == "__main__":
    parsed_text = parse_all_pdfs("static")

    chat_history = [
        {"role": "user", "parts": [f"Here are my combined medical records:\n{parsed_text}"]},
        {"role": "model", "parts": ["Understood. I'll use these records to answer your questions."]}
    ]

    print("Welcome to MedLynk AI! Type 'exit' to leave.\n")

    in_booking_mode = False

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        booking_keywords = ["appointment", "book", "schedule", "meeting"]
        if any(word in user_input.lower() for word in booking_keywords):
            in_booking_mode = True

        if in_booking_mode:
            print("MedLynk AI: Available times are:")
            for time_str in available_times:
                print(f"- {time_str}")

            user_input = input("Pick a time: ")

            if user_input.strip() not in available_times:
                print("MedLynk AI: I didn't understand that time. Please type exactly like '3:00 PM'.\n")
                continue

            # Now, create a scheduling link
            link = create_scheduling_link()

            if link:
                print(f"MedLynk AI: ✅ You can book your appointment here: {link}\n")
            else:
                print(f"MedLynk AI: ❌ Booking failed. Try again later.\n")

            in_booking_mode = False
            continue  # skip Gemini chat

        # regular Gemini conversation
        chat_history.append({"role": "user", "parts": [user_input]})

        try:
            bot_response = ask_gemini(chat_history)
        except Exception as e:
            print("Error talking to Gemini:", e)
            continue

        chat_history.append({"role": "model", "parts": [bot_response]})
        print(f"MedLynk AI: {bot_response}\n")
