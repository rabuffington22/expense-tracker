"""Plaid SDK wrapper — reads credentials from environment variables."""

import os
from datetime import datetime, timedelta

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_remove_request import ItemRemoveRequest


def _get_env():
    """Map PLAID_ENV string to Plaid API environment."""
    env = os.environ.get("PLAID_ENV", "sandbox").lower()
    return {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }.get(env, plaid.Environment.Sandbox)


def _get_client() -> plaid_api.PlaidApi:
    """Build and return a PlaidApi client from env vars."""
    client_id = os.environ.get("PLAID_CLIENT_ID", "")
    secret = os.environ.get("PLAID_SECRET", "")
    if not client_id or not secret:
        raise RuntimeError(
            "PLAID_CLIENT_ID and PLAID_SECRET environment variables are required."
        )
    config = plaid.Configuration(
        host=_get_env(),
        api_key={"clientId": client_id, "secret": secret},
    )
    return plaid_api.PlaidApi(plaid.ApiClient(config))


def create_link_token(user_id: str = "expense-tracker-user") -> str:
    """Create a Plaid Link token for the frontend. Returns the link_token string."""
    client = _get_client()
    req = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        client_name="Ledger Oak",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )
    resp = client.link_token_create(req)
    return resp.link_token


def exchange_public_token(public_token: str) -> dict:
    """Exchange a public token for an access token. Returns {access_token, item_id}."""
    client = _get_client()
    req = ItemPublicTokenExchangeRequest(public_token=public_token)
    resp = client.item_public_token_exchange(req)
    return {"access_token": resp.access_token, "item_id": resp.item_id}


def get_accounts(access_token: str) -> list[dict]:
    """Fetch accounts for an item. Returns list of account dicts."""
    client = _get_client()
    req = AccountsGetRequest(access_token=access_token)
    resp = client.accounts_get(req)
    return [
        {
            "account_id": a.account_id,
            "name": a.name,
            "mask": a.mask,
            "type": str(a.type),
            "subtype": str(a.subtype) if a.subtype else None,
        }
        for a in resp.accounts
    ]


def get_transactions(access_token: str, cursor: str | None = None) -> dict:
    """
    Fetch transactions using the sync endpoint (incremental).

    Returns {added: [...], modified: [...], removed: [...], next_cursor: str, has_more: bool}.
    Each transaction dict has: transaction_id, date, amount, name, merchant_name, account_id.
    """
    client = _get_client()
    all_added = []
    all_modified = []
    all_removed = []
    has_more = True

    while has_more:
        kwargs = {"access_token": access_token}
        if cursor:
            kwargs["cursor"] = cursor
        req = TransactionsSyncRequest(**kwargs)
        resp = client.transactions_sync(req)

        for t in resp.added:
            all_added.append({
                "plaid_transaction_id": t.transaction_id,
                "date": str(t.date),
                "amount": float(t.amount),
                "name": t.name,
                "merchant_name": t.merchant_name,
                "account_id": t.account_id,
            })
        for t in resp.modified:
            all_modified.append({
                "plaid_transaction_id": t.transaction_id,
                "date": str(t.date),
                "amount": float(t.amount),
                "name": t.name,
                "merchant_name": t.merchant_name,
                "account_id": t.account_id,
            })
        for t in resp.removed:
            all_removed.append(t.transaction_id)

        cursor = resp.next_cursor
        has_more = resp.has_more

    return {
        "added": all_added,
        "modified": all_modified,
        "removed": all_removed,
        "next_cursor": cursor,
        "has_more": False,
    }


def remove_item(access_token: str) -> bool:
    """Remove a Plaid item (disconnect). Returns True on success."""
    client = _get_client()
    req = ItemRemoveRequest(access_token=access_token)
    client.item_remove(req)
    return True
