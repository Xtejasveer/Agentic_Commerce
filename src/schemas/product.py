from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    """Full product representation returned from the catalog."""
    product_id: str = Field(..., description="Unique product SKU")
    name: str = Field(..., description="Product display name")
    description: str = Field(..., description="Rich text description used for semantic search")
    price_inr: float = Field(..., gt =0, description="Price in Indian Rupees")
    stock_quantity : int = Field(..., ge=0, description="Units available in inventory")
    category: str = Field(..., description = "Product category (eg. chargers, earbuds)")
    image_url: Optional[str] = Field(None, description="Optional product image URL")

class SearchQuery(BaseModel):
    """Input from an AI agent performing a product search"""
    query_text: str = Field(..., description="Natural language search query")
    max_price: Optional[float] = Field(None, description="Maximum price in INR (inclusive)")
    min_price: Optional[float] = Field(None, description="Minimum price in INR (inclusive)")
    category: Optional[str] = Field(None, description="Filter by product category")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results to return")

class SearchResult(BaseModel):
    """Structured response from a catalog search."""
    products :list[Product] = Field(..., description="Matching products ordered by relevance")
    total_found: int = Field(..., description="Number of products returned")
    query: str = Field(..., description= "The original search query")
    