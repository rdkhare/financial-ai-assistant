import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_URL = "https://api.teller.io"
CLIENT_CERT = os.getenv("TELLER_CLIENT_CERT")  # Path to certificate.pem
CLIENT_KEY = os.getenv("TELLER_CLIENT_KEY")   # Path to private_key.pem

def fetch_accounts(access_token):
    url = f"{BASE_URL}/accounts"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, cert=(CLIENT_CERT, CLIENT_KEY))
    response.raise_for_status()
    return response.json()

def fetch_transactions(access_token, account_id):
    url = f"{BASE_URL}/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, cert=(CLIENT_CERT, CLIENT_KEY))
    response.raise_for_status()
    return response.json()