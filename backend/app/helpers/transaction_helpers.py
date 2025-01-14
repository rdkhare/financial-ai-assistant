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
    for txn in transactions:
        category = txn["details"].get("category", "Unknown")  # Default category if missing
        category_count[str(category)] = category_count.get(category, 0) + 1
    return category_count
