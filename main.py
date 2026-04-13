import uuid
from langchain_core.messages import HumanMessage
from graph import app

def main():
    # Proper message format using HumanMessage
    initial_input = {
        "messages": [HumanMessage(content="Analyze this request and determine next steps.")],
        "context": {"user_id": "12345", "session_start": True}
    }
    
    # Generate unique thread_id for persistent sessions/checkpoints
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Starting orchestrator session: {thread_id}")
    print("-" * 50)
    
    try:
        for output in app.stream(initial_input, config):
            print(output)
    except Exception as e:
        print(f"Error during execution: {e}")
        raise
    
    print("-" * 50)
    print("Session completed.")

if __name__ == "__main__":
    main()