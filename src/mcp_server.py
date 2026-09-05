"""
The merchant MCP Gateway - a FastMCP server exposing the product catalog 
and purchase tools to AI buyer agents.

"""

from fastmcp import FastMCP
from pydantic import Field
from typing import Optional
from src.database.session import SessionLocal
from src.catalog import service as catalog_service
from src.schemas.product import SearchResult, Product
from src.policy.engine import policy_engine
from src.schemas.mandate import MandateCheckRequest
from src.payments.service import execute_purchase as payment_service_execute
from src.schemas.order import PurchaseRequest
from src.schemas.audit import AuditEventType
# Server Initialization

mcp = FastMCP(
    name = "AgenticCommerceMerchant",
    instructions=(
        "You are connected to an AI-native electronics merchant."
        "Use search_products to find items, get_product_details to verify stock, "
        "validate_purchase_mandate to check your spending authority, "
        "and execute_purchase to complete a transaction. "
        "Always validate your mandate before attempting a purchase."
    ),
)

# Resources

@mcp.resource("catalog://categories")
def get_categories() -> str:
    """Lists all available product categories in this merchant's catalog."""
    db = SessionLocal()
    try:
        from src.database.models import ProductRecord
        from sqlalchemy import distinct
        categories = db.query(distinct(ProductRecord.category)).all()
        category_list = sorted([c[0] for c in categories])
        return "Available product categories:\n" + "\n".join(f"-{c}" for c in category_list)
    finally:
        db.close()

@mcp.resource("merchant://policies")
def get_merchant_policies() -> str:
    """Returns the merchant's spending and purchasing policies for AI agents."""
    return """
MERCHANT PURCHASING POLICIES
=============================
1. All AI buyers must have a registered mandate with a valid agent_id.
2. Each transaction must not exceed the agent's max_single_txn_inr limit.
3. Daily cumulative spend must not exceed max_daily_spend_inr.
4. Purchases are only allowed in the agent's approved product categories.
5. Out-of-stock items cannot be purchased.
6. Transactions above the approval threshold require human review.
7. Duplicate purchases within 5 minutes will be blocked (idempotency).
8. All actions are logged in an immutable audit trail.
PAYMENT FLOW
============
1. Call validate_purchase_mandate before any purchase attempt.
2. If approved, call execute_purchase to create the order.
3. A Razorpay payment link will be returned for checkout completion.
    """

# Tools

@mcp.tool()
def search_products(
    query: str = Field(..., description="Natural language product search(e.g. 'fast charger under 2000.')"),
    max_price: Optional[float] = Field(None, description="Maximum price in INR"),
    min_price: Optional[float] = Field(None, description="Minimum price in INR"),
    category: Optional[str] = Field(None, description="Filter by category (e.g. 'chargers', 'earbuds')"),
    limit: int = Field(5, ge=1 , le=10, description="Maximum number of results to return"),
) -> dict:
    """
    Search the merchant's product catalog using natural language.
    Returns a ranked list of matching products with pricing and stock information.
    Use this to find products before attempting a purchase.
    """
    db = SessionLocal()

    try:
        result: SearchResult = catalog_service.search_products(
            db= db,
            query = query,
            max_price=max_price,
            min_price=min_price,
            category=category,
            limit = limit,
        )
        catalog_service.log_audit_event(db, {
            "event_type": AuditEventType.SEARCH,
            "agent_id": "System",
            "details": {"query": query, "found": result.total_found, "category": category}
        })

        # Capture Unmet Demand Signals
        if result.total_found == 0:
            catalog_service.log_audit_event(db, {
                "event_type": AuditEventType.DEMAND_SIGNAL,
                "agent_id": "System",
                "details": {
                    "query": query,
                    "category": category,
                    "reason": "NO_MATCH",
                    "signal": f"Zero catalog matches found for query: '{query}'"
                }
            })
        else:
            for p in result.products:
                if p.stock_quantity == 0:
                    catalog_service.log_audit_event(db, {
                        "event_type": AuditEventType.DEMAND_SIGNAL,
                        "agent_id": "System",
                        "product_id": p.product_id,
                        "amount_inr": p.price_inr,
                        "details": {
                            "query": query,
                            "product_id": p.product_id,
                            "name": p.name,
                            "reason": "OUT_OF_STOCK",
                            "estimated_lost_revenue_inr": p.price_inr,
                            "signal": f"Out-of-stock query for '{p.name}' (Lost pipeline: ₹{p.price_inr:,.0f})"
                        }
                    })

        return {
            "query":result.query,
            "total_found":result.total_found,
            "products": [p.model_dump() for p in result.products],
        }
    finally:
        db.close()

@mcp.tool()
def get_product_details(
    product_id: str = Field(..., description="The product_id (SKU) to look up")
) -> dict:
    """
    Retrieve full details and live stock count for a specific product.
    Use this to confirm avalability before placing an order.
    """

    db = SessionLocal()
    try:
        product: Product | None = catalog_service.get_product(db= db, product_id=product_id)
        if not product:
            return {
                "found" : False,
                "error" : f"Product '{product_id}' not found in catalog.",
            }
        return {"found" : True, "product" : product.model_dump()}
    finally:
        db.close()
