from sqlalchemy.orm import Session
from sqlalchemy import func, Date
from src.database.vector import vector_db
from src.database.models import ProductRecord, AuditLogRecord
from src.schemas.product import Product, SearchResult
from src.schemas.audit import AuditEventType
from datetime import datetime
import uuid

def _record_to_product(record: ProductRecord) -> Product:
    """Convert a SQLAlchemy ProductRecord to a Pydantic Product schema."""
    return Product(
        product_id=record.product_id,
        name = record.name,
        description= record.description,
        price_inr=record.price_inr,
        stock_quantity=record.stock_quantity,
        category=record.category,
        image_url = record.image_url,
    )

def search_products(
        db: Session,
        query: str,
        max_price: float | None = None,
        min_price: float | None = None,
        category: str | None = None,
        limit : int = 5,
) -> SearchResult:
    """
    Semantic product search via ChromaDB, enriched with live stock from PostgrSQL.
    ChromaDB handles relevance ranking; PostgreSQL provides authoritative stock data.
    """
    chroma_results = vector_db.search(
        query_string = query,
        n_results = limit,
        max_price=max_price,
        min_price=min_price,
        category = category,
    )

    if not chroma_results:
        return SearchResult(products=[], total_found=0, query=query)

    product_ids = [r["product_id"] for r in chroma_results]
    pg_records = db.query(ProductRecord).filter(
        ProductRecord.product_id.in_(product_ids)
    ).all()

    pg_map = {r.product_id: r for r in pg_records}

    products =[]
    for chroma_item in chroma_results:
        pid = chroma_item["product_id"]
        pg = pg_map.get(pid)
        if not pg:
            continue
        products.append(_record_to_product(pg))

    return SearchResult(products=products, total_found=len(products), query = query)

def get_product(db:Session, product_id: str) -> Product | None:
    """Fetch a single product by ID from PostgreSQL"""
    record = db.query(ProductRecord).filter(
        ProductRecord.product_id == product_id
    ).first()
    if not record:
        return None
    return _record_to_product(record)

def check_stock(db: Session, product_id: str, quantity: int) -> bool:
    """Record True if sufficient stock is available."""
    record = db.query(ProductRecord).filter(
        ProductRecord.product_id == product_id
    ).first()
    if not record:
        return False
    return record.stock_quantity >= quantity

def reserve_stock(db: Session, product_id: str, quantity: int) -> bool:
    """
    Automatically decrements stock in both PostgreSQL and ChromaDB.
    Returns False if stock is insufficient (does not raise).
    """

    record = db.query(ProductRecord).filter(
        ProductRecord.product_id == product_id
    ).with_for_update().first()

    if not record or record.stock_quantity < quantity:
        return False

    record.stock_quantity -= quantity
    db.commit()

    # Keep ChromaDB metadata in sync 
    vector_db.update_stock(product_id, record.stock_quantity)
    return True

def release_stock(db: Session, product_id: str, quantity: int):
    """
    Releases previously reserved stock on payment failure.
    Called during the rollback path in the payment service.
    """

    record = db.query(ProductRecord).filter(
        ProductRecord.product_id == product_id
    ).with_for_update().first()

    if not record:
        return 

    record.stock_quantity += quantity
    db.commit()

    vector_db.update_stock(product_id, record.stock_quantity)

def log_audit_event(db: Session, entry: dict):
    """Write an immutable audit entry to PostgreSQL."""
    record = AuditLogRecord(
        id=str(uuid.uuid4()),
        event_type=entry.get("event_type"),
        agent_id=entry.get("agent_id"),
        product_id=entry.get("product_id"),
        amount_inr=entry.get("amount_inr"),
        policy_decision=entry.get("policy_decision"),
        razorpay_order_id=entry.get("razorpay_order_id"),
        razorpay_status=entry.get("razorpay_status"),
        details=entry.get("details"),
        error_message=entry.get("error_message"),
    )
    db.add(record)
    db.commit()
    return record.id