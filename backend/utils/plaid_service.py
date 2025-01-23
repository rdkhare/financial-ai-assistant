import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_refresh_request import TransactionsRefreshRequest

from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
import os

# Configure Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_link_token(user_id):
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="Financial Assistant AI",
        country_codes=[CountryCode("US")],
        language="en",
        user={"client_user_id": user_id},
        webhook="https://yourdomain.com/plaid-webhook",
    )
    response = client.link_token_create(request)
    return response.to_dict()

def exchange_public_token(public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.to_dict()

def fetch_accounts(access_token):
    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)
    return response.to_dict()

def transactions_sync(access_token, cursor=None):
    request = TransactionsSyncRequest(access_token=access_token, cursor=cursor) if cursor else TransactionsSyncRequest(access_token=access_token)
    response = client.transactions_sync(request)
    return response.to_dict()

def transactions_refresh(access_token):
    request = TransactionsRefreshRequest(access_token=access_token)
    response = client.transactions_refresh(request)
    return response.to_dict()