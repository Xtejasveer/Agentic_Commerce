from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AgentMandate(BaseModel):
    """
    Defines an AI agent's spending authority.
    Stored in PostgreSQL and checked before every transaction.
    """

    agent_id: str = Field(..., description="Unique identifier for the AI buyer agent")
    api_key: str = Field(..., description="Secret ket the agent uses to authenticate")
    max_single_txn_inr: float = Field(..., description="Maximum amount per single transaction (INR)")
    max_daily_spend_inr : float = Field(..., description="Maximum total spend in a calendar day (INR)")

    allowed_categories: list[str] = Field(..., description="Product categories this agent may purchase from")
    requires_approval_above_inr : Optional[float] = Field(
        None, description="Transaction above this value require human approval"
    )
    is_active : bool = Field(True, description="Whether this mandate is currently active")
    expires_at: Optional[datetime] = Field(None, description="When this mandate expires (None = never)")

class MandateCheckRequest(BaseModel):
    """Input to the policy engine for a pre-purchase check."""
    agent_id: str
    api_key: str
    product_id: str
    addon_product_id: Optional[str] = None
    product_category: str
    quantity: int = Field(..., ge=1)
    total_amount_inr: float


class PolicyCheck(BaseModel):
    """Result of a single policy check step."""
    check: str = Field(..., description="Name of the check performed")
    passed: bool
    detail: str = Field(..., description="Human-readable explanation of the result")

class MandateCheckResult(BaseModel):
    """Full result of a mandate validation - returned to the MCP client."""
    approved: bool
    reason:str = Field(..., description = "Top-level approval or rejection reason")
    decision_trace: list[PolicyCheck] = Field(
        ..., description="Ordered list of every check performed with pass/fail"
    )
    remaining_daily_budget_inr :Optional[float] = Field(
        None, description="How much daily budget remains after this transaction"
    )
    requires_human_approval: bool = Field(False)
    warnings: list[str] = Field(default_factory=list)
    