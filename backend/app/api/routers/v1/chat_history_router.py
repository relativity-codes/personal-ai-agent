import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.db.repositories.chat_history_repository import ChatHistoryRepository
from app.api.schemas import ChatHistoryRead
from uuid import UUID
from typing import List, Dict
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=list[ChatHistoryRead])
async def read_chat_histories(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = UUID(current_user["user_id"])
        repo = ChatHistoryRepository
        return await repo.get_all_for_user(db, user_id, skip, limit)
    except Exception as e:
        log_exception(logger, e, context="Failed to read chat histories for user")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat histories")

@router.get("/{history_id}", response_model=ChatHistoryRead)
async def read_chat_history(history_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        repo = ChatHistoryRepository
        db_history = await repo.get_by_id(db, history_id)
        if db_history is None:
            raise HTTPException(status_code=404, detail="Chat history not found")
        return db_history
    except HTTPException:
        raise
    except Exception as e:
        log_exception(logger, e, context=f"Failed to read chat history {history_id}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.get("/session/{session_id}", response_model=List[Dict])
async def read_chat_history_by_session(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        repo = ChatHistoryRepository
        return await repo.get_history(db, session_id)
    except Exception as e:
        log_exception(logger, e, context=f"Failed to read chat history for session {session_id}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session chat history")

@router.delete("/{history_id}", response_model=bool)
async def delete_chat_history(history_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ChatHistoryRepository
    success = await repo.delete_by_id(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return success
