
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import StateGraph

from app.agents.managerial_agent import create_managerial_graph
from app.agents.state import AgentState
from app.api.deps import get_current_user, get_db
from app.db.repositories.chat_history_repository import ChatHistoryRepository
from app.db.repositories.session_repository import SessionRepository

router = APIRouter()

def get_managerial_graph():
    graph = create_managerial_graph()
    return graph

@router.websocket("/chat")
async def chat_socket(
    websocket: WebSocket,
    graph: StateGraph = Depends(get_managerial_graph),
    db: AsyncSession = Depends(get_db),
    chat_history_repo: ChatHistoryRepository = Depends(),
):
    user = None
    try:
        auth_header = websocket.headers.get("Authorization")
        user = await get_current_user(auth_header)
        await websocket.accept()
    except Exception as e:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    user_id = user.get("id")
    if not user_id:
        await websocket.close(code=4001, reason="User ID not found")
        return

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            client_session_id = data.get("session_id")

            session_id: UUID | None = None
            if client_session_id:
                try:
                    session_id = UUID(client_session_id)
                except ValueError:
                    await websocket.send_json({"error": "Invalid session ID format"})
                    continue

            if session_id is None:
                new_session = await SessionRepository.create(db, user_id=user_id)
                session_id = new_session.id
                await websocket.send_json({"type": "session_created", "session_id": str(session_id)})
            else:
                session = await SessionRepository.get_by_id(db, session_id)
                if not session or session.user_id != user_id:
                    await websocket.send_json({"error": "Invalid session ID"})
                    continue

            chat_history = await chat_history_repo.get_history(str(session_id))

            initial_state: AgentState = {
                "user_input": message,
                "session_id": str(session_id),
                "chat_history": chat_history,
                "results": [],
                "tasks": [],
                "needs_clarification": False,
            }

            async for step in graph.astream(initial_state):
                await websocket.send_json(step)

            final_step = list(step.values())[0]
            final_response = final_step.get("final_response", "Completed.")

            await chat_history_repo.add_message(str(session_id), "user", message)
            await chat_history_repo.add_message(str(session_id), "agent", final_response)

            await websocket.send_json({"type": "final_response", "message": final_response, "session_id": str(session_id)})

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        await websocket.send_text(f"An error occurred: {str(e)}")
        await websocket.close(code=1011)
