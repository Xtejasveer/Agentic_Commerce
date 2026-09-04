from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum 

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_INITIATED = "payment_initiated"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PurchaseRequest(BaseModel):
    """An AI agent's request to purchase a product"""
    agent_id: str = Field(..., description="The buyer agent's id")
    api_key: str = Field(..., description="The buyer agent's API key")
    product_id: str = Field(..., description="SKU of the product to purchase")
    addon_product_id: Optional[str] = Field(None, description="Optional bundled addon SKU")
    quantity: int = Field(1, ge=1, description="Number of units to buy")
    shipping_address : str = Field(..., min_length = 10, description="Delivery address")

class PurchaseResult(BaseModel):
    """Outcome of a purchase — returned to the MCP client."""
    success: bool
    order_id: Optional[str] = Field(None, description="Internal order ID (from our database)")
    razorpay_order_id: Optional[str] = Field(None, description="Razorpay order ID (e.g. order_xxx)")
    payment_link_url: Optional[str] = Field(None, description="Razorpay short payment URL for checkout")
    status: OrderStatus
    total_amount_inr: Optional[float] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    error_message: Optional[str] = Field(None, description="Reason for failure if success=False")
    audit_id: Optional[str] = Field(None, description="ID of the audit log entry for this transaction")