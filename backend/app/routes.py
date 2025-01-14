from flask import Blueprint, jsonify, request
from utils.db import add_access_token, add_user, db
from utils.teller_service import fetch_accounts, fetch_transactions
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.helpers.transaction_helpers import parse_transactions_categories, calculate_balance_over_time

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
    If accounts are not found, fetches them from the Teller API, retrieves balances and transactions in parallel,
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

            # Function to fetch balance and transactions for an account
            def fetch_balance_and_transactions(account):
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
                    "balance": None,
                    "transactions": None
                }

                balance_link = account.get("links", {}).get("balances")
                transaction_link = account.get("links", {}).get("transactions")

                try:
                    if balance_link:
                        balance_response = session.get(
                            balance_link,
                            auth=(access_token, ""),
                            cert=("certs/certificate.pem", "certs/private_key.pem"),
                            timeout=10
                        )
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            account_info["balance"] = balance_data.get("available")
                        else:
                            account_info["balance"] = "Error fetching balance"
                except RequestException as e:
                    account_info["balance"] = f"Error: {str(e)}"

                try:
                    if transaction_link:
                        transaction_response = session.get(
                            transaction_link,
                            auth=(access_token, ""),
                            cert=("certs/certificate.pem", "certs/private_key.pem"),
                            timeout=10
                        )
                        if transaction_response.status_code == 200:
                            transaction_data = transaction_response.json()
                            account_info["transactions"] = transaction_data
                        else:
                            account_info["transactions"] = "Error fetching transactions"
                except RequestException as e:
                    account_info["transactions"] = f"Error: {str(e)}"

                return account_info

            # Use ThreadPoolExecutor to fetch balances and transactions concurrently
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_account = {
                    executor.submit(fetch_balance_and_transactions, account): account
                    for account in accounts_data
                }
                for future in as_completed(future_to_account):
                    try:
                        account_info = future.result()
                        accounts.append(account_info)
                    except Exception as e:
                        accounts.append({"error": str(e)})

            # Parse transactions categories after fetching all accounts and transactions
            for account in accounts:
                transactions = account.get("transactions", [])
                if isinstance(transactions, list):  # Ensure valid transaction data before parsing
                    try:
                        account["transactionsPerCategory"] = parse_transactions_categories(transactions)
                    except Exception as e:
                        account["transactionsPerCategory"] = {"error": f"Parsing error: {str(e)}"}
                else:
                    account["transactionsPerCategory"] = {"error": "Invalid transaction data"}
            
            # Parse transactions over time for each account after fetching all data
            for account in accounts:
                if account.get("accountType") == "depository":

                    transactions = account.get("transactions", [])
                    if isinstance(transactions, list):
                        try:
                            # Calculate transactions over time
                            account["balanceOverTime"] = calculate_balance_over_time(transactions, None, None)
                        except Exception as e:
                            account["balanceOverTime"] = {"error": f"Error calculating balance over time: {str(e)}"}



            
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




@routes_bp.route("/sync-balances-and-transactions", methods=["POST"])
def sync_balances_and_transactions():
    """
    Syncs the balances and transactions of connected accounts for a user by fetching updated data from the Teller API.
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

        # Function to fetch balance and transactions for an account
        def fetch_account_data(account):
            balance_link = account.get("links", {}).get("balances")
            transaction_link = account.get("links", {}).get("transactions")
            
            try:
                if balance_link:
                    balance_response = session.get(
                        balance_link,
                        auth=(access_token, ""),
                        cert=("certs/certificate.pem", "certs/private_key.pem"),
                        timeout=10
                    )
                    if balance_response.status_code == 200:
                        balance_data = balance_response.json()
                        account["balance"] = balance_data.get("available")
                    else:
                        account["balance"] = "Error fetching balance"
            except RequestException as e:
                account["balance"] = f"Error: {str(e)}"

            try:
                if transaction_link:
                    transaction_response = session.get(
                        transaction_link,
                        auth=(access_token, ""),
                        cert=("certs/certificate.pem", "certs/private_key.pem"),
                        timeout=10
                    )
                    if transaction_response.status_code == 200:
                        transaction_data = transaction_response.json()
                        account["transactions"] = transaction_data
                    else:
                        account["transactions"] = "Error fetching transactions"
            except RequestException as e:
                account["transactions"] = f"Error: {str(e)}"

            return account

        # Use ThreadPoolExecutor to sync balances and transactions concurrently
        with get_session_with_retries() as session, ThreadPoolExecutor(max_workers=10) as executor:
            future_to_account = {
                executor.submit(fetch_account_data, account): account
                for account in accounts
            }
            updated_accounts = []
            for future in as_completed(future_to_account):
                try:
                    updated_accounts.append(future.result())
                except Exception as e:
                    updated_accounts.append({"error": str(e)})

        # Parse transactions per category for each account after fetching all data
        for account in updated_accounts:
            transactions = account.get("transactions", [])
            if isinstance(transactions, list):
                try:
                    account["transactionsPerCategory"] = parse_transactions_categories(transactions)
                except Exception as e:
                    account["transactionsPerCategory"] = {"error": f"Parsing error: {str(e)}"}

        # Parse transactions over time for each account after fetching all data
        for account in updated_accounts:
            if account.get("accountType") == "depository":

                transactions = account.get("transactions", [])
                if isinstance(transactions, list):
                    try:
                        # Calculate transactions over time
                        account["balanceOverTime"] = calculate_balance_over_time(transactions, None, None)
                    except Exception as e:
                        account["balanceOverTime"] = {"error": f"Error calculating balance over time: {str(e)}"}


        # Update the database with the refreshed balances and transactions
        bank_accounts_collection.update_one(
            {"userId": user_id},
            {"$set": {"accounts": updated_accounts}},
            upsert=True
        )

        return jsonify({"message": "Balances & transactions synced successfully", "accounts": updated_accounts}), 200

    except RequestException as re:
        return jsonify({"error": f"Request failed: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes_bp.route("/get-transactions-per-category", methods=["GET"])
def get_transactions_per_category():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
    if not stored_accounts:
        return jsonify({"error": "No accounts found for this user"}), 404

    transactions_per_category = {}
    for account in stored_accounts.get("accounts", []):
        account_map = account.get("transactionsPerCategory", {})
        for category, count in account_map.items():
            transactions_per_category[category] = transactions_per_category.get(category, 0) + count

    return jsonify({"transactionsPerCategory": transactions_per_category}), 200

@routes_bp.route("/get-balance-over-time", methods=["POST"])
def get_balance_over_time():
    data = request.json
    user_id = data.get("user_id")
    start_date = data.get("start_date")  
    end_date = data.get("end_date")     

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
    if not stored_accounts:
        return jsonify({"error": "No accounts found for this user"}), 404

    # Aggregate all transactions for the user
    all_transactions = []
    for account in stored_accounts.get("accounts", []):
        all_transactions.extend(account.get("transactions", []))

    # Calculate balance over time with date filtering
    balance_over_time = calculate_balance_over_time(all_transactions, start_date, end_date)

    return jsonify({"balanceOverTime": balance_over_time}), 200
