import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.exceptions import ApiException
import os

# Load environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")

# Configure Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": "677749b464d8db0020bd9a20",
        "secret": "302c60f63db51bccde6cb0f78bfc6d",
    },
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_link_token(user_id):
    """Generate a link token for a user."""
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="Financial Assistant AI",
        country_codes=[CountryCode("US")],
        language="en",
        user={"client_user_id": user_id},
    )
    response = client.link_token_create(request)
    return response.to_dict()

def exchange_public_token(public_token):
    """Exchange the public token for an access token."""
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.to_dict()

def fetch_the_transactions(access_token, start_date, end_date):
    """Fetch transactions for a user."""
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
    )
    response = client.transactions_get(request)
    return response.to_dict()

def create_sandbox_public_token():
    try:
        # Simulate public token creation in the Sandbox environment
        request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",  # Sample Plaid institution
            initial_products=[Products("transactions")],  # Specify the products you want
            options={
                "webhook": "https://your-webhook-url.com",  # Optional: Add webhook for transaction updates
            }
        )
        response = client.sandbox_public_token_create(request)
        return response.public_token
    except ApiException as e:
        print(f"Error creating sandbox public token: {e}")
        raise e