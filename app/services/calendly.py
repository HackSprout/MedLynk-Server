# app/services/calendly.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
print(f"[DEBUG] Loaded Calendly API Key: {CALENDLY_API_KEY}")
# This is YOUR event link (where bookings will happen)
EVENT_TYPE_URI = "https://api.calendly.com/event_types/39b1b552-bd46-4d9e-ba75-5ce78f295896"

# Doctor info (static for now)
DOCTOR_NAME = "Doctor Huang"
DOCTOR_EMAIL = "jasonboe510@gmail.com"

def book_real_appointment(invitee_email, invitee_name, start_time_iso):
    """Book an appointment via Calendly API."""
    url = "https://api.calendly.com/scheduled_events"

    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "event_type": EVENT_TYPE_URI,
        "invitees": [
            {
                "email": invitee_email,
                "name": invitee_name
            }
        ],
        "start_time": start_time_iso,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        return True
    else:
        print(f"❌ Booking Failed. Status: {response.status_code}, Response: {response.text}")
        return False
