from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents import orchestrator, specialist_node
from state import AgentState
from tools import tools

workflow = StateGraph(AgentState)
 
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("specialist", specialist_node)
workflow.add_node("tool_executor", ToolNode(tools))
 
workflow.set_entry_point("orchestrator")
 
def router(state: AgentState):
    """Route to tools, specialist, or end based on last message."""
    last_msg = state["messages"][-1]
    
    # Check for tool calls
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_executor"
    
    # Check for specialist routing signal
    if hasattr(last_msg, "content") and last_msg.content and "SPECIALIST" in str(last_msg.content):
        return "specialist"
    
    # End of workflow
    return END

workflow.add_conditional_edges(
    "orchestrator",
    router,
    {"tool_executor": "tool_executor", "specialist": "specialist", END: END}
)
 
workflow.add_edge("tool_executor", "orchestrator")
workflow.add_edge("specialist", "orchestrator")
 
app = workflow.compile()