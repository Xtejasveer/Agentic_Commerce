from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


class AuditEventType(str, Enum):
    SEARCH = "SEARCH"
    POLICY_CHECK = "POLICY_CHECK"
    POLICY_APPROVED = "POLICY_APPROVED"
    POLICY_REJECTED = "POLICY_REJECTED"
    STOCK_RESERVED = "STOCK_RESERVED"
    STOCK_RELEASED = "STOCK_RELEASED"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    IDEMPOTENCY_BLOCK = "IDEMPOTENCY_BLOCK"
    UPSELL_SUGGESTED = "UPSELL_SUGGESTED"
    UPSELL_ACCEPTED = "UPSELL_ACCEPTED"
    UPSELL_REJECTED = "UPSELL_REJECTED"


class AuditEntry(BaseModel):
    """
    Immutable log record for every action taken by or on behalf of an agent.
    Written to PostgreSQL — never updated, only appended.
    """
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: AuditEventType
    agent_id: str
    product_id: Optional[str] = None
    amount_inr: Optional[float] = None
    policy_decision: Optional[bool] = Field(
        None, description="True=approved, False=rejected, None=N/A"
    )
    razorpay_order_id: Optional[str] = None
    razorpay_status: Optional[str] = None
    details: Optional[dict[str, Any]] = Field(
        None, description="Arbitrary JSON payload with event-specific context"
    )
    error_message: Optional[str] = None