"""
Thin wrapper around the Razorpay Python SDK. All SDK calls go through here.
"""

import razorpay
import logging
from src.config import settings

logger = logging.getLogger(__name__)

# SDK Client
_client = razorpay.Client(
    auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
_client.set_app_details({"title" : "AgenticCommerce", "version" :"1.0.0"})

def create_order(
        amount_inr: float,
        receipt: str,
        notes: dict | None = None,
) -> dict:
    """
    Creates a Razorpay order.
    Args:
        amount_inr: Amount in Indian Rupees (will be converted to paise internally)
        receipt:    Your internal order ID / reference (max 40 chars)
        notes:      Optional key-value metadata (up to 15 pairs)
    Returns:
        Razorpay order dict with keys: id, amount, currency, status, receipt
    """
    amount_paise = int(amount_inr * 100)

    payload = {
        "amount" : amount_paise,
        "currency" : "INR",
        "receipt" : receipt[:40],
        "payment_capture":1,
        "notes" : notes or {},
    }
    try:
        order = _client.order.create(data = payload)
        logger.info(f"Razorpay order created: {order['id']} for ₹{amount_inr}")
        return order
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay bad request: {e}")
        raise ValueError(f"Razorpay order creation failed{e}") from e
    except razorpay.errors.ServerError as e:
        logger.error(f"Razorpay server error: {e}")
        raise RuntimeError(f"Razorpay server error: {e}") from e

def create_payment_link(
        amount_inr : float,
        description: str ,
        reference_id: str,
        customer_name: str = "AI_Buyer",
        customer_email: str = "buyer@agenticsystem.ai",
        customer_contact: str = "+919999999999",
        callback_url: str | None = None
) -> dict:
    """
    Creates a Razorpay Payment Link — the headless checkout URL.
    The AI agent returns this URL to the user who clicks it to pay.
    Returns:
        Payment link dict containing 'short_url' and 'id'
    """

    amount_paise = int(amount_inr * 100)

    payload = {
        "amount" : amount_paise,
        "currency" :"INR",
        "accept_partial" : False,
        "reference_id" : reference_id[:40],
        "description" : description[:255],
        "customer" : {
            "name" : customer_name,
            "email" : customer_email,
            "contact" : customer_contact,
        },
        "notify" : {
            "sms":False,
            "email":False,
        },
        "reminder_enable": False,
    }

    if callback_url:
        payload["callback_url"] = callback_url
        payload["callback_method"] = "get"

    try:
        link = _client.payment_link.create(data = payload)
        logger.info(
            f"Payment link created: {link['id']} -> {link.get('short_url')}"
            f"for ₹{amount_inr}"
        )
        return link
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Payment link creation failed: {e}")
        raise ValueError(f"Payment link creation failed: {e}") from e
    except razorpay.errors.ServerError as e:
        logger.error(f"Razorpay server error during payment link: {e}")
        raise RuntimeError(f"Razorpay server error: {e}") from e

def fetch_order(razorpay_order_id: str) -> dict:
    """Fetch a Razorpay Order by its ID to check current status."""
    try:
        return _client.order.fetch(razorpay_order_id)
    except Exception as e:
        logger.error(f"Failed to fetch order {razorpay_order_id}: {e}")
        raise

def verify_webhook_signature(
    body: str,
    signature: str,
    secret: str,
) -> bool:
    """
    Verifies a Razorpay webhook signature using HMAC-SHA256.
    Returns True if valid, False if tampered.
    """

    try:
        _client.utility.verify_webhook_signature(body, signature, secret)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    