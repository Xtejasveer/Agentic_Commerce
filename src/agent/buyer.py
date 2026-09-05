"""
LangGraph Buyer Agent — compiles the StateGraph and runs purchase workflows.
"""

import os
import sys
import uuid
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import (
    make_search_node,
    make_evaluate_node,
    make_validate_node,
    make_purchase_node,
    make_respond_node,
)
from src.config import settings

logger = logging.getLogger(__name__)

# In-memory registry for paused workflows awaiting human feedback
_pending_upsell_actions: dict[str, dict] = {}


def get_llm() -> ChatOpenAI:
    """Initialize ChatOpenAI pointed at OpenRouter."""
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in your .env file.")
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        openai_api_key=settings.OPENROUTER_API_KEY, 
        model=settings.OPENROUTER_MODEL,
        temperature=0,
    )


def _route_after_validate(state: AgentState) -> str:
    """After policy check: loop back if recovering, go to upsell eval if approved, else respond."""
    step = state.get("current_step")
    if step == "recover":
        return "validate"
    elif step == "purchase":
        return "evaluate_upsell"
    return "respond"


def _route_after_upsell(state: AgentState) -> str:
    """After upsell eval: halt for human approval if accepted, otherwise proceed to purchase."""
    step = state.get("current_step")
    if step == "awaiting_upsell_approval":
        return "end"
    return "purchase"


def build_graph(tools: list, llm: ChatOpenAI):
    """Compile the StateGraph with all nodes and routing logic."""
    from src.agent.nodes import make_evaluate_upsell_node
    
    graph = StateGraph(AgentState)

    graph.add_node("search",   make_search_node(tools, llm))
    graph.add_node("evaluate", make_evaluate_node(llm))
    graph.add_node("validate", make_validate_node(tools))
    graph.add_node("evaluate_upsell", make_evaluate_upsell_node(tools, llm))
    graph.add_node("purchase", make_purchase_node(tools))
    graph.add_node("respond",  make_respond_node())

    graph.set_entry_point("search")

    graph.add_edge("search",   "evaluate")
    
    graph.add_conditional_edges(
        "evaluate",
        lambda state: "validate" if state.get("selected_product", {}).get("product_id") else "respond",
        {"validate": "validate", "respond": "respond"},
    )

    graph.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"validate": "validate", "evaluate_upsell": "evaluate_upsell", "respond": "respond"},
    )

    graph.add_conditional_edges(
        "evaluate_upsell",
        _route_after_upsell,
        {"purchase": "purchase", "end": END},
    )
    graph.add_edge("purchase", "respond")
    graph.add_edge("respond",  END)

    return graph.compile()  


async def run_buyer_agent(
    user_request: str,
    agent_id: str = "agent-buyer-01",
    shipping_address: str = "123 Demo Street, Mumbai, Maharashtra 400001",
    api_key: str = "",
) -> AgentState:
    """
    Run the full buyer agent workflow for a natural language purchase request.
    Spawns the MCP server as a subprocess, loads its tools, builds the graph,
    and returns the final state.
    """
    llm = get_llm()

    mcp_config = {
        "merchant": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["src/mcp_server.py"],
            "env": {**os.environ, "PYTHONPATH": os.getcwd()},
        }
    }

    # Fix 3: new API — no context manager, await get_tools() directly
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()

    logger.info(f"Loaded {len(tools)} MCP tools: {[t.name for t in tools]}")

    compiled = build_graph(tools, llm)

    initial_state: AgentState = {
        "messages": [],
        "user_request": user_request,
        "agent_id": agent_id,
        "shipping_address": shipping_address,
        "api_key": api_key,
        "search_results": [],
        "selected_product": None,
        "mandate_result": None,
        "purchase_result": None,
        "current_step": "search",
        "final_response": None,
        "error": None,
    }

    final_state = await compiled.ainvoke(initial_state)
    return final_state


