# app/plaid_utils.py

import os
from plaid import Client
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.api import plaid_api
from app import app

client = Client(
    client_id=os.getenv('PLAID_CLIENT_ID'),
    secret=os.getenv('PLAID_SECRET'),
    environment=os.getenv('PLAID_ENV')
)

def get_accounts(access_token):
    """
    Fetch accounts linked to a user's bank.
    """
    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)
    return response['accounts']

def get_transactions(access_token, start_date, end_date):
    """
    Fetch transactions for a given period.
    """
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)
    return response['transactions']
