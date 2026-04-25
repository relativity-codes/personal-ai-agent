import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, parse_uuid
from app.agents.managerial_agent import create_managerial_graph
from app.agents.state import AgentState
from app.db.repositories.chat_history_repository import ChatHistoryRepository
from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.user_repository import UserRepository
from langgraph.graph import StateGraph
from app.core.config import settings
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    session_id: UUID | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: UUID

router = APIRouter()

def get_managerial_graph():
    graph = create_managerial_graph()
    return graph

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    graph: StateGraph = Depends(get_managerial_graph),
    db: AsyncSession = Depends(get_db),
    chat_history_repo: ChatHistoryRepository = Depends(),
) -> ChatResponse:
    session_id = request.session_id
    user_id_raw = user.get("user_id")
    if not user_id_raw:
        raise HTTPException(status_code=403, detail="User ID not found")
    
    user_id = parse_uuid(user_id_raw, "user_id")

    if session_id is None:
        # Create a new session if one is not provided
        new_session = await SessionRepository.create(db, user_id=user_id)
        session_id = new_session.id
    else:
        # Verify that the session belongs to the current user
        session = await SessionRepository.get_by_id(db, session_id)
        if not session or session.user_id != user_id:
            logger.warning(f"Session {session_id} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Invalid session ID")

    chat_history = await chat_history_repo.get_history(db, str(session_id))
    
    # Fetch full user context to provide to agents
    user_row = await UserRepository.get_by_id(db, user_id)
    user_context = {
        "name": user_row.name if user_row else None,
        "email": user_row.email if user_row else None,
        "timezone": user_row.timezone if user_row else "UTC",
        "default_github_repo": user_row.default_github_repo if user_row else None,
        "default_notion_db": user_row.default_notion_db if user_row else None,
    }

    initial_state: AgentState = {
        "user_id": user_id,
        "google_id": user.get("google_id", user_id),
        "user_context": user_context,
        "user_input": request.message,
        "session_id": str(session_id),
        "chat_history": chat_history or [],
        "needs_clarification": False,
        "validated_intent": None,
        "intent_confidence": 0.0,
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

    logger.info(f"Invoking graph for session {session_id} with user input: {request.message}")
    try:
        final_state = await graph.ainvoke(initial_state)
        
        # Defensive check for final_response
        response_message = final_state.get("final_response")
        if response_message is None or response_message == "":
            error_msg = final_state.get("error")
            response_message = f"I encountered an issue: {error_msg}" if error_msg else "Sorry, I encountered an issue and could not generate a response."

        await chat_history_repo.add_message(db, str(session_id), "user", request.message)
        await chat_history_repo.add_message(db, str(session_id), "agent", response_message)

        return ChatResponse(response=response_message, session_id=session_id)

    except Exception as e:
        log_exception(
            logger, 
            e, 
            context=f"Exception in chat endpoint for session {session_id}",
            extra_data={"initial_state_keys": list(initial_state.keys()), "user_input": request.message}
        )
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": str(e),
                "type": type(e).__name__,
                "session_id": str(session_id)
            }
        )
