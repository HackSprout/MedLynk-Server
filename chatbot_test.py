# chatbot_test.py

from app.services.llm import ask_gemini
from app.services.pdf_parser import parse_all_pdfs
from app.services.calendly import book_real_appointment

def extract_time_from_text(text):
    # 🕒 Simplistic matching
    if "3" in text:
        return "3:00 PM"
    elif "4" in text:
        return "4:00 PM"
    elif "5" in text:
        return "5:00 PM"
    else:
        return None

# 🔥 Hardcoded available times mapped to ISO8601 format (Calendly needs this)
available_times = {
    "3:00 PM": "2025-04-05T15:00:00Z",
    "4:00 PM": "2025-04-05T16:00:00Z",
    "5:00 PM": "2025-04-05T17:00:00Z"
}

if __name__ == "__main__":
    # 📂 Step 1: Parse ALL PDFs
    parsed_text = parse_all_pdfs("static")

    # 🧠 Step 2: Inject medical records into chat history
    chat_history = [
        {"role": "user", "parts": [f"Here are my combined medical records:\n{parsed_text}"]},
        {"role": "model", "parts": ["Understood. I'll use these records to answer your questions."]}
    ]

    print("Welcome to Sched AI! All medical records are loaded. Type 'exit' to leave.\n")

    in_booking_mode = False

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # 📅 Booking Intent Detection
        booking_keywords = ["appointment", "book", "schedule", "meeting"]
        if any(word in user_input.lower() for word in booking_keywords):
            in_booking_mode = True

        if in_booking_mode:
            print("Sched AI: Available times are:")
            for time_str in available_times.keys():
                print(f"- {time_str}")

            user_input = input("Pick a time: ")

            selected_time_iso = available_times.get(user_input.strip())

            if not selected_time_iso:
                print("Sched AI: I didn't understand that time. Please type exactly like '3:00 PM'.\n")
                continue

            # 🧠 Fake static patient info for now
            invitee_email = "tintinsri571@gmail.com"
            invitee_name = "Sri Tintin"

            success = book_real_appointment(
                invitee_email=invitee_email,
                invitee_name=invitee_name,
                start_time_iso=selected_time_iso
            )

            if success:
                print(f"Sched AI: ✅ Your appointment at {user_input} has been booked!\n")
            else:
                print(f"Sched AI: ❌ Sorry, the time {user_input} is no longer available. Try another one.\n")

            in_booking_mode = False
            continue  # Skip sending booking text to Gemini

        # 🧠 Regular conversation with Gemini
        chat_history.append({"role": "user", "parts": [user_input]})

        try:
            bot_response = ask_gemini(chat_history)
        except Exception as e:
            print("Error talking to Gemini:", e)
            continue

        chat_history.append({"role": "model", "parts": [bot_response]})
        print(f"Sched AI: {bot_response}\n")
