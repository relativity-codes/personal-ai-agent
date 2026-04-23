
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.agents.managerial_agent import create_managerial_graph
from app.agents.state import AgentState
from app.db.repositories.chat_history_repository import ChatHistoryRepository
from app.db.repositories.session_repository import SessionRepository
from langgraph.graph import StateGraph

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
    user_id = user.get("id")

    if not user_id:
        raise HTTPException(status_code=403, detail="User ID not found")

    if session_id is None:
        # Create a new session if one is not provided
        new_session = await SessionRepository.create(db, user_id=user_id)
        session_id = new_session.id
    else:
        # Verify that the session belongs to the current user
        session = await SessionRepository.get_by_id(db, session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Invalid session ID")

    chat_history = await chat_history_repo.get_history(str(session_id))

    initial_state: AgentState = {
        "user_input": request.message,
        "session_id": str(session_id),
        "chat_history": chat_history,
        "results": [],
        "tasks": [],
        "needs_clarification": False,
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        response_message = final_state.get("final_response", "Sorry, I encountered an issue.")

        await chat_history_repo.add_message(str(session_id), "user", request.message)
        await chat_history_repo.add_message(str(session_id), "agent", response_message)

        return ChatResponse(response=response_message, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
