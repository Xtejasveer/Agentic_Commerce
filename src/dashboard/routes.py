"""
FastAPI route handlers for the merchant dashboard.
Provides the audit trail, order management, and Razorpay webhook receiver.
"""
import json
import asyncio
import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, cast, Date
from typing import Optional

from src.database.session import get_db
from src.database.models import AuditLogRecord, OrderRecord, AgentMandateRecord, ProductRecord
from src.payments.razorpay_client import verify_webhook_signature
from src.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory queue for SSE - audit events are pushed here and streamed to clients
_sse_queue: asyncio.Queue = asyncio.Queue()

## Health 
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Confirms the server and database are reachable"""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status" : "ok", "database" : "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e}")

## Audit trail
@router.get("/audit")
def get_audit_trail(
    limit: int = 50,
    offset: int = 0,
    agent_id : Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Returns the paginated audit trail, most recent first.
    Optionally filter by agent_id or event_type
    """

    query = db.query(AuditLogRecord).order_by(desc(AuditLogRecord.timestamp))

    if agent_id:
        query = query.filter(AuditLogRecord.agent_id == agent_id)
    if event_type:
        query = query.filter(AuditLogRecord.event_type == event_type.upper())

    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {
        "total" : total,
        "offset" : offset,
        "limit": limit,
        "entries": [_format_audit(r) for r in records]
    }

