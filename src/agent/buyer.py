"""
LangGraph Buyer Agent — compiles the StateGraph and runs purchase workflows.
"""

import os
import logging
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
    """After policy check: go to purchase if approved, else skip to respond."""
    return "purchase" if state.get("current_step") == "purchase" else "respond"


def build_graph(tools: list, llm: ChatOpenAI):
    """Compile the StateGraph with all nodes and routing logic."""
    graph = StateGraph(AgentState)

    graph.add_node("search",   make_search_node(tools, llm))
    graph.add_node("evaluate", make_evaluate_node(llm))
    graph.add_node("validate", make_validate_node(tools))
    graph.add_node("purchase", make_purchase_node(tools))
    graph.add_node("respond",  make_respond_node())

    graph.set_entry_point("search")

    graph.add_edge("search",   "evaluate")
    graph.add_edge("evaluate", "validate")

    graph.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"purchase": "purchase", "respond": "respond"},
    )

    graph.add_edge("purchase", "respond")
    graph.add_edge("respond",  END)

    return graph.compile()  


async def run_buyer_agent(
    user_request: str,
    agent_id: str = "agent-buyer-01",
    shipping_address: str = "123 Demo Street, Mumbai, Maharashtra 400001",
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
            "command": "python",
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