"""
Paystack payment integration.

Key differences from Flutterwave that trip people up:
- Amounts are in KOBO, not naira (multiply by 100 when sending, divide by 100 when reading back)
- The callback only gives you one identifier: `reference` (not separate tx_ref + transaction_id)
- Verification endpoint takes the reference directly in the URL, not a numeric transaction ID
"""

import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"


def initiate_payment(payment, buyer, callback_url):
    """Creates a Paystack checkout link. Returns the URL to redirect the
    buyer to, or raises on failure."""

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    amount_in_kobo = int(payment.total_amount * 100)

    payload = {
        "reference": str(payment.tx_ref),
        "amount": amount_in_kobo,
        "currency": "NGN",
        "email": buyer.email,
        "callback_url": callback_url,
        "metadata": {
            "order_id": payment.order_id,
            "buyer": buyer.username,
        },
    }

    response = requests.post(
        f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers, timeout=15
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("status"):
        raise PaystackError(data.get("message", "Failed to initiate payment"))

    return data["data"]["authorization_url"]


def verify_transaction(reference):
    """Confirms a transaction actually went through. ALWAYS call this before
    marking a payment as paid — never trust the frontend redirect alone."""

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(
        f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers, timeout=15
    )
    response.raise_for_status()
    return response.json()


class PaystackError(Exception):
    pass