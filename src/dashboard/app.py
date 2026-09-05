"""
FastAPI merchant dashboard application

Exposes the audit trail, order management, and Razorpay webhook receiver.
The React frontend (built with Vite) is served from frontend/dist/.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from src.database.session import Base, engine
import src.database.models  # ensure models are registered
from src.dashboard.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="VendIQ - Merchant Dashboard",
    description=(
        "Real-time audit trail and order management for the AI-native merchant."
        "Every agent action is logged here - approvals, rejections, payments"
    ),
    version="1.0.0"
)

# Allow browser access to SSE stream
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically create any newly added tables (e.g. users) and columns
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE agent_mandates ADD COLUMN IF NOT EXISTS user_id VARCHAR;"))
        conn.commit()

    # Auto-seed if database catalog is empty
    from src.database.session import SessionLocal
    from src.database.models import ProductRecord, AgentMandateRecord
    from src.catalog.seed_data import PRODUCTS
    from src.database.vector import vector_db

    with SessionLocal() as db:
        if db.query(ProductRecord).count() == 0:
            logging.getLogger(__name__).info("Database catalog is empty. Auto-seeding 50 products...")
            for p in PRODUCTS:
                db.add(ProductRecord(
                    product_id=p["product_id"],
                    name=p["name"],
                    description=p["description"],
                    price_inr=p["price_inr"],
                    stock_quantity=p["stock_quantity"],
                    category=p["category"],
                ))
            db.commit()
            logging.getLogger(__name__).info("50 products seeded into PostgreSQL.")

        try:
            if vector_db.collection.count() == 0:
                logging.getLogger(__name__).info("ChromaDB vector collection is empty. Seeding embeddings...")
                vector_db.add_products(PRODUCTS)
                logging.getLogger(__name__).info("50 products seeded into ChromaDB.")
        except Exception as ve:
            logging.getLogger(__name__).warning(f"ChromaDB auto-seed notice: {ve}")

        if db.query(AgentMandateRecord).count() == 0:
            db.add(AgentMandateRecord(
                agent_id="agent-buyer-01",
                api_key="key-buyer-01-secret",
                max_single_txn_inr=5000.0,
                max_daily_spend_inr=15000.0,
                allowed_categories=[
                    "chargers", "cables", "power_banks", "earbuds", "headphones",
                    "speakers", "smartwatches", "keyboards", "mice", "storage",
                    "cases", "screen_protectors"
                ],
                requires_approval_above_inr=4000.0,
                is_active=True,
            ))
            db.add(AgentMandateRecord(
                agent_id="agent-buyer-02",
                api_key="key-buyer-02-secret",
                max_single_txn_inr=2000.0,
                max_daily_spend_inr=5000.0,
                allowed_categories=["chargers"],
                requires_approval_above_inr=None,
                is_active=True,
            ))
            db.commit()
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to auto-migrate/seed database: {e}")

# Mount API router
app.include_router(router, prefix="/api")

# ─── Serve React SPA ─────────────────────────────────────────────────────────
# Determine the path to the built React app
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_here, "..", ".."))
_frontend_dist = os.path.join(_project_root, "frontend", "dist")

def _react_index():
    """Return path to React index.html, or None if build doesn't exist."""
    idx = os.path.join(_frontend_dist, "index.html")
    return idx if os.path.exists(idx) else None

def _serve_spa():
    idx = _react_index()
    if idx and os.path.exists(idx):
        return FileResponse(idx)
    return HTMLResponse(
        "<h2>Frontend build initializing or not found. Please ensure frontend/dist is present.</h2>",
        status_code=503
    )

# Mount the static assets (JS/CSS chunks) under /assets
_assets_dir = os.path.join(_frontend_dist, "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="react-assets")

# SPA page routes — React Router handles navigation client-side
@app.get("/")
def root():
    return _serve_spa()

@app.get("/login")
def login_page():
    return _serve_spa()

@app.get("/landing")
def landing_page():
    return _serve_spa()

@app.get("/demo")
def demo_page():
    return _serve_spa()

# Serve any other static files from frontend/dist root (favicon, icons, etc.)
if os.path.isdir(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="react-root")

