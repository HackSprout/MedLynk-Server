from flask import Flask
from app.routes.oauth import oauth_bp 
from app.routes.chat import chat_bp
from app.routes.pdf import pdf_bp

app = Flask(__name__)

app.register_blueprint(oauth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(pdf_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)