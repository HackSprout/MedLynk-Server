import os
import requests
from dotenv import dotenv_values
from flask import Blueprint, request, jsonify
from cryptography.fernet import InvalidToken
from app.services.secure_file import encrypt_token, decrypt_token

oauth_bp = Blueprint('oauth', __name__, url_prefix='/api/oauth')

STATIC_FOLDER = 'static'

dotenv_vars = dotenv_values(".env")

key = dotenv_vars.get('SECURITY_KEY')


@oauth_bp.route('/', methods=['GET'])
def oauth_callback():
    code = request.args.get('code')

    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    token_url = "https://auth.calendly.com/oauth/token"
    
    response = requests.post(token_url, json={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://medlynk.tech/api/oauth",
        "client_id": os.environ.get("CALENDLY_CLIENT_ID"),
        "client_secret": os.environ.get("CALENDLY_CLIENT_SECRET")
    })


    if response.status_code != 200:
        return jsonify({"error": "Tokn exchange failed", "details": response.json()} ), 400

    token_data = response.json()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    encrypted_access_token = encrypt_token(access_token, key)
    encrypted_refresh_token = encrypt_token(refresh_token, key)

    user_info_url = "https://api.calendly.com/users/me"
    user_response = requests.get(user_info_url, headers={
        "Authorization": f"Bearer {access_token}"
    })

    if user_response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info", "details": user_response.json()}), 400

    user_info = user_response.json()
    user_email = user_info['resource']['email']
    
    user_folder = os.path.join(STATIC_FOLDER, user_email)
    os.makedirs(user_folder, exist_ok=True)

    with open(os.path.join(user_folder, 'tokens.txt'), 'wb') as f:
        f.write(encrypted_access_token + b'\n')
        f.write(encrypted_refresh_token + b'\n')

    return jsonify({
        "message": "OAuth flow complete",
        "user_email": user_email
    })

def get_valid_access_token(email):
    token_path = os.path.join(STATIC_FOLDER, email, 'tokens.txt')
    print(f"[DEBUG] Looking for tokens at: {token_path}")

    if not os.path.exists(token_path):
        print(f"[ERROR] Token file not found for: {email}")
        return None, "not_found"

    try:
        with open(token_path, 'rb') as f:
            encrypted_lines = f.readlines()
            print(f"[DEBUG] Raw encrypted lines: {encrypted_lines}")

            encrypted_access = encrypted_lines[0].strip()
            encrypted_refresh = encrypted_lines[1].strip()
    except Exception as e:
        print(f"[ERROR] Failed to read token file: {e}")
        return None, f"file_read_error: {e}"

    try:
        access_token = decrypt_token(encrypted_access, key)
        print(f"[DEBUG] Decrypted access token for {email}")
    except InvalidToken:
        print(f"[ERROR] Invalid access token for {email}")
        return None, "invalid_access_token"

    response = requests.get("https://api.calendly.com/users/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    print(f"[DEBUG] Access token check status: {response.status_code}")

    if response.status_code == 401:  
        print(f"[INFO] Access token expired for {email}, attempting refresh")

        try:
            refresh_token = decrypt_token(encrypted_refresh, key)
            refresh_response = requests.post("https://auth.calendly.com/oauth/token", data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": os.environ.get("CALENDLY_CLIENT_ID"),
                "client_secret": os.environ.get("CALENDLY_CLIENT_SECRET")
            })

            print(f"[DEBUG] Refresh response status: {refresh_response.status_code}")
            print(f"[DEBUG] Refresh response data: {refresh_response.text}")

            if refresh_response.status_code != 200:
                print(f"[ERROR] Failed to refresh token for {email}")
                return None, f"refresh_failed: {refresh_response.json()}"

            new_tokens = refresh_response.json()
            access_token = new_tokens['access_token']
            refresh_token = new_tokens['refresh_token']

            with open(token_path, 'wb') as f:
                f.write(encrypt_token(access_token, key) + b'\n')
                f.write(encrypt_token(refresh_token, key) + b'\n')

            print(f"[INFO] Successfully refreshed and updated tokens for {email}")

        except Exception as e:
            print(f"[ERROR] Exception while refreshing token: {e}")
            return None, f"refresh_exception: {e}"

    return access_token, "valid"


