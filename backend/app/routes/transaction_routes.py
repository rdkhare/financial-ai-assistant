from flask import Blueprint, jsonify, request
from utils.db import db
from app.helpers.transaction_helpers import calculate_balance_over_time

transaction_routes_bp = Blueprint("transaction_routes", __name__)

# Bank accounts collection
bank_accounts_collection = db["bank_accounts"]

@transaction_routes_bp.route("/get-transactions-per-category", methods=["GET"])
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

@transaction_routes_bp.route("/get-balance-over-time", methods=["POST"])
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

    all_transactions = []
    for account in stored_accounts.get("accounts", []):
        all_transactions.extend(account.get("transactions", []))

    balance_over_time = calculate_balance_over_time(all_transactions, start_date, end_date)

    return jsonify({"balanceOverTime": balance_over_time}), 200