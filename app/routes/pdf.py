from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app.memory.session_store import append_to_history, get_chat_history
from app.services.pdf_parser import parse_pdf
import os

pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/pdf')
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@pdf_bp.route("/upload/<user_email>", methods=["POST"])
def upload_pdf(user_email):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    user_folder = os.path.join(UPLOAD_FOLDER, user_email)

    os.makedirs(user_folder, exist_ok=True)

   
    filename = secure_filename(file.filename)

    file_path = os.path.join(user_folder, filename)
    file.save(file_path)

    text = parse_pdf(file_path)

    return jsonify({"parsed_text": text})

@pdf_bp.route("/delete/<user_email>/<filename>", methods=["DELETE"])
def delete_pdf(user_email, filename):
    filename = secure_filename(filename)
    user_folder = os.path.join(UPLOAD_FOLDER, user_email)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"})
    else:
        return jsonify({"error": "File not found"}), 404


@pdf_bp.route("/list", methods=["GET"])
def list_pdfs():
    pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    return jsonify({"pdf_files": pdf_files})


@pdf_bp.route("/parse/<user_email>", methods=["GET"])
def parse_pdfs(user_email):

    if get_chat_history(user_email):
        return jsonify({"message": "Chat already started"})

    user_folder = os.path.join(UPLOAD_FOLDER, user_email)
    if not os.path.exists(user_folder):
        return jsonify({"error": "User folder not found"}), 404

    pdf_files = [f for f in os.listdir(user_folder) if f.endswith(".pdf")]
    parsed_texts = {}

    for pdf_file in pdf_files:
        file_path = os.path.join(user_folder, pdf_file)
        text = parse_pdf(file_path)
        parsed_texts[pdf_file] = text

    

    append_to_history(user_email, "user", f"Here are my combined medical records:\n{parsed_texts}")
    append_to_history(user_email, "model", "Understood. I'll use these records to answer your questions.")

    return jsonify({"parsed_texts": parsed_texts})
