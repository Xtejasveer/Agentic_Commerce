"""
Run this script once to set up the database and populate the product catalog.
Usage:
    python seed_catalog.py
What it does:
    1. Creates all PostgreSQL tables (products, agent_mandates, orders, audit_log)
    2. Seeds 18 mock products into PostgreSQL
    3. Seeds the same products into ChromaDB for vector search
    4. Seeds 2 agent mandates for the demo
"""

import sys
import os 

# Make sure src is imporatable
sys.path.insert(0, os.path.dirname(__file__))

from src.database.session import engine, SessionLocal, Base
from src.database.models import ProductRecord, AgentMandateRecord
from src.database.vector import vector_db
from src.catalog.seed_data import PRODUCTS
from rich.console import Console
from rich.table import Table

console = Console()

def create_tables():
    console.print("\n[bold cyan] Creating databases tables... [/bold cyan]")
    Base.metadata.create_all(bind=engine)
    console.print("[green] Tables created [/green]")

def seed_products(db):
    console.print("\n [bold cyan] Seeding products into PostgreSQL... [/bold cyan]")

    from src.database.models import OrderRecord
    from src.database.models import AuditLogRecord

    # Clear dependents first to avoid foreign key constraints
    db.query(AuditLogRecord).delete()
    db.query(OrderRecord).delete()
    db.query(ProductRecord).delete()
    db.commit()

    for p in PRODUCTS:
        record = ProductRecord(
            product_id = p["product_id"],
            name = p["name"],
            description = p["description"],
            price_inr = p["price_inr"],
            stock_quantity = p["stock_quantity"],
            category = p["category"],
        )
        db.add(record)

    db.commit()
    console.print(f"[green]{len(PRODUCTS)} products seeded into PostgreSQL[/green]")

def seed_vector_db():
    console.print("\n[bold cyan]Seeding products into ChromaDB...[/bold cyan]")
    vector_db.delete_all()
    vector_db.add_products(PRODUCTS)
    console.print(f"[green]✓ {len(PRODUCTS)} products seeded into ChromaDB[/green]")

def seed_mandates(db):
    console.print("\n[bold cyan]Seeding agent mandates...[/bold cyan]")

    db.query(AgentMandateRecord).delete()
    db.commit()

    mandates = [
        AgentMandateRecord(
            agent_id = "agent-buyer-01",
            api_key = "key-buyer-01-secret",
            max_single_txn_inr = 5000.0,
            max_daily_spend_inr = 15000.0,
            allowed_categories=["chargers", "cables", "power_banks", "earbuds", "cases", "screen_protectors"],
            requires_approval_above_inr = 4000.0,
            is_active = True,
        ),
        AgentMandateRecord(
            # Restricted agent — used to demo policy rejections
            agent_id="agent-buyer-02",
            api_key="key-buyer-02-secret",
            max_single_txn_inr=2000.0,
            max_daily_spend_inr=5000.0,
            allowed_categories=["chargers"],
            requires_approval_above_inr=None,
            is_active=True,
        ),
    ]

    for m in mandates:
        db.add(m)
    db.commit()
    console.print("[green]2 Agent mandates seeded[/green]")

def print_summary(db):
    console.print("\n[bold yellow]── Catalog Summary ──────────────────────[/bold yellow]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Price (₹)", justify="right")
    table.add_column("Stock", justify="right")
    products = db.query(ProductRecord).all()
    for p in products:
        stock_display = f"[red]{p.stock_quantity}[/red]" if p.stock_quantity == 0 else str(p.stock_quantity)
        table.add_row(p.product_id, p.name[:45], p.category, f"₹{p.price_inr:,.0f}", stock_display)
    console.print(table)
    console.print(f"\n[bold green]✓ Seeding complete — {len(products)} products ready[/bold green]\n")
if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_tables()
        seed_products(db)
        seed_vector_db()
        seed_mandates(db)
        print_summary(db)
    finally:
        db.close()