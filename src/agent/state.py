from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # LangChain message history (HumanMessage, AIMessage, ToolMessage)
    messages: Annotated[list, add_messages]

    #Input
    user_request : str
    agent_id: str
    api_key: str
    shipping_address: str

    # Intermediate state
    search_results:list
    selected_product: Optional[dict]
    suggested_addon: Optional[dict]
    addon_decision: Optional[str]
    mandate_result: Optional[dict]
    purchase_result: Optional[dict]

    # Control Flow
    current_step: str
    final_response: Optional[str]
    error: Optional[str]

