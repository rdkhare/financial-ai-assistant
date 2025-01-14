# Helper functions for parsing transactions data

def parse_transactions_categories(transactions):
    """
    Parses a list of transactions and counts the number of transactions per category.

    Args:
        transactions (list): List of transactions with a 'category' field.

    Returns:
        dict: A hashmap where keys are categories and values are counts of transactions.
    """
    category_count = {}
    for transaction in transactions:
        category = transaction["details"].get("category", "Unknown")  # Default category if missing
        category_count[str(category)] = category_count.get(category, 0) + 1
    return category_count

def calculate_balance_over_time(transactions, start_date=None, end_date=None):
    """
    Aggregates balances over time based on transaction data and date range.
    Args:
        transactions (list): List of transaction dictionaries with 'amount' and 'date' fields.
        start_date (str): Start date in "YYYY-MM-DD" format (optional).
        end_date (str): End date in "YYYY-MM-DD" format (optional).

    Returns:
        list: A sorted list of dictionaries containing 'date' and cumulative 'balance'.
    """
    from collections import defaultdict
    from datetime import datetime

    daily_balances = defaultdict(float)

    # Filter transactions based on the date range
    for transaction in transactions:
        
        date_str = transaction.get("date")
        amount = float(transaction.get("amount", 0))
        if date_str and isinstance(amount, (int, float)):
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if start_date and date < datetime.strptime(start_date, "%Y-%m-%d").date():
                continue
            if end_date and date > datetime.strptime(end_date, "%Y-%m-%d").date():
                continue
            daily_balances[date] += amount

    # Sort dates and calculate cumulative balance
    sorted_dates = sorted(daily_balances.keys())
    cumulative_balance = 0
    balance_over_time = []

    for date in sorted_dates:
        cumulative_balance += daily_balances[date]
        balance_over_time.append({"date": date.strftime("%Y-%m-%d"), "balance": cumulative_balance})

    return balance_over_time
