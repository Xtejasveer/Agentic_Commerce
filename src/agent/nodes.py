"""
LangGraph node functions for the buyer agent workflow.

Each node is created via a factory function that captures tools and the LLM
in a closure - this keeps the node signature clean.
"""
import json
import logging
from langchain_core.messages import AIMessage, HumanMessage
from src.agent.state import AgentState

logger = logging.getLogger(__name__)

# ── Helper Functions ──────────────────────────────────────────────────────────


def _get_tool(tools: list, name: str):
    """Fetch a loaded MCP tool by name"""
    for tool in tools:
        if tool.name == name:
            return tool
    raise ValueError(f"MCP tool '{name}' not found. Available: {[t.name for t in tools]}")


def _parse_json(text: str) -> dict:
    """Extract a JSON object from LLM output that may include markdown fences."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except (json.JSONDecodeError, ValueError):
                continue
    return json.loads(text)


def _parse_mcp_response(raw) -> dict | list:
    """
    Parse raw MCP tool response into a Python dict or list.

    Handles all formats returned by langchain-mcp-adapters:
      - str: JSON string
      - dict: already parsed
      - list: content blocks [{"type":"text","text":"..."}] or TextContent objects
      - ToolMessage: object with .content attribute
    """
    # String → parse JSON
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    # Dict → return as-is
    if isinstance(raw, dict):
        return raw

    # List → could be MCP content blocks or raw data
    if isinstance(raw, list):
        # Content block dicts: [{"type": "text", "text": "{...}"}]
        if raw and isinstance(raw[0], dict) and "text" in raw[0]:
            texts = [item.get("text", "") for item in raw if isinstance(item, dict) and "text" in item]
            combined = "".join(texts)
            try:
                return json.loads(combined)
            except (json.JSONDecodeError, TypeError):
                return {}
        # TextContent objects with .text attribute
        if raw and hasattr(raw[0], "text"):
            texts = [item.text for item in raw if hasattr(item, "text")]
            combined = "".join(texts)
            try:
                return json.loads(combined)
            except (json.JSONDecodeError, TypeError):
                return {}
        # Otherwise it's a plain list (e.g. the products array itself)
        return raw

    # ToolMessage or similar → unwrap .content
    if hasattr(raw, "content"):
        return _parse_mcp_response(raw.content)

    # Object with .text
    if hasattr(raw, "text"):
        try:
            return json.loads(raw.text)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return {}

    return {}


# ── Node Factories ────────────────────────────────────────────────────────────


def make_search_node(tools: list, llm):
    """
    Node-1: Parse user intent and search the product catalog.
    Uses the LLM to extract structured search parameters from the natural language request.
    """
    search_tool = _get_tool(tools, "search_products")

    async def search_node(state: AgentState) -> dict:
        logger.info(f"[search_node] Request: {state['user_request']}")

        # Ask the LLM to extract search params from the raw user request
        user_req = state["user_request"]
        extraction_prompt = (
            f'Extract search parameters from: "{user_req}"\n\n'
            "Return ONLY a JSON object with these optional fields:\n"
            '{"query": "search terms", "max_price": float (if mentioned), "category": "category if explicitly mentioned"}\n'
            "Omit fields not mentioned. For example, if no category is explicitly specified, do not include the category field. Return only JSON."
        )
        response = await llm.ainvoke([HumanMessage(content=extraction_prompt)])

        try:
            params = _parse_json(response.content)
        except (json.JSONDecodeError, IndexError):
            params = {"query": state["user_request"]}

        logger.info(f"[search_node] Extracted params: {params}")

        # Prepare arguments, filtering out None values
        args = {
            "query": params.get("query", state["user_request"]),
            "max_price": params.get("max_price"),
            "category": params.get("category"),
            "limit": 5,
        }
        args = {k: v for k, v in args.items() if v is not None}

        # Invoke the MCP search tool
        raw = await search_tool.ainvoke(args)

        result = _parse_mcp_response(raw)

        # Normalize: if result is a list, it's the products array directly
        if isinstance(result, list):
            result = {"products": result, "total_found": len(result), "query": state["user_request"]}
        elif not isinstance(result, dict):
            result = {"products": []}

        products = result.get("products", [])
        logger.info(f"[search_node] Found {len(products)} products.")

        if not products:
            return {
                "search_results": [],
                "current_step": "failed",
                "error": "No products found matching your request. Try different search terms.",
                "messages": [AIMessage(content="No matching products found in the catalog.")],
            }

        return {
            "search_results": products,
            "current_step": "evaluate",
            "messages": [AIMessage(
                content=f"Found {len(products)} matching products. Evaluating best option..."
            )],
        }

    return search_node


def make_evaluate_node(llm):
    """
    Node-2: Use the LLM to pick the best product from the search results.
    Considers relevance, price and stock availability.
    """

    async def evaluate_node(state: AgentState) -> dict:
        products = state.get("search_results", [])
        logger.info(f"[evaluate_node] Evaluating {len(products)} products.")

        # Guard: if search found nothing, skip evaluation
        if not products:
            return {
                "selected_product": {},
                "current_step": "failed",
                "error": "No products to evaluate — search returned empty results.",
                "messages": [AIMessage(content="No products available to evaluate.")],
            }

        products_text = json.dumps(products, indent=2)
        evaluation_prompt = (
            f'User request: "{state["user_request"]}"\n\n'
            f"Available products:\n{products_text}\n\n"
            "If the user is explicitly asking to BUY or PURCHASE something, pick the BEST product. Consider:\n"
            "1. How well it matches the request\n"
            "2. Price (prefer cheapest that meets requirements)\n"
            "3. Stock (stock_quantity must be > 0)\n\n"
            "If the user is just asking a question (e.g., 'What can I buy?', 'list items') and NOT explicitly asking to purchase an item, DO NOT select a product.\n\n"
            "Return ONLY a JSON object:\n"
            '{"product_id": "prod-123" or null, "name": "...", "price_inr": 0, "reason": "Explain why you selected it, or if null, summarize the available products."}\n'
        )

        response = await llm.ainvoke([HumanMessage(content=evaluation_prompt)])

        try:
            selected = _parse_json(response.content)
        except (json.JSONDecodeError, IndexError, ValueError):
            # Fallback: pick the first in-stock product
            in_stock = [p for p in products if isinstance(p, dict) and p.get("stock_quantity", 0) > 0]
            if in_stock:
                selected = dict(in_stock[0])
            elif products and isinstance(products[0], dict):
                selected = dict(products[0])
            else:
                selected = {"product_id": None, "name": "Unknown", "price_inr": 0}
            selected["reason"] = "Best available match"

        # Use "or 0" because .get default only applies when key is MISSING, not when value is None
        price = selected.get("price_inr") or 0
        name = selected.get("name") or "Unknown"
        product_id = selected.get("product_id")

        if not product_id:
            logger.info(f"[evaluate_node] No product selected for purchase. Reason: {selected.get('reason')}")
            return {
                "selected_product": selected,
                "current_step": "inform",
                "final_response": selected.get("reason", "I can help you find products, but I didn't detect a purchase request."),
                "messages": [AIMessage(content=selected.get("reason", "I can help you find products."))]
            }

        logger.info(f"[evaluate_node] Selected: {name} at ₹{price}")

        return {
            "selected_product": selected,
            "current_step": "validate",
            "messages": [AIMessage(
                content=(
                    f"Selected: **{name}** at ₹{price:,.0f}\n"
                    f"Reason: {selected.get('reason', 'Best match for your request')}"
                )
            )],
        }

    return evaluate_node


def make_evaluate_upsell_node(tools: list, llm):
    suggest_tool = _get_tool(tools, "suggest_addon")
    validate_tool = _get_tool(tools, "validate_purchase_mandate")
    details_tool = _get_tool(tools, "get_product_details")

    async def evaluate_upsell_node(state: AgentState) -> dict:
        product = state.get("selected_product", {})
        if not product:
            return {}

        logger.info(f"[evaluate_upsell_node] Checking for addons for {product.get('product_id')}")

        # Check if the policy engine already provided an embedded upsell offer
        mandate_res = state.get("mandate_result") or {}
        embedded_offer = mandate_res.get("upsell_offer")

        if embedded_offer:
            addon_data = {
                "has_addon": True,
                "addon_product_id": embedded_offer.get("addon_product_id"),
                "name": embedded_offer.get("name"),
                "price_inr": embedded_offer.get("price_inr"),
                "merchant_pitch": embedded_offer.get("pitch"),
            }
        else:
            raw_addon = await suggest_tool.ainvoke({"product_id": product.get("product_id")})
            addon_data = _parse_mcp_response(raw_addon)
        
        if not isinstance(addon_data, dict) or not addon_data.get("has_addon"):
            return {}

        logger.info(f"[evaluate_upsell_node] Merchant suggested addon: {addon_data.get('addon_product_id')}")

        # Check combined cart policy
        raw_details = await details_tool.ainvoke({"product_id": product.get("product_id")})
        details = _parse_mcp_response(raw_details)
        if not isinstance(details, dict): details = {}
        
        full_product = details.get("product", {})
        product_category = full_product.get("category", "unknown")

        combined_price = product.get("price_inr", 0.0) + addon_data.get("price_inr", 0.0)

        raw_val = await validate_tool.ainvoke({
            "agent_id": state["agent_id"],
            "agent_api_key": state.get("api_key", ""),
            "product_id": product.get("product_id"),
            "addon_product_id": addon_data.get("addon_product_id"),
            "product_category": product_category,
            "total_amount_inr": combined_price,
            "quantity": 1
        })
        val_result = _parse_mcp_response(raw_val)
        if not isinstance(val_result, dict): val_result = {}

        is_approved = val_result.get("approved", False)
        reason = val_result.get("reason", "Unknown")
        trace = val_result.get("decision_trace", [])

        # Ask LLM to evaluate the upsell negotiation
        prompt = f"""
