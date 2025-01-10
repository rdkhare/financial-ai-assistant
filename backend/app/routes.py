from flask import Blueprint, jsonify, request
from utils.db import add_access_token, add_user, db
from utils.teller_service import fetch_accounts, fetch_transactions
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

routes_bp = Blueprint("routes", __name__)

# Users collection
users_collection = db["users"]
# Bank accounts collection
bank_accounts_collection = db["bank_accounts"]

# Configure retries for API requests
def get_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=5,  # Retry up to 5 times
        backoff_factor=0.5,  # Exponential backoff
        status_forcelist=[500, 502, 503, 504],  # Retry on these status codes
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

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
    Retrieves connected accounts for a user from the MongoDB database.
    If accounts are not found, fetches them from the Teller API, retrieves balances,
    and stores them in the database.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Check if accounts already exist in the database
        stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
        if stored_accounts:
            return jsonify({"accounts": stored_accounts["accounts"]}), 200

        # Fetch user's access token
        user = users_collection.find_one({"_id": user_id})
        if not user or "teller_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["teller_access_token"]

        # Fetch accounts from the Teller API
        with get_session_with_retries() as session:
            response = session.get(
                "https://api.teller.io/accounts",
                auth=(access_token, ""),
                cert=("certs/certificate.pem", "certs/private_key.pem"),
                timeout=10
            )

            if response.status_code != 200:
                return jsonify({"error": response.json()}), response.status_code

            accounts_data = response.json()
            accounts = []

            # Fetch balances for each account
            for account in accounts_data:
                account_info = {
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
                    "linkedAt": None,
                    "balance": None
                }

                # Fetch the balance using the balance link
                balance_link = account.get("links", {}).get("balances")
                if balance_link:
                    try:
                        balance_response = session.get(
                            balance_link,
                            auth=(access_token, ""),
                            cert=("certs/certificate.pem", "certs/private_key.pem"),
                            timeout=10
                        )
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            account_info["balance"] = balance_data.get("available")  # Use "available" or "current"
                        else:
                            account_info["balance"] = "Error fetching balance"
                    except RequestException as balance_error:
                        account_info["balance"] = f"Error: {str(balance_error)}"

                accounts.append(account_info)

            # Store accounts in the database
            bank_accounts_collection.update_one(
                {"userId": user_id},
                {"$set": {"accounts": accounts}},
                upsert=True
            )

        return jsonify({"accounts": accounts}), 200

    except RequestException as re:
        return jsonify({"error": f"Request failed: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@routes_bp.route("/sync-balances", methods=["POST"])
def sync_balances():
    """
    Syncs the balances of connected accounts for a user by fetching updated data from the Teller API.
    Triggered by the sync button on the frontend.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Fetch user's access token
        user = users_collection.find_one({"_id": user_id})
        if not user or "teller_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["teller_access_token"]

        # Retrieve accounts from the database
        stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
        if not stored_accounts:
            return jsonify({"error": "No accounts found for this user"}), 404

        accounts = stored_accounts["accounts"]

        # Sync balances for each account
        with get_session_with_retries() as session:
            for account in accounts:
                balance_link = account.get("links", {}).get("balances")
                if balance_link:
                    try:
                        response = session.get(
                            balance_link,
                            auth=(access_token, ""),
                            cert=("certs/certificate.pem", "certs/private_key.pem"),
                            timeout=10
                        )
                        if response.status_code == 200:
                            balance_data = response.json()
                            account["balance"] = balance_data.get("available")  # Use "available" or "current"
                        else:
                            account["balance"] = "Error fetching balance"
                    except RequestException as balance_error:
                        account["balance"] = f"Error: {str(balance_error)}"

            # Update the database with the refreshed balances
            bank_accounts_collection.update_one(
                {"userId": user_id},
                {"$set": {"accounts": accounts}},
                upsert=True
            )

        return jsonify({"message": "Balances synced successfully", "accounts": accounts}), 200

    except RequestException as re:
        return jsonify({"error": f"Request failed: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

