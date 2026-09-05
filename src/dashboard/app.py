"""
FastAPI merchant dashboard application

Exposes the audit trail, order management, and Razorpay webhook receiver.
The React frontend (built with Vite) is served from frontend/dist/.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
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
    title="Agentic Commerce - Merchant Dashboard",
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
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to auto-migrate database: {e}")

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

# Mount the static assets (JS/CSS chunks) under /assets
_assets_dir = os.path.join(_frontend_dist, "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="react-assets")

# SPA fallback routes — serve index.html for all page routes
# React Router handles navigation client-side
@app.get("/")
def root(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login")
def login_page(request: Request):
    idx = _react_index()
    if idx:
        return FileResponse(idx)
    return RedirectResponse(url="/")

@app.get("/landing")
def landing_page():
    idx = _react_index()
    if idx:
        return FileResponse(idx)
    return RedirectResponse(url="/login")

@app.get("/demo")
def demo_page():
    idx = _react_index()
    if idx:
        return FileResponse(idx)
    return RedirectResponse(url="/login")

# Serve any other static files from frontend/dist root (favicon, etc.)
if os.path.isdir(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="react-root")
