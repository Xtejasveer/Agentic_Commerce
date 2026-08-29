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