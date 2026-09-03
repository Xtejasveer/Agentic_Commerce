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
            '{"query": "what to search for", "max_price": 2000, "category": "chargers"}\n'
            "Omit fields not mentioned. Return only JSON."
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
            f'User wants: "{state["user_request"]}"\n\n'
            f"Available products:\n{products_text}\n\n"
            "Pick the BEST product. Consider:\n"
            "1. How well it matches the request\n"
            "2. Price (prefer cheapest that meets requirements)\n"
            "3. Stock (stock_quantity must be > 0)\n\n"
            "Return ONLY a JSON object:\n"
            '{"product_id": "...", "name": "...", "price_inr": 0, "reason": "one sentence"}\n'
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
            return {
                "mandate_result": mandate_result,
                "current_step": "failed",
                "error": f"{reason}: {failed.get('detail', '')}",
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

        raw_result = await purchase_tool.ainvoke({
            "agent_id": state["agent_id"],
            "product_id": pid,
            "shipping_address": state.get(
                "shipping_address",
                "123 Demo Street, Mumbai, Maharashtra 400001"
            ),
            "quantity": 1,
        })

        result = _parse_mcp_response(raw_result)
        if not isinstance(result, dict):
            result = {}

        success = result.get("success", False)
        logger.info(f"[purchase_node] Result: success = {success}")

        if success:
            return {
                "purchase_result": result,
                "current_step": "done",
                "messages": [AIMessage(content="✅ Order created. Payment link generated.")],
            }

        return {
            "purchase_result": result,
            "current_step": "failed",
            "error": result.get("error_message", "Purchase failed"),
            "messages": [AIMessage(content=f"Purchase failed: {result.get('error_message')}")],
        }

    return purchase_node


def make_respond_node():
    """
    Node-5 (terminal): Generate the final human-readable response.
    """

    async def respond_node(state: AgentState) -> dict:
        step = state.get("current_step")
        if step == "done":
            result = state.get("purchase_result", {})
            response = (
                f"✅ Order placed successfully!\n\n"
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