@router.get("/audit/stream")
async def stream_audit_events(request: Request):
    """
    Server-Sent events (SSE) endpoint- streams audit events in real time.
    """

    async def event_generator():
        yield "data: {\"type\": \"connected\", \"message\": \"Audit stream live\"}\n\n"

        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            try:
                # Wait for 5 seconds for a new event
                event = await asyncio.wait_for(_sse_queue.get(), timeout=5)
                yield f"data {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                yield "data: {\"type\": \"heartbeat\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

def push_audit_event(event: dict):
    """
    Called whenever a new audit entry is written.
    Pushes it to the SSE queue so connected dashboard clients see it instantly.
    """
    try:
        _sse_queue.put_nowait(event)
    except asyncio.QueueFull:
        pass
# Orders

@router.get("/orders")
def get_orders(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns all orders with optional filtering by status or agent."""
    query = db.query(OrderRecord).order_by(desc(OrderRecord.created_at))

    if status:
        query = query.filter(OrderRecord.status == status)
    if agent_id:
        query = query.filter(OrderRecord.agent_id == agent_id)

    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {
        "total" : total,
        "orders" : [_format_order(r) for r in records]
    }

@router.get("/orders/{order_id}")
def get_order(order_id: str, db:Session = Depends(get_db)):
    """Returns full details for a single order."""
    record = db.query(OrderRecord).filter(OrderRecord.order_id == order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return _format_order(record)

# Mandates

@router.get("/mandates")
def get_mandates(db: Session = Depends(get_db)):
    """Returns all registered agent mandates.""" 
    records = db.query(AgentMandateRecord).all()
    return {"mandates" : [_format_mandate(r) for r in records]}

@router.get("/mandates/{agent_id}/spend")
def get_agent_spend (agent_id: str, db:Session = Depends(get_db)):
    """
    Returns an agent's spend summary - today's total, all-time total,
    and remaining daily budget.
    """
    mandate = db.query(AgentMandateRecord).filter(
        AgentMandateRecord.agent_id == agent_id
    ).first()

    if not mandate:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    today = date.today()

    today_spend = db.query(
        func.coalesce(func.sum(OrderRecord.total_amount_inr),0)
    ).filter(
        OrderRecord.agent_id == agent_id,
        OrderRecord.status.in_(["paid", "payment_initiated"]),
        cast(OrderRecord.created_at, Date) == today,
    ).scalar()

    all_time_spend = db.query(
        func.coalesce(func.sum(OrderRecord.total_amount_inr),0)
    ).filter(
        OrderRecord.agent_id == agent_id,
        OrderRecord.status.in_(["paid","payment_initiated"])
    ).scalar()

    today_spend = float(today_spend or 0)
    all_time_spend = float(all_time_spend or 0)

    return {
        "agent_id": agent_id,
        "today_spend_inr": today_spend,
        "all_time_spend_inr": all_time_spend,
        "daily_limit_inr": mandate.max_daily_spend_inr,
        "remaining_today_inr": max(0, mandate.max_daily_spend_inr - today_spend),
        "single_txn_limit_inr": mandate.max_single_txn_inr,
        "allowed_categories": mandate.allowed_categories,
    }

# Razorpay Webhook

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias = "X-Razorpay-Signature"),
    db: Session = Depends(get_db)
):
    """
    Receives and processes Razorpay Webhook events.

    IMPORTANT: Uses the raw reuest body for signature verification -
    do NOT parse the body before verifying.
    """

    raw_body = await request.body()

    # verify webhook signature
    if x_razorpay_signature and settings.RAZORPAY_WEBHOOK_SECRET != "mock_webhook_secret":
        is_valid = verify_webhook_signature(
            body = raw_body.decode("utf=8"),
            signature = x_razorpay_signature,
            secret=settings.RAZORPAY_WEBHOOK_SECRET,
        )
        if not is_valid:
            logger.warning("Received webhook with invalid signature - rejected")
            raise HTTPException(status_code=400, detail="Invalid webhooks signature.")

    event_data = json.loads(raw_body)
    event_type = event_data.get("event", "unknown")
    logger.info(f"Webhook received: {event_type}")

    # Handle Event types

    if event_type == "order_paid":
        _handle_order_paid(db, event_data)

    elif event_type == "payment.captured":
        _handle_payment_captured(db, event_data)
    elif event_type == "payment.failed":
        _handle_payment_failed(db, event_data)
    elif event_type == "payment_link.paid":
        _handle_payment_link_paid(db, event_data)
    return {"status": "ok"}


def _handle_order_paid(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("order", {}).get("entity", {})
    razorpay_order_id = entity.get("id")
    if not razorpay_order_id:
        return

    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()

    if order:
        order.status = "paid"
        db.commit()
        push_audit_event({
            "type" : "ORDER_PAID",
            "razorpay_order_id": razorpay_order_id,
            "amount" : entity.get("amount_paid",0) /100,
        })
        logger.info(f"Order {razorpay_order_id} marked as paid.")

def _handle_payment_captured(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    payment_id = entity.get("id")
    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()
    if order:
        order.status = "paid"
        order.razorpay_payment_id = payment_id
        db.commit()
        push_audit_event({
            "type": "PAYMENT_CAPTURED",
            "payment_id": payment_id,
            "amount_inr": entity.get("amount", 0) / 100,
        })
def _handle_payment_failed(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()
    if order:
        order.status = "failed"
        db.commit()
        push_audit_event({
            "type": "PAYMENT_FAILED",
            "razorpay_order_id": razorpay_order_id,
            "error": entity.get("error_description", "Unknown error"),
        })
def _handle_payment_link_paid(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment_link", {}).get("entity", {})
    reference_id = entity.get("reference_id")
    # reference_id is our internal order_id
    order = db.query(OrderRecord).filter(
        OrderRecord.order_id == reference_id
    ).first()
    if order:
        order.status = "paid"
        db.commit()
        push_audit_event({
            "type": "PAYMENT_LINK_PAID",
            "order_id": reference_id,
            "amount_inr": entity.get("amount", 0) / 100,
        })
        logger.info(f"Payment link paid for order {reference_id}.")

# Formatters

def _format_audit(r: AuditLogRecord) -> dict:
    return {
        "id": r.id,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        "event_type": r.event_type,
        "agent_id": r.agent_id,
        "product_id": r.product_id,
        "amount_inr": r.amount_inr,
        "policy_decision": r.policy_decision,
        "razorpay_order_id": r.razorpay_order_id,
        "razorpay_status": r.razorpay_status,
        "details": r.details,
        "error_message": r.error_message,
    }
def _format_order(r: OrderRecord) -> dict:
    return {
        "order_id": r.order_id,
        "agent_id": r.agent_id,
        "product_id": r.product_id,
        "quantity": r.quantity,
        "total_amount_inr": r.total_amount_inr,
        "status": r.status,
        "razorpay_order_id": r.razorpay_order_id,
        "razorpay_payment_id": r.razorpay_payment_id,
        "payment_link_url": r.payment_link_url,
        "shipping_address": r.shipping_address,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
def _format_mandate(r: AgentMandateRecord) -> dict:
    return {
        "agent_id": r.agent_id,
        "max_single_txn_inr": r.max_single_txn_inr,
        "max_daily_spend_inr": r.max_daily_spend_inr,
        "allowed_categories": r.allowed_categories,
        "requires_approval_above_inr": r.requires_approval_above_inr,
        "is_active": r.is_active,
        "expires_at": r.expires_at.isoformat() if r.expires_at else None,
    }