from sqlalchemy import (
    Column, String, Float, Integer, Boolean,
    DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from src.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class ProductRecord(Base):
    """Relational mirror of the ChromaDB catalog - used for SQL queries."""
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price_inr = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentMandateRecord(Base):
    """Spending authority granted to an AI buyer agent."""
    __tablename__ = "agent_mandates"

    agent_id = Column(String, primary_key=True)
    api_key = Column(String, nullable=False)
    max_single_txn_inr = Column(Float, nullable=False)
    max_daily_spend_inr = Column(Float, nullable=False)
    allowed_categories = Column(JSON, nullable = False)
    requires_approval_above_inr = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone = True), server_default=func.now())

class OrderRecord(Base):
    """Every purchase attempt - sucessfull or not."""
    __tablename__ = "orders"

    order_id = Column(String, primary_key = True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agent_mandates.agent_id"), nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount_inr = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    payment_link_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLogRecord(Base):
    """Append-only audit trail - every agent action is logged here.
    Never updated, only inserted."""

    __tablename__= "audit_log"
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    event_type = Column(String(50), nullable = False)
    agent_id = Column(String, nullable = False)
    product_id = Column(String, nullable=True)
    amount_inr = Column(Float, nullable = True)
    policy_decision = Column(Boolean, nullable=True)
    razorpay_order_id = Column(String, nullable=True)
    razorpay_status = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
