
from langgraph.graph import StateGraph, END
from typing import Literal

from app.agents.state import AgentState
from app.agents.intent_agent import create_intent_node
from app.agents.task_planner_agent import create_task_planner_node
from app.agents.action_agent import create_action_node
from app.agents.response_agent import create_response_node # Import the new response node
from app.core.openrouter import OpenRouterClient
from app.db.repositories.plan_repository import PlanRepository
from app.services.mcp_registry import mcp_registry

def should_continue(state: AgentState) -> Literal["task_planner", "action", "response", END]:
    """
    Determine the next step in the agentic workflow based on the current state.
    """
    # If the intent is unclear, we need to ask a clarifying question.
    if state.get("needs_clarification"):
        return "response"
    
    # If we have a final response, the process is complete.
    if state.get("final_response"):
        return END
    
    # If there are tasks in the queue, execute them.
    if state.get("tasks"):
        return "action"
    
    # Otherwise, the default next step is to continue planning.
    return "task_planner"

def create_managerial_graph() -> StateGraph:
    """
    Creates and configures the main LangGraph for the multi-agent system.

    This graph defines the complete workflow, from intent classification to final response.
    """
    # Initialize dependencies
    openrouter = OpenRouterClient()
    plan_repo = PlanRepository()
    
    # Create all the agent nodes
    intent_node = create_intent_node(openrouter)
    task_planner_node = create_task_planner_node(plan_repo, openrouter)
    action_node = create_action_node(mcp_registry)
    response_node = create_response_node(openrouter) # Create the new response node
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("intent", intent_node)
    workflow.add_node("task_planner", task_planner_node)
    workflow.add_node("action", action_node)
    workflow.add_node("response", response_node)
    
    # Set the entry point of the graph
    workflow.set_entry_point("intent")
    
    # Define the edges and conditional routing
    workflow.add_edge("intent", "task_planner")
    workflow.add_conditional_edges(
        "task_planner",
        should_continue,
        {
            "action": "action",
            "response": "response",
            END: END
        }
    )
    workflow.add_edge("action", "task_planner")
    workflow.add_edge("response", END) # After responding, the flow ends
    
    # Compile the graph into a runnable object
    return workflow.compile()