You are {state['agent_id']}. You selected '{product.get('name')}' for ₹{product.get('price_inr')} to fulfill: "{state['user_request']}"
The merchant is offering an upsell: '{addon_data.get('name')}' for ₹{addon_data.get('price_inr')}.
Merchant Pitch: "{addon_data.get('merchant_pitch')}"

You ran a policy check on the COMBINED cart (Primary + Addon). 
Policy Result: {"APPROVED" if is_approved else "REJECTED"}
Reason: {reason}
Trace details: {trace}

Decide whether to accept the upsell. 
If Policy Result is REJECTED, you MUST reject the upsell and narrate exactly why based on the trace (e.g. category restriction or budget).
If Policy Result is APPROVED, you can accept it if it makes logical sense for the user.

Output JSON:
{{
  "decision": "accept" or "reject",
  "narration": "A one sentence explanation of your choice (e.g. 'I will accept the cable bundle as it fits the budget' OR 'I must decline the cable because my mandate only allows chargers.')."
}}
"""
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        # Parse JSON
        decision_data = {"decision": "reject", "narration": "Failed to parse decision."}
        import json
        content = response.content.strip()
        if content.startswith("```json"): content = content[7:-3]
        try:
            decision_data = json.loads(content)
        except Exception:
            pass

        decision = decision_data.get("decision", "reject")
        narration = decision_data.get("narration", "")

        try:
            from src.database.session import SessionLocal
            from src.catalog.service import log_audit_event
            from src.schemas.audit import AuditEventType
            
            db = SessionLocal()
            try:
                log_audit_event(db, {
                    "event_type": AuditEventType.UPSELL_ACCEPTED if decision == "accept" else AuditEventType.UPSELL_REJECTED,
                    "agent_id": state["agent_id"],
                    "product_id": addon_data.get("addon_product_id"),
                    "details": {"narration": narration}
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to log upsell event: {e}")

        return {
            "suggested_addon": addon_data if decision == "accept" else None,
            "addon_decision": decision,
            "messages": [AIMessage(content=f"🛍️ Upsell Evaluation: {narration}")]
        }
    return evaluate_upsell_node

def make_validate_node(tools: list):
    """
    Node-3: Run the policy engine to check if this agent can make this purchase.
    Fetches full product details (including category) before calling the policy check.
    """
    validate_tool = _get_tool(tools, "validate_purchase_mandate")
    details_tool = _get_tool(tools, "get_product_details")

    async def validate_node(state: AgentState) -> dict:
        product = state.get("selected_product", {})
        product_id = product.get("product_id")

        logger.info(f"[validate_node] Validating mandate for product: {product_id}")

        if not product_id:
            return {
                "current_step": "failed",
                "error": "No product_id available — search or evaluation may have failed.",
                "messages": [AIMessage(content="Could not determine which product to validate.")],
            }

        # Get product details
        raw_details = await details_tool.ainvoke({"product_id": product_id})
        details = _parse_mcp_response(raw_details)
        if not isinstance(details, dict):
            details = {}

        logger.info(f"[validate_node] Product details response: found={details.get('found')}")

        if not details.get("found"):
            return {
                "current_step": "failed",
                "error": f"Product {product_id} could not be found for validation.",
                "messages": [AIMessage(content=f"Product {product_id} not found")],
            }

        full_product = details.get("product", {})
        price_inr = full_product.get("price_inr", product.get("price_inr", 0))
        category = full_product.get("category", "electronics")

        # Call the policy engine via MCP tool
        raw_mandate = await validate_tool.ainvoke({
            "agent_id": state["agent_id"],
            "agent_api_key" : state["api_key"],
            "product_id": product_id,
            "product_category": category,
            "total_amount_inr": price_inr,
            "quantity": 1,
        })
        mandate_result = _parse_mcp_response(raw_mandate)
        if not isinstance(mandate_result, dict):
            mandate_result = {}

        approved = mandate_result.get("approved", False)
        reason = mandate_result.get("reason", "Unknown")

        logger.info(f"[validate_node] Mandate decision: {approved} | Reason: {reason}")

        if approved:
            warnings = mandate_result.get("warnings", [])
            msg = f"Mandate approved for ₹{price_inr:,.0f} purchase."
            if warnings:
                msg += f"\n⚠ Warning: {warnings[0]}"
            return {
                "mandate_result": mandate_result,
                "current_step": "purchase",
                "messages": [AIMessage(content=msg)],
            }
        else:
            trace = mandate_result.get("decision_trace", [])
            failed = next((c for c in reversed(trace) if not c.get("passed")), {})
            error_detail = f"{reason}: {failed.get('detail', '')}"

            alt = mandate_result.get("recommended_alternative")
            if alt and not state.get("recovery_attempted"):
                logger.info(f"[validate_node] Policy failed, but merchant proposed alternative: {alt.get('name')}")
                
                # Log SALE_RECOVERED audit entry
                try:
                    from src.database.session import SessionLocal
                    from src.catalog.service import log_audit_event
                    from src.schemas.audit import AuditEventType
                    
                    db = SessionLocal()
                    try:
                        log_audit_event(db, {
                            "event_type": AuditEventType.SALE_RECOVERED,
                            "agent_id": state["agent_id"],
                            "product_id": alt["product_id"],
                            "amount_inr": alt["price_inr"],
                            "details": {
                                "original_product_id": product_id,
                                "original_reason": reason,
                                "alternative_name": alt["name"],
                                "alternative_price_inr": alt["price_inr"],
                                "recovery_reason": alt.get("reason"),
                            }
                        })
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"Failed to log recovery event: {e}")

                recovery_msg = f"🔄 Mandate failed ({reason}). Recovered transaction with merchant alternative: {alt['name']} at ₹{alt['price_inr']:,.0f}"
                return {
                    "selected_product": {
                        "product_id": alt["product_id"],
                        "name": alt["name"],
                        "price_inr": alt["price_inr"],
                        "category": alt.get("category", category)
                    },
                    "recovery_attempted": True,
                    "recovered_from_rejection": True,
                    "recovery_narrative": alt.get("reason", recovery_msg),
                    "mandate_result": mandate_result,
                    "current_step": "recover",
                    "messages": [AIMessage(content=recovery_msg)]
                }

            return {
                "mandate_result": mandate_result,
                "current_step": "failed",
                "error": error_detail,
                "messages": [AIMessage(
                    content=f"Purchase rejected by policy engine.\nReason: {reason}"
                )],
            }

    return validate_node


def make_purchase_node(tools: list):
    """
    Node-4: Execute the purchase — creates Razorpay order and payment link.
    """
    purchase_tool = _get_tool(tools, "execute_purchase")

    async def purchase_node(state: AgentState) -> dict:
        product = state.get("selected_product", {})
        pid = product.get("product_id")
        logger.info(f"[purchase_node] Executing purchase: {pid}")

        addon = state.get("suggested_addon")
        addon_id = addon.get("addon_product_id") if addon else None

        raw_result = await purchase_tool.ainvoke({
            "agent_id": state["agent_id"],
            "agent_api_key": state.get("api_key", ""),
            "product_id": pid,
            "addon_product_id": addon_id,
            "shipping_address": state.get(
                "shipping_address",
                "123 Default Tech Park, BLR"
            ),
            "quantity": 1
        })

        result = _parse_mcp_response(raw_result)
        if not isinstance(result, dict):
            result = {}

        if result.get("success"):
            return {
                "purchase_result": result,
                "current_step": "done",
                "messages": [AIMessage(
                    content=(
                        f"Order placed! Order ID: {result.get('order_id')}\n"
                        f"Razorpay link: {result.get('payment_link_url')}"
                    )
                )],
            }
        else:
            return {
                "purchase_result": result,
                "current_step": "failed",
                "error": result.get("error_message", "Purchase execution failed"),
                "messages": [AIMessage(content=f"Purchase failed: {result.get('error_message')}")],
            }

    return purchase_node


def make_respond_node():
    """
    Node-5 (terminal): Generate the final human-readable response.
    """

    async def respond_node(state: AgentState) -> dict:
        step = state.get("current_step")
        if step == "inform":
            # The agent is just answering a question, return the final response
            return {"final_response": state.get("final_response", "I can help you find products.")}
        elif step == "done":
            result = state.get("purchase_result", {})
            recovery_prefix = ""
            if state.get("recovered_from_rejection"):
                recovery_prefix = f"🔄 **Sale Recovered!** {state.get('recovery_narrative', '')}\n\n"

            response = (
                f"{recovery_prefix}✅ Order placed successfully!\n\n"
                f"📦 Product:       {result.get('product_name')}\n"
                f"🔢 Quantity:      {result.get('quantity')}\n"
                f"💰 Total:         ₹{result.get('total_amount_inr', 0):,.2f}\n"
                f"🆔 Order ID:      {result.get('order_id', 'N/A')}\n"
                f"📋 Razorpay ID:   {result.get('razorpay_order_id', 'N/A')}\n"
                f"🔗 Payment Link:  {result.get('payment_link_url', 'N/A')}\n\n"
                f"Open the payment link to complete checkout."
            )
        else:
            error = state.get("error", "Unknown error")
            mandate = state.get("mandate_result") or {}
            trace = mandate.get("decision_trace", [])
            failed_check = next((c for c in reversed(trace) if not c.get("passed")), None)
            response = f"❌ Purchase could not be completed.\n\nReason: {error}"
            if failed_check:
                response += (
                    f"\n\nFailed check: [{failed_check.get('check')}]\n"
                    f"{failed_check.get('detail', '')}"
                )
        return {
            "final_response": response,
            "messages": [AIMessage(content=response)],
        }

    return respond_node