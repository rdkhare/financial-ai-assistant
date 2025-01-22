from flask import Blueprint, jsonify, request
from utils.db import db
from utils.teller_service import fetch_accounts
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.helpers.transaction_helpers import parse_transactions_categories, calculate_balance_over_time
from utils.request_utils import get_session_with_retries
from utils.plaid_service import create_link_token, exchange_public_token, transactions_sync, transactions_refresh, fetch_accounts as fetch_plaid_accounts

account_routes_bp = Blueprint("account_routes", __name__)

# Bank accounts collection
bank_accounts_collection = db["bank_accounts"]
users_collection = db["users"]

@account_routes_bp.route("/accounts", methods=["POST"])
def get_accounts():
    access_token = request.json.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token is required"}), 400
    try:
        accounts = fetch_accounts(access_token)
        return jsonify(accounts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## Plaid API get accounts route
@account_routes_bp.route("/get-plaid-accounts", methods=["POST"])
def get_plaid_accounts():
    try:
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Check if accounts already exist in the database
        stored_accounts = bank_accounts_collection.find_one({"userId": user_id})
        if stored_accounts:
            return jsonify({"accounts": stored_accounts["accounts"]}), 200

        user = users_collection.find_one({"_id": user_id})
        if not user or "plaid_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["plaid_access_token"]
        accounts = fetch_plaid_accounts(access_token)

        account_infos = []
        if accounts["accounts"]:
            for account in accounts["accounts"]:
                account_info = {
                    "accountName": account.get("name"),
                    "accountType": account.get("type"),
                    "accountNumber": account.get("mask"),
                    "currency": account.get("balances", {}).get("iso_currency_code"),
                    "subtype": account.get("subtype"),
                    "account_id": account.get("account_id"),
                    "balance": account.get("balances", {}).get("current"),
                    "transactions": None
                }
                account_infos.append(account_info)
                users_collection.update_one(
                    {"_id": user_id},
                    {"$addToSet": {"accountIds": account.get("account_id")}}
                )

                bank_accounts_collection.update_one(
                    {"userId": user_id},
                    {"$set": {"accounts": account_infos}},
                    upsert=True
                )

        
        return jsonify(account_infos), 200
    except RequestException as re:
        return jsonify({"error": f"Request failed: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@account_routes_bp.route("/get-transactions", methods=["POST"])
def get_transactions():
    try:
        data = request.json
        user_id = data.get("user_id")
        start_date = data.get("start_date") or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = data.get("end_date") or datetime.now().strftime("%Y-%m-%d")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Fetch user's access token
        user = users_collection.find_one({"_id": user_id})
        if not user or "plaid_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["plaid_access_token"]

        # Fetch transactions using Plaid API
        transactions = fetch_transactions(access_token, start_date, end_date)
        return jsonify({"transactions": transactions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## Teller API
@account_routes_bp.route("/get-connected-accounts", methods=["POST"])
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

@account_routes_bp.route("/sync-balances-and-transactions", methods=["POST"])
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

@account_routes_bp.route("/create-link-token", methods=["POST"])
def create_link_token_route():
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    try:
        link_token = create_link_token(user_id)
        return jsonify(link_token), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@account_routes_bp.route("/exchange-public-token", methods=["POST"])
def exchange_public_token_route():
    public_token = request.json.get("public_token")
    user_id = request.json.get("user_id")
    if not public_token or not user_id:
        return jsonify({"error": "Public token and User ID are required"}), 400
    try:
        exchange_response = exchange_public_token(public_token)
        access_token = exchange_response.get("access_token")
        # Save access_token in the database
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"plaid_access_token": access_token, "next_cursor": None}},
            upsert=True
        )
        return jsonify({"message": "Token exchanged successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@account_routes_bp.route("/transactions/sync", methods=["POST"])
def sync_transactions():
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    try:
        user = users_collection.find_one({"_id": user_id})
        if not user or "plaid_access_token" not in user:
            return jsonify({"error": "No access token found for this user"}), 404

        access_token = user["plaid_access_token"]
        cursor = user.get("next_cursor", None)

        transactions = []
        while True:
            response = transactions_sync(access_token, cursor)
            transactions.extend(response["added"])
            cursor = response.get("next_cursor")
            if not response.get("has_more", False):
                break

        # Save the latest cursor in the database
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"next_cursor": cursor}}
        )

        return jsonify({"transactions": transactions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500