@mcp.tool()
def suggest_addon(
    product_id: str = Field(..., description="The primary product ID you are buying"),
) -> dict:
    """
    Get a relevant accessory or addon for a product to upsell the human.
    """
    db = SessionLocal()
    try:
        from src.catalog.service import get_product, log_audit_event
        # Multi-category upsell logic:
        # 1. Chargers & Power Banks -> Offer Anker 240W braided cable (prod-006)
        if product_id in ["prod-001", "prod-002", "prod-003", "prod-004", "prod-005", "prod-018", "prod-019", "prod-020", "prod-008", "prod-009", "prod-010", "prod-024"]: 
            addon = get_product(db, "prod-006")
            if addon:
                return {
                    "has_addon": True,
                    "addon_product_id": addon.product_id,
                    "name": addon.name,
                    "price_inr": addon.price_inr,
                    "merchant_pitch": "10% discount on this premium braided cable when bundled with a charger today! Highly recommended to maximize charging speed."
                }
        # 2. Mice -> Offer ergonomic memory foam mouse pad with wrist rest (prod-047)
        elif product_id in ["prod-044", "prod-045", "prod-046"]:
            addon = get_product(db, "prod-047")
            if addon:
                return {
                    "has_addon": True,
                    "addon_product_id": addon.product_id,
                    "name": addon.name,
                    "price_inr": addon.price_inr,
                    "merchant_pitch": "Bundle an ergonomic memory foam mouse pad with wrist rest to maximize precision and eliminate wrist fatigue."
                }
        # 3. Phone Cases -> Offer tempered glass screen protector (prod-016)
        elif product_id in ["prod-014", "prod-015"]:
            addon = get_product(db, "prod-016")
            if addon:
                return {
                    "has_addon": True,
                    "addon_product_id": addon.product_id,
                    "name": addon.name,
                    "price_inr": addon.price_inr,
                    "merchant_pitch": "Complete 360-degree protection: Add a 9H tempered glass screen protector to your order for just ₹499."
                }
        # 4. Keyboards -> Offer heavy-duty braided cable (prod-006)
        elif product_id in ["prod-041", "prod-042", "prod-043"]:
            addon = get_product(db, "prod-006")
            if addon:
                return {
                    "has_addon": True,
                    "addon_product_id": addon.product_id,
                    "name": addon.name,
                    "price_inr": addon.price_inr,
                    "merchant_pitch": "Upgrade your desk setup with a high-durability braided cable to power your mechanical keyboard."
                }

        return {"has_addon": False}
    finally:
        db.close()

@mcp.tool()
def validate_purchase_mandate(
    agent_id : str = Field(..., description="Your agent ID registered with this merchant."),
    agent_api_key: str = Field(..., description="The secret API key of your agent."),
    product_id: str = Field(..., description="The product_id you intend to purchase"),
    product_category: str = Field(..., description="The category fo the product (from get_product_details)"),
    total_amount_inr: float = Field(..., description="Total cost in INR (price x quantity)"),
    addon_product_id: Optional[str] = Field(None, description="Optional addon product ID to bundle"),
    quantity: int = Field(1, ge=1, description = "Number of units you want to buy"),
) -> dict:
    """
    Check whether your agent mandate authorizes a specific purchase.
    Always call this before execute_purchase.

    Returns a full decision an explainable trace of every policy check
    performed - whether or rejected, you will know exactly why.
    """
    db = SessionLocal()
    try:
        request = MandateCheckRequest(
            agent_id = agent_id,
            api_key=agent_api_key,
            product_id=product_id,
            addon_product_id=addon_product_id,
            product_category=product_category,
            quantity=quantity,
            total_amount_inr=total_amount_inr,
        )
        result = policy_engine.validate(db=db, request=request)
        return result.model_dump()
    finally:
        db.close()

@mcp.tool()
def execute_purchase(
    agent_id: str = Field(..., description="Your agent ID"),
    agent_api_key: str = Field(..., description="The secret API key of your agent."),
    product_id: str = Field(..., description="The product_id to purchase (from search results)"),
    shipping_address: str = Field(..., description="Delivery address (minimum 10 characters)"),
    addon_product_id: Optional[str] = Field(None, description="Optional addon product ID to bundle"),
    quantity: int = Field(1, ge=1, description="Number of units to buy"),
) -> dict:
    """
    Execute a complete purchase — policy check, stock reservation, and Razorpay payment link.
    IMPORTANT: Call validate_purchase_mandate first to confirm approval.
    This tool will also re-validate internally as a safety measure.
    On success: returns a payment_link_url the user can open to complete payment.
    On failure: returns success=False with a clear error_message explaining why.
    """
    db = SessionLocal()
    try:
        request = PurchaseRequest(
            agent_id=agent_id,
            api_key = agent_api_key,
            product_id=product_id,
            addon_product_id=addon_product_id,
            quantity=quantity,
            shipping_address=shipping_address,
        )
        result = payment_service_execute(db=db, request=request)
        return result.model_dump()
    finally:
        db.close()

if __name__ == "__main__":
    # Run in stdio mode — used when spawned as subprocess by the buyer agent
    mcp.run(transport="stdio")