from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS

    # Example route
    @app.route("/")
    def home():
        return {"message": "Welcome to the Financial Assistant AI Backend"}

    return app