@oauth_bp.route('/availability', methods=['GET'])
def doctor_availability():
    """
    Fetch doctor's availability.
    Fetch Format:
    GET /api/oauth/availability?doctor_email={doctor_email}
    """
    doctor_email = request.args.get('doctor_email')
    if not doctor_email:
        return jsonify({"error": "Missing doctor email"}), 400

    access_token, status = get_valid_access_token(doctor_email)
    if not access_token:
        return jsonify({"error": f"Failed to retrieve access token: {status}"}), 400

    if status == "not_found":
        return jsonify({"error": "Doctor not found"}), 404
    if not access_token:
        return jsonify({"error": "Failed to get valid access token"}), 400
    
    user_info_url = "https://api.calendly.com/users/me"
    user_response = requests.get(user_info_url, headers={
        "Authorization": f"Bearer {access_token}"
    })

    if user_response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info", "details": user_response.json()}), 400
    

    uri = user_response.json()['resource']['uri']

    available_times_url = f"https://api.calendly.com/user_availability_schedules?user={uri}"
    response = requests.get(available_times_url, headers={
        "Authorization": f"Bearer {access_token}"
    })

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch available times", "details": response.json()}), 400

    return jsonify({
        "message": "Successfully fetched doctor's availability",
        "available_times": response.json()
    })


@oauth_bp.route('/schedule', methods=['POST'])
def schedule_appointment():
    """
    Schedule an appointment with a doctor.
    Fetch Format:
    POST /api/oauth/schedule
    {
        "user_email": "user@example.com",
        "doctor_email": "doctor@example.com"
    }
    """
    data = request.json
    required = ['user_email', 'doctor_email']
    if not all(data.get(x) for x in required):
        return jsonify({"error": "Missing parameters"}), 400

    doctor_token, doc_status = get_valid_access_token(data['doctor_email'])
    if doc_status == "not_found":
        return jsonify({"error": "Doctor not found"}), 404
    if not doctor_token:
        return jsonify({"error": "Doctor token error"}), 400

    user_token, user_status = get_valid_access_token(data['user_email'])
    if user_status == "not_found":
        return jsonify({"error": "User not found"}), 404
    if not user_token:
        return jsonify({"error": "User token error"}), 400
    

    doctor_info_url = "https://api.calendly.com/users/me"
    doctor_response = requests.get(doctor_info_url, headers={
        "Authorization": f"Bearer {doctor_token}"
    })

    if doctor_response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info", "details": doctor_response.json()}), 400
    

    uri = doctor_response.json()['resource']['uri']

    doctor_event_types_url = f"https://api.calendly.com/event_types?user={uri}"
    doctor_event_response = requests.get(doctor_event_types_url, headers={
        "Authorization": f"Bearer {doctor_token}"
    })

    if doctor_event_response.status_code != 200:
        return jsonify({"error": "Failed to fetch doctor's event types", "details": doctor_event_response.json()}), 400

    event_type_uri = None
    event_types = doctor_event_response.json().get('collection', [])
    for event in event_types:
        if event.get('name') == "Doctor Consultation":
            event_type_uri = event.get('uri')
            break

    if not event_type_uri:
        return jsonify({"error": "Doctor Consultation event type not found"}), 404

    scheduling_link_url = "https://api.calendly.com/scheduling_links"
    scheduling_link_data = {
        "max_event_count": 1,
        "owner": event_type_uri,
        "owner_type": "EventType"
    }

    scheduling_response = requests.post(scheduling_link_url, json=scheduling_link_data, headers={
        "Authorization": f"Bearer {doctor_token}"
    })

    if scheduling_response.status_code != 201:
        return jsonify({"error": "Failed to create scheduling link", "details": scheduling_response.json()}), 400

    booking_url = scheduling_response.json().get("resource", {}).get("booking_url", "")
    if not booking_url:
        return jsonify({"error": "Failed to generate booking URL"}), 400

    return jsonify({
        "message": "Scheduling link generated successfully",
        "booking_url": booking_url
    })
