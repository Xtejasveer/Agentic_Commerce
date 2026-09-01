"""
Payment orchestration service.

Coordinates the full purchase flow:
mandates re-check -> stock reserve -> Razorpay order ->
payment link -> audit log -> return result

On any failure: stock is released, error is logged, exception is raised.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from src.database.models import OrderRecord
from src.schemas.order import PurchaseRequest, PurchaseResult, OrderStatus
from src.schemas.mandate import MandateCheckRequest
from src.schemas.audit import AuditEventType
from src.policy.engine import policy_engine
from src.catalog.service import reserve_stock, release_stock,get_product, log_audit_event
from src.payments import razorpay_client

logger = logging.getLogger(__name__)

def execute_purchase(
    db: Session,
    request: PurchaseRequest,
) -> PurchaseResult:
    """
    Executes the full purchase pipeline for an AI buyer agent.
    Steps:
        1. Re-validate mandate (defense in depth — policy is checked twice)
        2. Fetch product details
        3. Reserve stock atomically
        4. Create internal order record (status: pending)
        5. Create Razorpay order
        6. Create Razorpay payment link
        7. Update order record with Razorpay IDs
        8. Log PAYMENT_INITIATED audit entry
        9. Return PurchaseResult with payment link
    On failure at any step after stock reservation:
        - Stock is released back
        - Order is marked failed
        - PAYMENT_FAILED audit entry is written
        - Exception is re-raised with a clear message
    """
    order_id = str(uuid.uuid4())
    product = None
    stock_reserved = False

    try:
        # Step-1 : Revalidate Mandate
        product = get_product(db, request.product_id)
        if not product:
            raise ValueError(f"Product '{request.product_id}' not found")

        total_amount = product.price_inr * request.quantity

        mandate_request = MandateCheckRequest(
            agent_id = request.agent_id,
            product_id=request.product_id,
            product_category=product.category,
            quantity = request.quantity,
            total_amount_inr = total_amount,
        )
        mandate_result = policy_engine.validate(db=db, request=mandate_request)

        if not mandate_result.approved:
            return PurchaseResult(
                success = False,
                status = OrderStatus.FAILED,
                error_message = f"Policy rejected: {mandate_result.reason}."
                                f"{mandate_result.decision_trace[-1].detail}",
            )

        # Step-2 : Reserve Stock
        reserved = reserve_stock(db, request.product_id, request.quantity)
        if not reserved:
            raise ValueError(
                f"Stock reservation failed for '{request.product_id}'."
                f"Item may have sold out between validation and purchase."
            )
        stock_reserved = True

        log_audit_event(db, {
            "event_type" : AuditEventType.STOCK_RESERVED,
            "agent_id" : request.agent_id,
            "product_id" : request.product_id,
            "amount_inr" : total_amount,
            "details" : {"quantity" : request.quantity, "order_id" : order_id}
        })

        # Step-3: Create internal order record
        order_record = OrderRecord(
            order_id = order_id,
            agent_id = request.agent_id,
            product_id = request.product_id,
            quantity = request.quantity,
            total_amount_inr = total_amount,
            shipping_address = request.shipping_address,
            status = OrderStatus.PENDING,
        )
        db.add(order_record)
        db.commit()

        # Step-4 : Create Razorpay order
        rp_order = razorpay_client.create_order(
            amount_inr = total_amount,
            receipt=order_id[:40],
            notes = {
                "agent_id" : request.agent_id,
                "product_id" : request.product_id,
                "product_name" : product.name,
                "internal_order_id" : order_id,
            },
        )
        razorpay_order_id = rp_order["id"]

        # Step-5 : Create Razorpay Payment link
        payment_link = razorpay_client.create_payment_link(
            amount_inr = total_amount,
            description=f"{request.quantity} x {product.name}",
            reference_id = order_id[:40],
        )
        payment_link_url = payment_link.get("short_url")

        # Step-6: Update order record with Razorpay details
        order_record.razorpay_order_id = razorpay_order_id
        order_record.payment_link_url = payment_link_url
        order_record.status = OrderStatus.PAYMENT_INITIATED
        db.commit()

        # Step-7 : Log audit entry
        audit_id = log_audit_event(db, {
             "event_type": AuditEventType.PAYMENT_INITIATED,
            "agent_id": request.agent_id,
            "product_id": request.product_id,
            "amount_inr": total_amount,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_status": "created",
            "details": {
                "order_id": order_id,
                "product_name": product.name,
                "quantity": request.quantity,
                "payment_link_id": payment_link.get("id"),
                "shipping_address": request.shipping_address,
            },
        })

        logger.info(
            f"Purchase initiated - order: {order_id},"
            f"Razorpay: {razorpay_order_id}, agent: {request.agent_id}"
        )

        return PurchaseResult(
            success= True,
            order_id=order_id,
            razorpay_order_id=razorpay_order_id,
            payment_link_url=payment_link_url,
            status = OrderStatus.PAYMENT_INITIATED,
            total_amount_inr=total_amount,
            product_name=product.name,
            quantity=request.quantity,
            audit_id = audit_id
        )
    except Exception as e:
        # Rollback - release stock if it was reserved
        if stock_reserved and product:
            release_stock(db, request.product_id, request.quantity)
            log_audit_event(db, {
                "event_type" : AuditEventType.STOCK_RELEASED,
                "agent_id": request.agent_id,
                "product_id" : request.product_id,
                "details" : {"reason" : "payment_failure_rollback", "error": str(e)}
            })
        log_audit_event(db, {
            "event_type": AuditEventType.PAYMENT_FAILED,
            "agent_id": request.agent_id,
            "product_id": request.product_id,
            "amount_inr": product.price_inr * request.quantity if product else None,
            "error_message": str(e),
            "details": {"order_id": order_id},
        })

        logger.error(f"Purchase failed for agent {request.agent_id}: {e}")

        return PurchaseResult(
            success=False,
            order_id=order_id,
            status=OrderStatus.FAILED,
            error_message=str(e)
        )