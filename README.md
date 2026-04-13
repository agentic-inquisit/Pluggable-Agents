# Multi-Agent Orchestration Framework

A modular, stateful multi-agent system built with **LangGraph** and **Claude 3.5 Sonnet**. 
The framework uses an orchestrator-specialist architecture to decompose complex tasks into discrete, manageable sub-tasks.

---

## Architecture Overview

The system follows a **supervisor-worker pattern** where a central orchestrator maintains the session state and delegates work to specialized agents or external tools.

* **Orchestrator:** The reasoning core that interprets user intent and routes execution flow.
* **Specialists:** Dedicated nodes for complex data processing and domain-specific transformations.
* **State Machine:** Managed by **LangGraph**, providing persistent session memory and explicit context sharing across nodes.
* **Tools:** Python-based functions registered as tools, enabling external API connectivity and real-time data retrieval.

---

## Getting Started

### Prerequisites
* **Docker & Docker Compose** installed locally.
* **Anthropic API Key** for Claude 3.5 Sonnet.

### Installation
1.  **Clone the repository and set up environment:**
    ```bash
    # Create .env file with your API credentials
    echo "ANTHROPIC_API_KEY=your_key_here" > .env
    ```

2.  **Build and run the containerized environment:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Enter the isolated development environment:**
    ```bash
    docker exec -it langgraph_dev /bin/bash
    ```

---

## Project Structure

* `state.py`: Defines the `AgentState` schema using `TypedDict` and custom reducers for context merging.
* `tools.py`: Contains function-calling logic with structured docstrings for LLM interpretation.
* `agents.py`: Defines the agent nodes, including system instructions and LLM bindings.
* `graph.py`: The execution engine (Runner) defining the graph topology and routing logic.
* `main.py`: Entry point for executing the graph workflow.

---

## Development Guidelines

### State Management
The system uses an explicit `AgentState` schema. To update the shared context, return a dictionary from your node functions; the custom reducer will automatically merge new data into the existing session context.

### Adding New Specialists
1.  Define the logic in `agents.py` as a function accepting `AgentState`.
2.  Register the node in `graph.py` using `workflow.add_node()`.
3.  Define routing logic in the conditional edges to determine when the orchestrator should hand off control.
---

## Patterns & Best Practices
* **Explicit State:** Avoid side effects; pass all necessary data through the `AgentState` context.
* **Modular Routing:** Use conditional edges to handle tool-calling and agent handoffs, keeping the orchestrator logic clean.
* **Resilient Tools:** Always return error messages as strings rather than raising unhandled exceptions to allow the agent to self-correct.