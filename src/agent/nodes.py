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

# Helper Functions

def _get_tool(tools: list, name:str):
    """Fetch a loaded MCP tool by name"""
    for tool in tools:
        if tool.name == name:
            return tool

    raise ValueError(f"MCP tool '{name}' not found. Available: {[t.name for t in tools]}")

def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

# Node Factories

def make_search_node(tools: list, llm):
    """
    Node-1 : Parse user intent and search the product catalog
    Uses the LLM to extract structured search parameters from the matural language request.
    """ 
    search_tool = _get_tool(tools, "search_products")

    async def search_node(state: AgentState) -> dict:
        logger.info(f"[search_node] Request: {state['user_request']}")

        # Ask the LLM to extract search params from the raw user request
        user_req = state['user_request']
        extraction_prompt = (
            f'Extract search parameters from: "{user_req}"\n\n'
            "Return ONLY a JSON object with these optional fields:\n"
            '{"query" : "what to search for", "max_price": 2000, "category": "chargers"}\n'
            "Omit fields not mentioned. Return only JSON."
        )
        response = await llm.ainvoke([HumanMessage(content = extraction_prompt)])

        try:
            params = _parse_json(response.content)
        except (json.JSONDecodeError, IndexError):
            params = {"query" : state["user_request"]}

        logger.info(f"[search_node] Extracted params: {params}")

        #Invoke the MCP search tool
        raw = await search_tool.ainvoke({
            "query": params.get("query", state["user_request"]),
            "max_price": params.get("max_price"),
            "category": params.get("category"),
            "limit": 5,
        })

        if isinstance(raw, str):
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                result = {"products" : []}
        elif isinstance(raw, dict):
            result = raw
        elif isinstance(raw, list):
            result = {"products" : raw, "total_found" : len(raw), "query" : state["user_request"]}
        else:
            result = {"products" : []}
        products = result.get("products", []) if isinstance(result, dict) else []

        logger.info(f"[search_node] Found {len(products)} products.")

        if not products:
            return {
                "search_results" : [],
                "current_step" : "failed",
                "error" : "No products found matching your request. Try different search terms.",
                "messages" : [AIMessage(content = "No matching products found in the catalog.")]
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
    Node-2 : Use the LLM to pick the bect product from the search results.
    Considers relevance, price and stock availability.
    """

    async def evaluate_node(state: AgentState) -> dict:
        products = state.get("search_results", [])
        logger.info(f"[evaluate_node] Evaluating {len(products)} products.")

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

        response = await llm.ainvoke([HumanMessage(content = evaluation_prompt)])

        try:
            selected = _parse_json(response.content)
        except (json.JSONDecodeError, IndexError):
            # fallback: pick the first in-stock product
            in_stock = [p for p in products if p.get("stock_quantity", 0) > 0]
            selected = in_stock[0] if in_stock else products[0]
            selected["reason"] = "Best available match"

        logger.info(
            f"[evaluate_node] Selected: {selected.get('name')}"
            f"at ₹{selected.get('price_inr')}"
        )
        return {
            "selected_product": selected,
            "current_step": "validate",
            "messages": [AIMessage(
                content=(
                    f"Selected: **{selected.get('name', 'Unknown')}** at ₹{selected.get('price_inr',0):,.0f}\n"
                    f"Reason: {selected.get('reason', 'Best match for your request')}"
                )
            )],
        }
    return evaluate_node

def make_validate_node(tools:list):
    """
    Node-3 : Run the policy engine to check if this agent can make this purchase.
    Fetches full product details (including category) before calling the policy check.
    """

    validate_tool = _get_tool(tools, "validate_purchase_mandate")
    details_tool = _get_tool(tools, "get_product_details")

    async def validate_node(state: AgentState) -> dict:
        product = state.get("selected_product", {})
        product_id = product.get("product_id")

        logger.info(f"[validate_node] Validating mandate for product: {product_id}")

        # Get product details
        raw_details = await details_tool.ainvoke({"product_id" : product_id})
        # details = json.loads(raw_details) if isinstance(raw_details, str) else raw_details
        if isinstance(raw_details, str):
            try:
                details = json.loads(raw_details)
            except json.JSONDecodeError:
                details ={}
        elif isinstance(raw_details, dict):
            details = raw_details
        else:
            details = {}

        if not details.get("found"):
            return {
                "current_step" : "failed",
                "error" : f"Product {product_id} could not be found for validation.",
                "messages" : [AIMessage(content = f"Product {product_id} not found")]
            }
        full_product = details.get("product", {})
        price_inr = full_product.get("price_inr", product.get("price_inr", 0))
        category = full_product.get("category", "electronics")

        # Call the policy engine via MCP tool
        raw_mandate = await validate_tool.ainvoke({
            "agent_id" : state["agent_id"],
            "product_id" : product_id,
            "product_category" : category,
            "quantity" : 1,
            "total_amount_inr" : price_inr
        })
        if isinstance(raw_mandate, str):
            try:
                mandate_result = json.loads(raw_mandate)
            except json.JSONDecodeError:
                mandate_result ={}
        elif isinstance(raw_mandate, dict):
            mandate_result = raw_mandate
        else :
            mandate_result = {}

        approved = mandate_result.get("approved", False)
        reason = mandate_result.get("reason", "Unknown")

        logger.info(f"[validate_node] Mandate decision: {approved} | Reason : {reason}")

        if approved:
            warnings = mandate_result.get("warnings", [])
            msg = f"Mandate approved for ₹{price_inr:,.0f} purchase."
            if warnings:
                msg += f"\n Warning: {warnings[0]}"

            return {
                "mandate_result" : mandate_result,
                "current_step" : "purchase",
                "messages" : [AIMessage(content = msg)]
            }
        else:
            # Get the specific check that failed for a clear message
            trace = mandate_result.get("decision_trace", [])
            failed = next((c for c in reversed(trace) if not c.get("passed")), {})

            return {
                "mandate_result" : mandate_result,
                "current_step" : "failed",
                "error": f"{reason} : {failed.get('detail', '')}",
                "messages" : [AIMessage(
                    content = f"Purchase rejected by policy engine. \nReason :{reason}"
                )],
            }
    return validate_node

def make_purchase_node(tools:list):
    """
    Node-4 : Execute the purchase - creates Razorpay order and payment link.
    """

    purchase_tool = _get_tool(tools, "execute_purchase")

    async def purchase_node(state: AgentState) -> dict:
        product = state.get("selected_product", {})
        pid = product.get('product_id')
        logger.info(f"[purchase_node] Executing purchase: {pid}")

        raw_result = await purchase_tool.ainvoke({
            "agent_id" : state["agent_id"],
            "product_id" : product.get("product_id"),
            "quantity" :1,
            "shipping_address" : state.get(
                "shipping_address",
                "123 Demo Street, Mumbai, Maharashtra 400001"
            ),
        })   

        if isinstance(raw_result, str):
            try:
                result = json.loads(raw_result)
            except json.JSONDecodeError:
                result= {}
        elif isinstance(raw_result, dict):
            result = raw_result
        else:
            result = {}
        success = result.get("success", False)

        logger.info(f"[purchase_node] Result: success = {success}")

        if success:
            return {
                "purchase_result": result,
                "current_step" : "done",
                "messages" : [AIMessage(
                    content = "Order created. Payment link generated."
                )],
            }
        return {
            "purchase_result" : result,
            "current_step" : "failed",
            "error" : result.get("error_message","Purchase failed"),
            "messages" : [AIMessage(content = f"Purchase failed : {result.get('error_message')}")]
        }
    return purchase_node

def make_respond_node():
    """
    Node 5 (terminal): Generate the final human-readable response.
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