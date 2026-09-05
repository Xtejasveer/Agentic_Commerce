"""
The Policy Engine - deterministic, explainable spending authorzation.

Every purchase attempt must pass through here before any money moves.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, date, timezone, timedelta
from src.database.models import AgentMandateRecord, OrderRecord, AuditLogRecord
from src.schemas.mandate import MandateCheckRequest, MandateCheckResult, PolicyCheck
from src.schemas.audit import AuditEventType
from src.catalog.service import log_audit_event
import uuid

class PolicyEngine:

    def validate(
        self,
        db: Session,
        request: MandateCheckRequest,
    ) -> MandateCheckResult:
        """
        Runs all policy checks in order and returns a full decision with trace.
        Stops at the first failure - remaining checks are skipped.
        Short-circuit evaluation ensures clear, acionable rejectio reasons.
        """

        trace: list[PolicyCheck] =[]
        warnings: list[str] = []

        ## Check-1 : Identity and Auth check
        mandate = db.query(AgentMandateRecord).filter(
            AgentMandateRecord.agent_id == request.agent_id
        ).first()

        if not mandate or mandate.api_key != request.api_key:
            trace.append(PolicyCheck(
                check = "agent_auth",
                passed = False,
                detail = f"Agent '{request.agent_id}' not found or invalid API key."
            ))
            return self._reject("UNAUTHORIZED", trace, warnings, db, request)

        trace.append(PolicyCheck(
            check = "agent_auth",
            passed = True,
            detail = f"Agent '{request.agent_id}' authenticated."
        ))
        # 2. Idempotency check (Prevent duplicate purchases within 5 mins)
        five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_txn = db.query(AuditLogRecord).filter(
            AuditLogRecord.agent_id == request.agent_id,
            AuditLogRecord.product_id == request.product_id,
            AuditLogRecord.event_type == AuditEventType.PAYMENT_INITIATED.value,
            AuditLogRecord.timestamp >= five_mins_ago
        ).first()

        if recent_txn:
            trace.append(PolicyCheck(
                check = "idempotency_check",
                passed = False,
                detail = "Duplicate purchase detected. You already bought this item less than 5 minutes ago."
            ))
            return self._reject("IDEMPOTENCY_BLOCK", trace, warnings, db, request)

        trace.append(PolicyCheck(
            check = "idemptency_check",
            passed = True,
            detail = "No duplicate recent purchases found."
        ))

        ## Check-2 : Mandate Active
        if not mandate.is_active:
            trace.append(PolicyCheck(
                check = "mandate_active",
                passed = False,
                detail = "This agent's mandate has been deactivated."
            ))
            return self._reject("MANDATE_INACTIVE", trace, warnings, db, request)

        if mandate.expires_at and mandate.expires_at < datetime.now(timezone.utc):
            trace.append(PolicyCheck(
                check = "mandate_active",
                passed = False,
                detail=f"Mandate expired at {mandate.expires_at.isoformat()}."
            ))
            return self._reject("MANDATE_EXPIRED", trace, warnings, db, request)

        trace.append(PolicyCheck(
            check = "mandate_active",
            passed = True,
            detail="Mandate is active and not expired",
        ))

        # Check-3 : Category Allowed
        allowed = [c.lower() for c in mandate.allowed_categories]
        requested_category = request.product_category.lower()

        if requested_category not in allowed:
            trace.append(PolicyCheck(
                check = "category_allowed",
                passed = False,
                detail = (
                    f"Category '{requested_category}' is not in this agent's"
                    f"allowed categories: {mandate.allowed_categories}."
                )
            ))
            return self._reject("CATEGORY_NOT_ALLOWED", trace, warnings, db, request)
        trace.append(PolicyCheck(
            check = "category_allowed",
            passed = True,
            detail = f"Primary category '{requested_category}' is permitted."
        ))

        # Check-3b : Addon Category Allowed (If addon is bundled)
        if request.addon_product_id:
            from src.catalog.service import get_product
            addon = get_product(db, request.addon_product_id)
            if addon:
                addon_category = addon.category.lower()
                if addon_category not in allowed:
                    trace.append(PolicyCheck(
                        check = "addon_category_allowed",
                        passed = False,
                        detail = (
                            f"Addon category '{addon_category}' is not in this agent's"
                            f"allowed categories: {mandate.allowed_categories}."
                        )
                    ))
                    return self._reject("ADDON_CATEGORY_NOT_ALLOWED", trace, warnings, db, request)
                trace.append(PolicyCheck(
                    check = "addon_category_allowed",
                    passed = True,
                    detail = f"Addon category '{addon_category}' is permitted."
                ))


        # Check-4 : Single Transaction Limit
        if request.total_amount_inr > mandate.max_single_txn_inr:
            trace.append(PolicyCheck(
                check = "single_txn_limit",
                passed = False,
                detail = (
                    f"Transaction amount ₹{request.total_amount_inr:,.2f} exceeds"
                    f"single transaction limit of ₹{mandate.max_single_txn_inr:,.2f}."
                ),
            ))
            return self._reject("SINGLE_TXN_LIMIT_EXCEEDED", trace, warnings, db, request)

        trace.append(PolicyCheck(
            check = "single_txn_limit",
            passed = True,
            detail=(
                f"₹{request.total_amount_inr:,.2f} is within the "
                f"₹{mandate.max_single_txn_inr:,.2f} single transaction limit."
            ),
        ))

        # Check-5 : Daily Spend Limit
        today_spend = self._get_today_spend(db, request.agent_id)
        projected_spend = today_spend + request.total_amount_inr

        if projected_spend > mandate.max_daily_spend_inr:
            trace.append(PolicyCheck(
                check = "daily_spend_limit",
                passed = False,
                detail = (
                    f"Today's spend so far: ₹{today_spend:,.2f}."
                    f"This purchase of ₹{request.total_amount_inr:,.2f} would bring"
                    f"total to ₹{projected_spend:,.2f}, exceeding daily limit of "
                    f"₹{mandate.max_daily_spend_inr:,.2f}."
                )
            ))
            return self._reject("DAILY_SPEND_LIMIT_EXCEEDED", trace, warnings, db, request)

        remaining_after = mandate.max_daily_spend_inr - projected_spend
        trace.append(PolicyCheck(
            check = "daily_spend_limit",
            passed = True,
            detail = (
                f"Daily limit OK. Spent today: ₹{today_spend:,.2f}. "
                f"Remaining after this purchase: ₹{remaining_after:,.2f}."
            )
        ))

        # Check-6 : Stock Available
        from src.catalog.service import check_stock
        in_stock = check_stock(db, request.product_id, request.quantity)

        if not in_stock:
            trace.append(PolicyCheck(
                check = "stock_available",
                passed = False,
                detail= (
                    f"Insufficient stock for product '{request.product_id}'."
                    f"Requested: {request.quantity} unit(s)."
                )
            ))
            return self._reject("STOCK_EXHAUSTED", trace , warnings, db, request)

        trace.append(PolicyCheck(
            check = "stock_available",
            passed = True,
            detail = f"Stock confirmed for {request.quantity} unit(s)."
        ))

        # Check-7 : Human Approval Gate
        requires_human = False
        if (
            mandate.requires_approval_above_inr is not None
            and request.total_amount_inr > mandate.requires_approval_above_inr
        ):
            requires_human = True
            warnings.append(
                f"Transaction amount ₹{request.total_amount_inr:,.2f} exceeds the "
                f"₹{mandate.requires_approval_above_inr:,.2f} human approval threshold. "
                f"Flagged for review — proceeding for demo purposes."
            )
            trace.append(PolicyCheck(
                check = "human_approval_gate",
                passed = True,
                detail = f"Amount exceeds approval threshold. Flagged but allowed for demo."
            ))
        else:
            trace.append(PolicyCheck(
                check="human_approval_gate",
                passed = True,
                detail = f"No human approval required for this amount."
            ))

        # Check for merchant upsell offer if this is a primary purchase
        upsell_offer = None
        if not request.addon_product_id:
            from src.catalog.service import get_product
            if request.product_category.lower() in ["chargers"] or request.product_id in ["prod-001", "prod-002", "prod-004", "prod-005"]:
                cable = get_product(db, "prod-006")
                if cable and cable.stock_quantity > 0:
                    upsell_offer = {
                        "addon_product_id": cable.product_id,
                        "name": cable.name,
                        "price_inr": 499.0,
                        "category": cable.category,
                        "pitch": "Exclusive bundle: Save ₹300 on this 240W braided cable when purchased with your charger today."
                    }
                    log_audit_event(db, {
                        "event_type": AuditEventType.UPSELL_SUGGESTED,
                        "agent_id": request.agent_id,
                        "product_id": cable.product_id,
                        "amount_inr": 499.0,
                        "details": {
                            "primary_product_id": request.product_id,
                            "pitch": upsell_offer["pitch"]
                        }
                    })

        # All checks passed - Approve
        log_audit_event(db, {
            "event_type": AuditEventType.POLICY_APPROVED,
            "agent_id": request.agent_id,
            "product_id": request.product_id,
            "amount_inr": request.total_amount_inr,
            "policy_decision": True,
            "details": {
                "trace": [c.model_dump() for c in trace],
                "warnings": warnings,
                "upsell_included": bool(upsell_offer),
            },
        })

        return MandateCheckResult(
            approved=True,
            reason = "APPROVED",
            decision_trace = trace,
            remaining_daily_budget_inr = remaining_after,
            requires_human_approval=requires_human,
            warnings=warnings,
            upsell_offer=upsell_offer,
        )

    # Helper Functions
    def _reject(
        self,
        reason : str,
        trace : list[PolicyCheck],
        warnings: list[str],
        db: Session,
        request: MandateCheckRequest,
    ) -> MandateCheckResult:
        """Logs rejection to audit trail and returns a rejection result with a smart alternative if available."""
        from src.catalog.service import find_alternative_product
        
        # Look up mandate to find budget and allowed categories
        mandate = db.query(AgentMandateRecord).filter(
            AgentMandateRecord.agent_id == request.agent_id
        ).first()

        recommended_alt = None
        if mandate:
            today_spend = self._get_today_spend(db, request.agent_id)
            daily_remaining = mandate.max_daily_spend_inr - today_spend
            effective_budget = min(mandate.max_single_txn_inr, daily_remaining)

            if effective_budget > 0:
                alt = find_alternative_product(
                    db=db,
                    category=request.product_category,
                    max_price_inr=effective_budget,
                    exclude_product_id=request.product_id,
                    allowed_categories=mandate.allowed_categories
                )
                if alt:
                    recommended_alt = {
                        "product_id": alt.product_id,
                        "name": alt.name,
                        "price_inr": alt.price_inr,
                        "category": alt.category,
                        "reason": (
                            f"Original product was rejected ({reason}). "
                            f"{alt.name} is in stock at ₹{alt.price_inr:,.0f} and fits within "
                            f"your ₹{effective_budget:,.0f} budget limit."
                        )
                    }

        log_audit_event(db, {
            "event_type" : AuditEventType.POLICY_REJECTED,
            "agent_id" : request.agent_id,
            "product_id" : request.product_id,
            "amount_inr" : request.total_amount_inr,
            "policy_decision" : False,
            "details" : {
                "rejection_reason" : reason,
                "trace":[c.model_dump() for c in trace],
                "recommended_alternative": recommended_alt,
            },
        })

        return MandateCheckResult(
            approved=False,
            reason = reason,
            decision_trace = trace,
            remaining_daily_budget_inr = None,
            requires_human_approval=False,
            warnings=warnings,
            recommended_alternative=recommended_alt,
        )

    def _get_today_spend(self, db: Session, agent_id: str) -> float:
        """
        Sums all sucessful order amounts for this agent today(UTC).
        Only counts orders with status 'paid' or 'payment_initiated'.
        """
        today = date.today()
        result = db.query(func.coalesce(func.sum(OrderRecord.total_amount_inr), 0)).filter(
            OrderRecord.agent_id == agent_id,
            OrderRecord.status.in_(["paid", "payment_initiated"]),
            func.cast(OrderRecord.created_at, Date) == today,
        ).scalar()

        return float(result or 0.0)

policy_engine = PolicyEngine()

