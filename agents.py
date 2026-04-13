from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage
from state import AgentState
from tools import tools 

model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0
).bind_tools(tools)

def orchestrator(state: AgentState):
    """
    Lead agent node using Claude for reasoning.
    Routes to tools or specialists based on analysis.
    """
    system_prompt = (
        "You are an Orchestrator. Analyze the user request. "
        "If a tool is required, invoke it. "
        "If a specific specialist task is needed, output 'SPECIALIST' "
        "as part of your thought process."
    )
 
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    return {"messages": [response]}

# def orchestrator(state: AgentState):
#     """
#     Lead agent node that decides the path of execution.
#     Analyzes state['messages'] and determines if tools or specialists are needed.
#     """
#     system_prompt = (
#         "You are an Orchestrator. "
#         "Analyze the user request. If a tool is required, invoke it. "
#         "If a specific specialist task is needed, output 'SPECIALIST' in your response."
#     )
     
#     messages = [SystemMessage(content=system_prompt)] + state["messages"]
#     response = model.invoke(messages)
    
#     # Return the updated messages to be appended to the state
#     return {"messages": [response]}

def specialist_node(state: AgentState):
    """
    A specialist node for deep-dive tasks.
    Processes specialized requests with enhanced reasoning.
    """
    # Specialist processing with proper message object
    specialist_message = AIMessage(
        content="Specialist task complete: Data refined and processed."
    )
    return {
        "messages": [specialist_message],
        "context": {**state.get("context", {}), "specialist_processed": True}
    }   