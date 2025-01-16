from flask import Blueprint, jsonify, request
from utils.db import add_user, add_access_token, db

user_routes_bp = Blueprint("user_routes", __name__)

# Users collection
users_collection = db["users"]

@user_routes_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        user_id = data["user_id"]
        email = data["email"]
        name = data.get("name", "Anonymous")

        user_data = add_user(user_id, name, email)
        return jsonify({"status": "success", "user": user_data}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_routes_bp.route("/store-access-token", methods=["POST"])
def store_access_token():
    try:
        data = request.json
        access_token = data.get("access_token")
        user_id = data.get("user_id")

        if not access_token or not user_id:
            return jsonify({"error": "Access token and user ID are required"}), 400

        add_access_token(user_id, access_token)
        return jsonify({"message": "Access token stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500