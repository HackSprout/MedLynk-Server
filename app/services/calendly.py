# app/services/calendly.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
CALENDLY_USER_URI = os.getenv("CALENDLY_USER_URI")
CALENDLY_EVENT_TYPE_URI = os.getenv("CALENDLY_EVENT_TYPE_URI")

print(f"[DEBUG] Loaded Calendly API Key: {CALENDLY_API_KEY}")

def create_scheduling_link():
    url = "https://api.calendly.com/scheduling_links"
    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "owner": CALENDLY_EVENT_TYPE_URI,  
        "max_event_count": 1,
        "owner_type": "EventType"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        scheduling_link = response.json()["resource"]["booking_url"]
        return scheduling_link
    else:
        print(f"Failed to create scheduling link. Status: {response.status_code}, Response: {response.text}")
        return None
