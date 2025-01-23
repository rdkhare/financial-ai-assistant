from flask import Blueprint, jsonify, request
from utils.db import add_user, add_plaid_access_token, db

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

        # Append the access token to the user's list of tokens
        users_collection.update_one(
            {"_id": user_id},
            {"$addToSet": {"plaid_access_tokens": {"token": access_token, "created_at": datetime.datetime.utcnow()}}},
            upsert=True
        )
        return jsonify({"message": "Access token stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500