async def stream_buyer_agent(
    user_request: str,
    agent_id: str = "agent-buyer-01",
    shipping_address: str = "123 Demo Street, Mumbai, Maharashtra 400001",
    api_key: str = "",
):
    """
    Generator that yields intermediate execution steps in real-time,
    finishing with the final agent response.
    """
    now_str = datetime.now().strftime("%H:%M:%S")
    yield {
        "type": "step",
        "time": now_str,
        "text": f"Agent {agent_id} requested: \"{user_request}\""
    }

    llm = get_llm()

    mcp_config = {
        "merchant": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["src/mcp_server.py"],
            "env": {**os.environ, "PYTHONPATH": os.getcwd()},
        }
    }

    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    compiled = build_graph(tools, llm)

    initial_state: AgentState = {
        "messages": [],
        "user_request": user_request,
        "agent_id": agent_id,
        "shipping_address": shipping_address,
        "api_key": api_key,
        "search_results": [],
        "selected_product": None,
        "mandate_result": None,
        "purchase_result": None,
        "current_step": "search",
        "final_response": None,
        "error": None,
        "recovery_attempted": False,
        "recovered_from_rejection": False,
        "recovery_narrative": None,
    }

    latest_state = dict(initial_state)

    async for output in compiled.astream(initial_state):
        if not isinstance(output, dict):
            continue

        for node_name, node_output in output.items():
            if not isinstance(node_output, dict):
                continue

            now_str = datetime.now().strftime("%H:%M:%S")
            latest_state.update(node_output)

            if node_name == "search":
                products = node_output.get("search_results", [])
                err = node_output.get("error")
                query_words = user_request.split()[:4]
                query_summary = " ".join(query_words)
                if products:
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🔍 Searching catalog for {query_summary}... · {len(products)} results found"
                    }
                else:
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🔍 Searching catalog for {query_summary}... · 0 results found"
                    }

            elif node_name == "evaluate":
                selected = node_output.get("selected_product")
                if selected and selected.get("product_id"):
                    price = selected.get("price_inr", 0)
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🎯 Selected product: {selected.get('name')} · ₹{price:,.0f}"
                    }

            elif node_name == "validate":
                mandate_res = node_output.get("mandate_result", {})
                current_step = node_output.get("current_step")
                selected = latest_state.get("selected_product", {})
                price = selected.get("price_inr", 0) if selected else 0
                name = selected.get("name", "Product") if selected else "Product"

                if current_step == "recover":
                    alt = mandate_res.get("recommended_alternative", {})
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🔄 Policy check: Rejection triggered · Auto-recovering alternative: {alt.get('name')} (₹{alt.get('price_inr', 0):,.0f})"
                    }
                elif mandate_res.get("approved"):
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"📋 Policy check: {name} ₹{price:,.0f} · ✅ Within limits"
                    }
                else:
                    reason = mandate_res.get("reason", "Mandate policy rejected")
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"📋 Policy check: {name} ₹{price:,.0f} · ❌ Rejected ({reason})"
                    }

            elif node_name == "evaluate_upsell":
                addon = node_output.get("addon_product") or node_output.get("suggested_addon")
                decision = node_output.get("addon_decision")
                if addon:
                    dec_text = "Proposes Accept" if decision == "accept" else "Declined"
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🎁 Upsell offered: {addon.get('name')} ₹{addon.get('price_inr', 0):,.0f} · Agent {dec_text}"
                    }

                # If the agent decided to accept the upsell, pause for human feedback!
                if decision == "accept" and addon:
                    action_id = f"upsell_{uuid.uuid4().hex[:8]}"
                    _pending_upsell_actions[action_id] = {
                        "action_id": action_id,
                        "latest_state": dict(latest_state),
                        "agent_id": agent_id,
                        "api_key": api_key,
                        "shipping_address": shipping_address,
                        "addon": addon,
                        "created_at": datetime.now(),
                    }
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"🤝 Human Feedback Required: Awaiting your decision to bundle {addon.get('name')} (+₹{addon.get('price_inr', 0):,.0f})"
                    }
                    primary_prod = latest_state.get("selected_product") or {}
                    primary_price = float(primary_prod.get("price_inr") or 0)
                    addon_price = float(addon.get("price_inr") or 0)
                    yield {
                        "type": "upsell_approval_required",
                        "action_id": action_id,
                        "primary_product": primary_prod,
                        "addon_product": addon,
                        "agent_narration": node_output.get("addon_narration") or "This add-on complements your selected product within budget limits.",
                        "primary_price": primary_price,
                        "addon_price": addon_price,
                        "total_with_addon": primary_price + addon_price,
                    }
                    return

            elif node_name == "purchase":
                purch = node_output.get("purchase_result", {})
                if purch.get("success"):
                    order_ref = purch.get("razorpay_order_id") or purch.get("order_id", "created")
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"✅ Purchase complete · Razorpay order {order_ref} created"
                    }
                else:
                    err = purch.get("error", "Payment failed")
                    yield {
                        "type": "step",
                        "time": now_str,
                        "text": f"❌ Purchase execution failed: {err}"
                    }

    # Final response
    final_msg = latest_state.get("final_response")
    if not final_msg:
        if latest_state.get("error"):
            final_msg = f"❌ Purchase could not be completed.\n\nReason: {latest_state['error']}"
        elif latest_state.get("messages"):
            final_msg = latest_state["messages"][-1].content
        else:
            final_msg = "Task completed."

    yield {
        "type": "done",
        "response": final_msg
    }


