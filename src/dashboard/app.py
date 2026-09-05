"""
FastAPI merchant dashboard application

Exposes the audit trail, order management, and Razorpay webhook receiver.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.dashboard.routes import router

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title = "Agentic Commerce - Merchant Dashboard",
    description = (
        "Real-time audit trail and order management for the AI-native merchant."
        "Every agent action is logged here - approvals, rejections, payments"
    ),
    version = "1.0.0"
)

# Allow browser access to SSE stream
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy import text
from src.database.session import Base, engine
import src.database.models # ensure models are registered

# Automatically create any newly added tables (e.g. users) and columns
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE agent_mandates ADD COLUMN IF NOT EXISTS user_id VARCHAR;"))
        conn.commit()
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to auto-migrate database: {e}")

# Set up templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

app.include_router(router, prefix="/api")

@app.get("/login")
def login_page(request: Request):
    # If already logged in, redirect to dashboard
    if request.cookies.get("agentic_session"):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/")
def root(request: Request):
    session_id = request.cookies.get("agentic_session")
    if not session_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request})
