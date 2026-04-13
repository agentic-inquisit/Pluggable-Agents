from typing import Annotated, TypedDict, Dict, Any, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

def update_context(existing: Dict[str, Any] | None, new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to merge context dictionaries instead of overwriting.
    Handles initial state where existing may be None.
    """
    if existing is None:
        return new if isinstance(new, dict) else {}
    
    if not isinstance(existing, dict) or not isinstance(new, dict):
        raise TypeError("Context must be a dictionary")
    
    return {**existing, **new}

class AgentState(TypedDict):
    """
    Standard state schema for LangGraph.
    - messages: Uses 'add_messages' to append to history rather than overwriting.
    - context: Uses a custom reducer to merge updates rather than replacing the whole dict.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    context: Annotated[Dict[str, Any], update_context]