async def stream_buyer_agent_resume(action_id: str, approved: bool):
    """
    Resume an agent purchase flow after human feedback on an upsell offer.
    - If approved: bundles the addon product and executes purchase.
    - If declined: clears the addon and executes purchase for the primary product only.
    Always guarantees the primary product is purchased.
    """
    action_data = _pending_upsell_actions.pop(action_id, None)
    if not action_data:
        yield {
            "type": "done",
            "response": "❌ Upsell action expired or already processed."
        }
        return

    latest_state = action_data["latest_state"]
    addon = action_data["addon"]
    agent_id = action_data["agent_id"]
    api_key = action_data["api_key"]
    shipping_address = action_data["shipping_address"]
    primary = latest_state.get("selected_product") or {}

    now_str = datetime.now().strftime("%H:%M:%S")

    from src.database.session import SessionLocal
    from src.catalog.service import log_audit_event
    from src.schemas.audit import AuditEventType

    if approved:
        yield {
            "type": "step",
            "time": now_str,
            "text": f"👤 Human Feedback: User APPROVED upsell bundle · Adding {addon.get('name')} (+₹{addon.get('price_inr', 0):,.0f})"
        }
        latest_state["suggested_addon"] = addon
        latest_state["addon_decision"] = "accept"
        latest_state["human_feedback"] = "approved"

        try:
            db = SessionLocal()
            try:
                log_audit_event(db, {
                    "event_type": AuditEventType.UPSELL_ACCEPTED,
                    "agent_id": agent_id,
                    "product_id": addon.get("addon_product_id"),
                    "details": {
                        "resolved_by": "human_feedback",
                        "narration": "User approved the upsell bundle."
                    }
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to log upsell accept: {e}")

    else:
        yield {
            "type": "step",
            "time": now_str,
            "text": f"👤 Human Feedback: User DECLINED add-on · Proceeding with {primary.get('name')} only"
        }
        latest_state["suggested_addon"] = None
        latest_state["addon_decision"] = "declined"
        latest_state["human_feedback"] = "declined"

        try:
            db = SessionLocal()
            try:
                log_audit_event(db, {
                    "event_type": AuditEventType.UPSELL_REJECTED,
                    "agent_id": agent_id,
                    "product_id": addon.get("addon_product_id"),
                    "details": {
                        "resolved_by": "human_feedback",
                        "narration": "User opted to decline the upsell bundle."
                    }
                })
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to log upsell reject: {e}")

    # Step: Execute purchase with MCP tools
    mcp_config = {
        "merchant": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["src/mcp_server.py"],
            "env": {**os.environ, "PYTHONPATH": os.getcwd()},
        }
    }
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()

    purchase_fn = make_purchase_node(tools)
    purch_res = await purchase_fn(latest_state)
    latest_state.update(purch_res)

    now_str = datetime.now().strftime("%H:%M:%S")
    purch = purch_res.get("purchase_result", {})
    if purch.get("success"):
        order_ref = purch.get("razorpay_order_id") or purch.get("order_id", "created")
        yield {
            "type": "step",
            "time": now_str,
            "text": f"✅ Purchase complete · Razorpay order {order_ref} created"
        }
    else:
        err = purch.get("error_message") or purch.get("error", "Payment failed")
        yield {
            "type": "step",
            "time": now_str,
            "text": f"❌ Purchase execution failed: {err}"
        }

    # Step: Build final response with decision rationale
    respond_fn = make_respond_node()
    resp_res = await respond_fn(latest_state)
    final_msg = resp_res.get("final_response") or "Task completed."

    yield {
        "type": "done",
        "response": final_msg
    }