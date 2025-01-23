from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
# Get the MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)

# Access the database
db = client["financial_assistant"]

# Access the users collection
users_collection = db["users"]
# Function to get the database client 
def get_db():
    return db
def add_user(user_id, name, email):
    """Add a new user to the users collection."""
    user_data = {
        "_id": user_id,      # Firebase UID
        "name": name,
        "email": email,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "preferences": {
            "currency": "USD",
            "dark_mode": False,
        }
    }
    users_collection.insert_one(user_data)
    return user_data

def add_plaid_access_token(user_id, access_token):
    users_collection.update_one(
        {"_id": user_id},
        {"$addToSet": {"plaid_access_tokens": {"token": access_token, "created_at": datetime.datetime.utcnow()}}},
        upsert=True
    )

def add_account(user_id, account_info):
    bank_accounts_collection.update_one(
        {"userId": user_id},
        {"$addToSet": {"accounts": account_info}},
        upsert=True
    )

