from flask import Blueprint, jsonify, request
from utils.db import add_access_token, add_user, db
from utils.teller_service import fetch_accounts, fetch_transactions
import requests


routes_bp = Blueprint("routes", __name__)

# Users collection
users_collection = db["users"]
# Bank accounts collection
bank_accounts_collection = db["bank_accounts"]

@routes_bp.route("/signup", methods=["POST"])
def signup():
    try:
        # Parse JSON request
        data = request.get_json()
        user_id = data["user_id"]
        email = data["email"]
        name = data.get("name", "Anonymous")  # Default to 'Anonymous' if no name is provided

        # Add user to MongoDB
        user_data = add_user(user_id, name, email)
        return jsonify({"status": "success", "user": user_data}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@routes_bp.route("/accounts", methods=["POST"])
def get_accounts():
    access_token = request.json.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token is required"}), 400
    try:
        accounts = fetch_accounts(access_token)
        return jsonify(accounts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route("/transactions", methods=["POST"])
def get_transactions():
    access_token = request.json.get("access_token")
    account_id = request.json.get("account_id")
    if not access_token or not account_id:
        return jsonify({"error": "Access token and account ID are required"}), 400
    try:
        transactions = fetch_transactions(access_token, account_id)
        return jsonify(transactions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes_bp.route("/store-access-token", methods=["POST"])
def store_access_token():
    try:
        data = request.json
        access_token = data.get("access_token")
        user_id = data.get("user_id")  # Retrieve the user's ID from the frontend

        if not access_token or not user_id:
            return jsonify({"error": "Access token and user ID are required"}), 400

        # Update or insert the user document with the access token
        add_access_token(user_id, access_token)
        return jsonify({"message": "Access token stored successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes_bp.route("/get-connected-accounts", methods=["POST"])
def get_connected_accounts():
    """
    Retrieves connected accounts for a user from the Teller API, updates their balances, 
    and ensures balance information is available even for newly connected accounts.
    """
    try:
        # Extract data from the request
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Retrieve the user's access token from the `users` collection
        user = users_collection.find_one({"_id": user_id})
        if not user or "teller_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["teller_access_token"]

        # Check if accounts are already stored in the `bank_accounts` collection
        stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
        accounts = []

        if stored_accounts:
            accounts = stored_accounts["accounts"]
        else:
            # Fetch accounts from the Teller API
            response = requests.get(
                "https://api.teller.io/accounts",
                auth=(access_token, ""),  # Use access token for Basic Auth
                cert=("certs/certificate.pem", "certs/private_key.pem")  # Teller certificates
            )

            if response.status_code != 200:
                return jsonify({"error": response.json()}), response.status_code

            # Parse the accounts data from the API response
            accounts_data = response.json()
            for account in accounts_data:
                accounts.append({
                    "accountName": account.get("name"),
                    "bankName": account.get("institution", {}).get("name"),
                    "accountType": account.get("type"),
                    "accountNumber": account.get("last_four"),
                    "currency": account.get("currency"),
                    "status": account.get("status"),
                    "subtype": account.get("subtype"),
                    "links": account.get("links"),
                    "enrollment_id": account.get("enrollment_id"),
                    "teller_id": account.get("id"),
                    "linkedAt": None,  # Set to None initially
                    "balance": None  # Initialize balance
                })

            # Insert the user's accounts into the database
            bank_accounts_collection.insert_one({
                "userId": user_id,
                "accounts": accounts
            })

        # Fetch and update balances for all accounts
        for account in accounts:
            balance_link = account.get("links", {}).get("balances")
            if balance_link:
                response = requests.get(
                    balance_link,
                    auth=(access_token, ""),  # Use access token for Basic Auth
                    cert=("certs/certificate.pem", "certs/private_key.pem")  # Teller certificates
                )
                if response.status_code == 200:
                    balance_data = response.json()
                    account["balance"] = balance_data.get("available")  # Use "available" or "current"
                else:
                    account["balance"] = "Error Occurred"  # Handle API failure gracefully

        # Update the database with the refreshed balances
        bank_accounts_collection.update_one(
            {"userId": user_id},
            {"$set": {"accounts": accounts}},
            upsert=True  # Create a new document if one does not already exist
        )

        # Return the updated account information
        return jsonify({"accounts": accounts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

