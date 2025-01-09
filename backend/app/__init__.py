from flask import Flask
from flask_cors import CORS
from app.routes import routes_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # Register Blueprint
    app.register_blueprint(routes_bp)

    @app.route("/")
    def home():
        return {"message": "Welcome to the Financial Assistant AI Backend"}

    return app