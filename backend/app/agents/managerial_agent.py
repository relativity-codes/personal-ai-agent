
from langgraph.graph import StateGraph, END
from typing import Literal

from app.agents.state import AgentState
from app.agents.intent_agent import create_intent_node
from app.agents.task_planner_agent import create_task_planner_node
from app.agents.action_agent import create_action_node
from app.agents.response_agent import create_response_node # Import the new response node
from app.core.openrouter import OpenRouterClient
from app.core.config import settings
from app.db.repositories.plan_repository import PlanRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository
from app.mcp_alt.registry import mcp_alt_registry

def should_continue(state: AgentState) -> Literal["task_planner", "action", "response", END]:
    """
    Deterministic router for the agent workflow.
    Priority order matters.
    """
    print("_________\n\n\nAgent State from should continue", state)
    
    # --- 0. Hard stop (safety) ---
    if state["iteration"] >= state["max_iterations"]:
        return "response"

    if state.get("error"):
        return "response"

    # --- 1. Clarification phase ---
    if state.get("needs_clarification") and state.get("intent_confidence", 0) < 0.7:
        return "response"

    # --- 2. Planning phase ---
    if not state.get("tasks"):
        return "task_planner"

    # --- 3. Execution complete ---
    if state["current_task_index"] >= len(state["tasks"]):
        return "response"

    # --- 4. Execution step ---
    current_task = state["tasks"][state["current_task_index"]]

    if current_task["status"] in ["pending", "in_progress"]:
        return "action"

    # --- 5. Fallback ---
    return "response"

def create_managerial_graph() -> StateGraph:
    """
    Production-grade orchestration graph for multi-agent workflow.
    """

    # --- Dependencies ---
    openrouter = OpenRouterClient(api_key=settings.OPENROUTER_API_KEY)
    plan_repo = PlanRepository()
    user_repo = UserRepository()
    audit_repo = AuditRepository()

    # --- Nodes ---
    intent_node = create_intent_node(openrouter, user_repo, audit_repo)
    planner_node = create_task_planner_node(mcp_alt_registry, plan_repo, openrouter, user_repo, audit_repo)
    action_node = create_action_node(mcp_alt_registry, openrouter, user_repo, audit_repo)
    response_node = create_response_node(openrouter, user_repo, audit_repo)

    # --- Graph ---
    workflow = StateGraph(AgentState)

    workflow.add_node("intent", intent_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("action", action_node)
    workflow.add_node("response", response_node)

    workflow.set_entry_point("intent")

    # --- Routers (IMPORTANT: separate logic) ---

    def route_from_intent(state: AgentState):
        print("_________\n\n\nAgent State from route from intent", state)
        intent = state.get("validated_intent") or {}
        if intent:
            return "planner"
        return "response"

    def route_from_planner(state: AgentState):
        print("_________\n\n\nAgent State from route from planner", state)
        tasks = state.get("tasks", [])
        if not tasks:
            return "response"

        if state.get("current_task_index", 0) >= len(tasks):
            return "response"

        return "action"

    def route_from_action(state: AgentState):
        print("_________\n\n\nAgent State from route from action", state)
        if state.get("error"):
            return "response"
        
        # All tasks from previous planner step are cleared in action_node
        # If there are more tasks in the overall plan that are pending, go back to planner
        plan_tasks = state.get("tasks", []) # This is already cleared in action_node though
        
        # We check the actual plan status from the state/DB
        all_tasks_complete = all(
            status in ["completed", "failed"]
            for status in state.get("task_status", {}).values()
        )
        
        if not all_tasks_complete:
            return "planner"
        return "response"

    # --- Edges ---
    workflow.add_conditional_edges(
        "intent",
        route_from_intent,
        {
            "planner": "planner",
            "response": "response",
        },
    )

    workflow.add_conditional_edges(
        "planner",
        route_from_planner,
        {
            "action": "action",
            "response": "response",
        },
    )

    workflow.add_conditional_edges(
        "action",
        route_from_action,
        {
            "planner": "planner",
            "response": "response",
        },
    )

    workflow.add_edge("response", END)

    return workflow.compile()