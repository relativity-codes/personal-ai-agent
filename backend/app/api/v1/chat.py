from fastapi import APIRouter, Depends, HTTPException
from langgraph.graph import StateGraph
from pydantic import BaseModel

from app.agents.managerial_agent import create_managerial_graph
from app.agents.state import AgentState
from app.api.deps import CurrentUser, get_current_user
from app.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


def get_managerial_graph() -> StateGraph:
    return create_managerial_graph()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: CurrentUser = Depends(get_current_user),
    graph: StateGraph = Depends(get_managerial_graph),
) -> ChatResponse:
    session_id = user.get("user_id", "anonymous")

    initial_state: AgentState = {
        "user_id": user["user_id"],
        "clerk_sub": user.get("clerk_sub", user["user_id"]),
        "session_id": session_id,
        "user_input": request.message,
        "validated_intent": None,
        "intent_confidence": 0.0,
        "needs_clarification": False,
        "clarification_question": None,
        "plan_id": None,
        "tasks": [],
        "task_status": {},
        "execution_order": [],
        "current_task_index": 0,
        "completed_tasks": [],
        "failed_tasks": [],
        "task_results": {},
        "final_response": None,
        "error": None,
        "iteration": 0,
        "max_iterations": settings.MAX_EXECUTION_ITERATIONS,
        "results": [],
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        response_message = final_state.get("final_response", "Sorry, I encountered an issue.")
        return ChatResponse(response=response_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}") from e
