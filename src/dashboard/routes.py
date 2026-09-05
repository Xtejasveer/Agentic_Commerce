"""
FastAPI route handlers for the merchant dashboard.
Provides the audit trail, order management, and Razorpay webhook receiver.
"""
import json
import asyncio
import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Response
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, cast, Date
from typing import Optional
import hashlib
import secrets
import urllib.request
import urllib.parse

from src.database.session import get_db
from src.database.models import AuditLogRecord, OrderRecord, AgentMandateRecord, ProductRecord, UserRecord
from src.payments.razorpay_client import verify_webhook_signature
from src.config import settings
from pydantic import BaseModel, EmailStr
from src.agent.buyer import run_buyer_agent

logger = logging.getLogger(__name__)
router = APIRouter()

# Password hashing utilities
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, key_hex = stored_hash.split("$", 1)
    test_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return secrets.compare_digest(key_hex, test_key.hex())

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[UserRecord]:
    user_id = request.cookies.get("agentic_session")
    if not user_id:
        return None
    return db.query(UserRecord).filter(UserRecord.id == user_id).first()

# Auth Schemas
class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleTokenRequest(BaseModel):
    credential: str

## Auth Endpoints
@router.post("/auth/register")
def register_user(req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    existing = db.query(UserRecord).filter(UserRecord.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    user = UserRecord(
        email=clean_email,
        name=req.name.strip(),
        password_hash=hash_password(req.password),
        avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={clean_email}",
        auth_provider="local"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response.set_cookie(key="agentic_session", value=user.id, httponly=True, samesite="lax", max_age=86400*7)
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": user.name, "avatar_url": user.avatar_url}}

@router.post("/auth/login")
def login_user(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(UserRecord).filter(UserRecord.email == clean_email).first()
    if not user or not verify_password(user.password_hash or "", req.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    response.set_cookie(key="agentic_session", value=user.id, httponly=True, samesite="lax", max_age=86400*7)
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": user.name, "avatar_url": user.avatar_url}}

@router.get("/auth/google/config")
def get_google_config():
    """Returns whether Google OAuth is configured and its client ID."""
    return {
        "configured": bool(settings.GOOGLE_CLIENT_ID),
        "client_id": settings.GOOGLE_CLIENT_ID or ""
    }

@router.get("/auth/google/login")
def google_oauth_login(request: Request):
    """Redirects the browser to Google's real OAuth 2.0 consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        return RedirectResponse(url="/login?error=google_not_configured")
    
    redirect_uri = f"{str(request.base_url).rstrip('/')}/api/auth/google/callback"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    google_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=google_url)

@router.get("/auth/google/callback")
def google_oauth_callback(code: Optional[str] = None, error: Optional[str] = None, request: Request = None, db: Session = Depends(get_db)):
    """Handles Google OAuth callback, exchanges code for user profile, and creates session."""
    if error or not code:
        return RedirectResponse(url=f"/login?error={error or 'cancelled'}")
    
    redirect_uri = f"{str(request.base_url).rstrip('/')}/api/auth/google/callback"
    
    # 1. Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = urllib.parse.urlencode({
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    try:
        token_req = urllib.request.Request(token_url, data=token_payload, method="POST")
        with urllib.request.urlopen(token_req) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
        
        access_token = token_data.get("access_token")
        
        # 2. Fetch user profile from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_req = urllib.request.Request(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
        with urllib.request.urlopen(user_req) as resp:
            user_info = json.loads(resp.read().decode("utf-8"))
        
        email = user_info["email"].lower().strip()
        name = user_info.get("name", email.split("@")[0])
        avatar_url = user_info.get("picture")

        # 3. Create or find user in PostgreSQL
        user = db.query(UserRecord).filter(UserRecord.email == email).first()
        if not user:
            user = UserRecord(
                email=email,
                name=name,
                avatar_url=avatar_url,
                auth_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
                db.commit()

        # 4. Set session cookie and redirect to dashboard
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="agentic_session", value=user.id, httponly=True, samesite="lax", max_age=86400*7)
        return response

    except Exception as e:
        logger.error(f"Google OAuth exchange error: {e}")
        return RedirectResponse(url="/login?error=oauth_failed")

@router.post("/auth/google/token")
def google_token_verify(req: GoogleTokenRequest, response: Response, db: Session = Depends(get_db)):
    """Verifies a Google Identity Services (GIS) ID token and creates session."""
    try:
        verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={req.credential}"
        with urllib.request.urlopen(verify_url) as resp:
            token_info = json.loads(resp.read().decode("utf-8"))
        
        if "email" not in token_info:
            raise HTTPException(status_code=400, detail="Invalid Google token payload.")
        
        email = token_info["email"].lower().strip()
        name = token_info.get("name", email.split("@")[0])
        avatar_url = token_info.get("picture")

        user = db.query(UserRecord).filter(UserRecord.email == email).first()
        if not user:
            user = UserRecord(
                email=email,
                name=name,
                avatar_url=avatar_url,
                auth_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        response.set_cookie(key="agentic_session", value=user.id, httponly=True, samesite="lax", max_age=86400*7)
        return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": user.name, "avatar_url": user.avatar_url}}

    except Exception as e:
        logger.error(f"Google ID token verification failed: {e}")
        raise HTTPException(status_code=400, detail=f"Google token verification failed: {str(e)}")

@router.post("/auth/logout")
def logout_user(response: Response):
    response.delete_cookie("agentic_session")
    return {"status": "logged_out"}

@router.get("/auth/me")
def get_auth_me(current_user: Optional[UserRecord] = Depends(get_current_user)):
    if not current_user:
        return {"user": None}
    return {"user": {"id": current_user.id, "email": current_user.email, "name": current_user.name, "avatar_url": current_user.avatar_url}}

# In-memory queue for SSE - audit events are pushed here and streamed to clients
_sse_queue: asyncio.Queue = asyncio.Queue()

class ChatRequest(BaseModel):
    agent_id: str
    message: str

class CreateMandateRequest(BaseModel):
    agent_id: str
    max_single_txn_inr: float
    max_daily_spend_inr: float
    allowed_categories: list[str]
    requires_approval_above_inr: Optional[float] = None

@router.get("/mandates")
def list_agent_mandates(request: Request, db: Session = Depends(get_db)):
    """List all active agent mandates scoped to the authenticated user, or public demo mandates."""
    current_user = get_current_user(request, db)
    query = db.query(AgentMandateRecord).filter(AgentMandateRecord.is_active == True)
    
    if current_user:
        # Show user's agents plus legacy/system agents where user_id is None
        from sqlalchemy import or_
        query = query.filter(or_(AgentMandateRecord.user_id == current_user.id, AgentMandateRecord.user_id == None))

    mandates = query.all()
    return [
        {
            "agent_id": m.agent_id,
            "max_single_txn_inr": m.max_single_txn_inr,
            "max_daily_spend_inr": m.max_daily_spend_inr,
            "allowed_categories": m.allowed_categories,
            "requires_approval_above_inr": m.requires_approval_above_inr,
            "is_owner": (m.user_id == current_user.id) if current_user else False,
        }
        for m in mandates
    ]

@router.post("/mandates")
def create_agent_mandate(req: CreateMandateRequest, request: Request, db: Session = Depends(get_db)):
    """Create or update an agent mandate in PostgreSQL assigned to the current user."""
    clean_id = req.agent_id.strip().lower().replace(" ", "-")
    current_user = get_current_user(request, db)
    user_id = current_user.id if current_user else None

    existing = db.query(AgentMandateRecord).filter(AgentMandateRecord.agent_id == clean_id).first()
    if existing:
        existing.max_single_txn_inr = req.max_single_txn_inr
        existing.max_daily_spend_inr = req.max_daily_spend_inr
        existing.allowed_categories = req.allowed_categories
        existing.requires_approval_above_inr = req.requires_approval_above_inr
        existing.is_active = True
        if user_id:
            existing.user_id = user_id
        db.commit()
        return {"status": "updated", "agent_id": clean_id, "api_key": existing.api_key}

    api_key = f"key-{clean_id}-secret"
    new_record = AgentMandateRecord(
        agent_id=clean_id,
        user_id=user_id,
        api_key=api_key,
        max_single_txn_inr=req.max_single_txn_inr,
        max_daily_spend_inr=req.max_daily_spend_inr,
        allowed_categories=req.allowed_categories,
        requires_approval_above_inr=req.requires_approval_above_inr,
        is_active=True,
    )
    db.add(new_record)
    db.commit()
    return {"status": "created", "agent_id": clean_id, "api_key": api_key}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Runs the LangGraph buyer agent in the background and returns its response.
    Dynamically looks up the agent's real credentials from PostgreSQL.
    """
    try:
        # Dynamically look up the agent's real API key from PostgreSQL
        mandate = db.query(AgentMandateRecord).filter(
            AgentMandateRecord.agent_id == request.agent_id
        ).first()
        api_key = mandate.api_key if mandate else f"key-{request.agent_id}-secret"
        
        # Run agent
        state = await run_buyer_agent(
            user_request=request.message,
            agent_id=request.agent_id,
            api_key=api_key
        )
        
        # Check for error or final response
        if state.get("error"):
            return {"response": f"❌ Purchase could not be completed.\n\nReason: {state['error']}"}
        
        final_msg = state.get("final_response")
        if not final_msg:
            # Fallback to last message
            if state.get("messages"):
                final_msg = state["messages"][-1].content
            else:
                final_msg = "Task completed."
                
        return {"response": final_msg}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": f"❌ Error running agent: {str(e)}"}

## Health 
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Confirms the server and database are reachable"""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status" : "ok", "database" : "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e}")

## Audit trail
@router.get("/audit")
def get_audit_trail(
    limit: int = 50,
    offset: int = 0,
    agent_id : Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Returns the paginated audit trail, most recent first.
    Optionally filter by agent_id or event_type
    """

    query = db.query(AuditLogRecord).order_by(desc(AuditLogRecord.timestamp))

    if agent_id:
        query = query.filter(AuditLogRecord.agent_id == agent_id)
    if event_type:
        query = query.filter(AuditLogRecord.event_type == event_type.upper())

    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {
        "total" : total,
        "offset" : offset,
        "limit": limit,
        "entries": [_format_audit(r) for r in records]
    }

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated business intelligence metrics:
    - Unmet demand signals (count & estimated lost pipeline)
    - Recovered sales (count & recovered revenue)
    - Upsell metrics (accepted vs rejected count)
    """
    from sqlalchemy import func
    
    # Demand signals
    demand_count = db.query(func.count(AuditLogRecord.id)).filter(
        AuditLogRecord.event_type == "DEMAND_SIGNAL"
    ).scalar() or 0
    
    unmet_revenue = db.query(func.coalesce(func.sum(AuditLogRecord.amount_inr), 0)).filter(
        AuditLogRecord.event_type == "DEMAND_SIGNAL"
    ).scalar() or 0.0

    # Recovered sales
    recovered_count = db.query(func.count(AuditLogRecord.id)).filter(
        AuditLogRecord.event_type == "SALE_RECOVERED"
    ).scalar() or 0

    recovered_revenue = db.query(func.coalesce(func.sum(AuditLogRecord.amount_inr), 0)).filter(
        AuditLogRecord.event_type == "SALE_RECOVERED"
    ).scalar() or 0.0

    # Upsells
    upsells_accepted = db.query(func.count(AuditLogRecord.id)).filter(
        AuditLogRecord.event_type == "UPSELL_ACCEPTED"
    ).scalar() or 0

    upsells_rejected = db.query(func.count(AuditLogRecord.id)).filter(
        AuditLogRecord.event_type == "UPSELL_REJECTED"
    ).scalar() or 0

    return {
        "unmet_demand_count": demand_count,
        "unmet_demand_revenue_inr": float(unmet_revenue),
        "recovered_sales_count": recovered_count,
        "recovered_sales_revenue_inr": float(recovered_revenue),
        "upsells_accepted": upsells_accepted,
        "upsells_rejected": upsells_rejected,
    }

@router.get("/audit/stream")
async def stream_audit_events(request: Request):
    """
    Server-Sent events (SSE) endpoint- streams audit events in real time.
    """

    async def event_generator():
        yield "data: {\"type\": \"connected\", \"message\": \"Audit stream live\"}\n\n"
        
        from datetime import datetime, timezone
        from src.database.session import SessionLocal
        
        last_timestamp = datetime.now(timezone.utc)
        
        while True:
            if await request.is_disconnected():
                break
            try:
                await asyncio.sleep(0.5)
                with SessionLocal() as db:
                    new_records = db.query(AuditLogRecord).filter(AuditLogRecord.timestamp > last_timestamp).order_by(AuditLogRecord.timestamp.asc()).all()
                    if new_records:
                        for r in new_records:
                            event = _format_audit(r)
                            yield f"data: {json.dumps(event)}\n\n"
                            last_timestamp = r.timestamp
                    else:
                        # Send heartbeat occasionally
                        yield "data: {\"type\": \"heartbeat\"}\n\n"
            except Exception as e:
                logger.error(f"SSE Error: {e}")
                await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

def push_audit_event(event: dict):
    """
    Called whenever a new audit entry is written.
    Pushes it to the SSE queue so connected dashboard clients see it instantly.
    """
    try:
        _sse_queue.put_nowait(event)
    except asyncio.QueueFull:
        pass
# Orders

@router.get("/orders")
def get_orders(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns all orders with optional filtering by status or agent."""
    query = db.query(OrderRecord).order_by(desc(OrderRecord.created_at))

    if status:
        query = query.filter(OrderRecord.status == status)
    if agent_id:
        query = query.filter(OrderRecord.agent_id == agent_id)

    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {
        "total" : total,
        "orders" : [_format_order(r) for r in records]
    }

@router.get("/orders/{order_id}")
def get_order(order_id: str, db:Session = Depends(get_db)):
    """Returns full details for a single order."""
    record = db.query(OrderRecord).filter(OrderRecord.order_id == order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return _format_order(record)

# Mandates

@router.get("/mandates")
def get_mandates(db: Session = Depends(get_db)):
    """Returns all registered agent mandates.""" 
    records = db.query(AgentMandateRecord).all()
    return {"mandates" : [_format_mandate(r) for r in records]}

@router.get("/mandates/{agent_id}/spend")
def get_agent_spend (agent_id: str, db:Session = Depends(get_db)):
    """
    Returns an agent's spend summary - today's total, all-time total,
    and remaining daily budget.
    """
    mandate = db.query(AgentMandateRecord).filter(
        AgentMandateRecord.agent_id == agent_id
    ).first()

    if not mandate:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    today = date.today()

    today_spend = db.query(
        func.coalesce(func.sum(OrderRecord.total_amount_inr),0)
    ).filter(
        OrderRecord.agent_id == agent_id,
        OrderRecord.status.in_(["paid", "payment_initiated"]),
        cast(OrderRecord.created_at, Date) == today,
    ).scalar()

    all_time_spend = db.query(
        func.coalesce(func.sum(OrderRecord.total_amount_inr),0)
    ).filter(
        OrderRecord.agent_id == agent_id,
        OrderRecord.status.in_(["paid","payment_initiated"])
    ).scalar()

    today_spend = float(today_spend or 0)
    all_time_spend = float(all_time_spend or 0)

    return {
        "agent_id": agent_id,
        "today_spend_inr": today_spend,
        "all_time_spend_inr": all_time_spend,
        "daily_limit_inr": mandate.max_daily_spend_inr,
        "remaining_today_inr": max(0, mandate.max_daily_spend_inr - today_spend),
        "single_txn_limit_inr": mandate.max_single_txn_inr,
        "allowed_categories": mandate.allowed_categories,
    }

# Razorpay Webhook

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias = "X-Razorpay-Signature"),
    db: Session = Depends(get_db)
):
    """
    Receives and processes Razorpay Webhook events.

    IMPORTANT: Uses the raw reuest body for signature verification -
    do NOT parse the body before verifying.
    """

    raw_body = await request.body()

    # verify webhook signature
    if x_razorpay_signature and settings.RAZORPAY_WEBHOOK_SECRET != "mock_webhook_secret":
        is_valid = verify_webhook_signature(
            body = raw_body.decode("utf=8"),
            signature = x_razorpay_signature,
            secret=settings.RAZORPAY_WEBHOOK_SECRET,
        )
        if not is_valid:
            logger.warning("Received webhook with invalid signature - rejected")
            raise HTTPException(status_code=400, detail="Invalid webhooks signature.")

    event_data = json.loads(raw_body)
    event_type = event_data.get("event", "unknown")
    logger.info(f"Webhook received: {event_type}")

    # Handle Event types

    if event_type == "order_paid":
        _handle_order_paid(db, event_data)

    elif event_type == "payment.captured":
        _handle_payment_captured(db, event_data)
    elif event_type == "payment.failed":
        _handle_payment_failed(db, event_data)
    elif event_type == "payment_link.paid":
        _handle_payment_link_paid(db, event_data)
    return {"status": "ok"}


def _handle_order_paid(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("order", {}).get("entity", {})
    razorpay_order_id = entity.get("id")
    if not razorpay_order_id:
        return

    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()

    if order:
        order.status = "paid"
        db.commit()
        push_audit_event({
            "type" : "ORDER_PAID",
            "razorpay_order_id": razorpay_order_id,
            "amount" : entity.get("amount_paid",0) /100,
        })
        logger.info(f"Order {razorpay_order_id} marked as paid.")

def _handle_payment_captured(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    payment_id = entity.get("id")
    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()
    if order:
        order.status = "paid"
        order.razorpay_payment_id = payment_id
        db.commit()
        push_audit_event({
            "type": "PAYMENT_CAPTURED",
            "payment_id": payment_id,
            "amount_inr": entity.get("amount", 0) / 100,
        })
def _handle_payment_failed(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    order = db.query(OrderRecord).filter(
        OrderRecord.razorpay_order_id == razorpay_order_id
    ).first()
    if order:
        order.status = "failed"
        db.commit()
        push_audit_event({
            "type": "PAYMENT_FAILED",
            "razorpay_order_id": razorpay_order_id,
            "error": entity.get("error_description", "Unknown error"),
        })
def _handle_payment_link_paid(db: Session, event_data: dict):
    entity = event_data.get("payload", {}).get("payment_link", {}).get("entity", {})
    reference_id = entity.get("reference_id")
    # reference_id is our internal order_id
    order = db.query(OrderRecord).filter(
        OrderRecord.order_id == reference_id
    ).first()
    if order:
        order.status = "paid"
        db.commit()
        push_audit_event({
            "type": "PAYMENT_LINK_PAID",
            "order_id": reference_id,
            "amount_inr": entity.get("amount", 0) / 100,
        })
        logger.info(f"Payment link paid for order {reference_id}.")

# Formatters

def _format_audit(r: AuditLogRecord) -> dict:
    return {
        "id": r.id,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        "event_type": r.event_type,
        "agent_id": r.agent_id,
        "product_id": r.product_id,
        "amount_inr": r.amount_inr,
        "policy_decision": r.policy_decision,
        "razorpay_order_id": r.razorpay_order_id,
        "razorpay_status": r.razorpay_status,
        "details": r.details,
        "error_message": r.error_message,
    }
def _format_order(r: OrderRecord) -> dict:
    return {
        "order_id": r.order_id,
        "agent_id": r.agent_id,
        "product_id": r.product_id,
        "quantity": r.quantity,
        "total_amount_inr": r.total_amount_inr,
        "status": r.status,
        "razorpay_order_id": r.razorpay_order_id,
        "razorpay_payment_id": r.razorpay_payment_id,
        "payment_link_url": r.payment_link_url,
        "shipping_address": r.shipping_address,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
def _format_mandate(r: AgentMandateRecord) -> dict:
    return {
        "agent_id": r.agent_id,
        "max_single_txn_inr": r.max_single_txn_inr,
        "max_daily_spend_inr": r.max_daily_spend_inr,
        "allowed_categories": r.allowed_categories,
        "requires_approval_above_inr": r.requires_approval_above_inr,
        "is_active": r.is_active,
        "expires_at": r.expires_at.isoformat() if r.expires_at else None,
    }