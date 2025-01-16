from flask import Flask
from flask_cors import CORS
from app.routes import user_routes_bp, account_routes_bp, transaction_routes_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(user_routes_bp)
    app.register_blueprint(account_routes_bp)
    app.register_blueprint(transaction_routes_bp)

    @app.route("/")
    def home():
        return {"message": "Welcome to the Financial Assistant AI Backend"}

    return app