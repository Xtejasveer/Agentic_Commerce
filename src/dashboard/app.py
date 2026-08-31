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

app.include_router(router, prefix= "/api")

@app.get("/")
def root():
    return {
        "service" :"Agentic Commerce Merchant Dashboard",
        "docs" : "/docs",
        "audit_trail" : "/api/audit",
        "live_stream" : "/api/audit/stream",
        "orders": "/api/orders",
        "mandates":"/api/mandates",
        "health":"/api/health", 
    }
