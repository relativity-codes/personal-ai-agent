from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.chat_history_repository import ChatHistoryRepository
from app.api.schemas import ChatHistoryRead
from uuid import UUID
from typing import List, Dict

router = APIRouter()

@router.get("/", response_model=list[ChatHistoryRead])
async def read_chat_histories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = ChatHistoryRepository
    return await repo.get_all(db, skip, limit)

@router.get("/{history_id}", response_model=ChatHistoryRead)
async def read_chat_history(history_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ChatHistoryRepository
    db_history = await repo.get_by_id(db, history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return db_history

@router.get("/session/{session_id}", response_model=List[Dict])
async def read_chat_history_by_session(session_id: str, db: AsyncSession = Depends(get_db)):
    repo = ChatHistoryRepository
    return await repo.get_history(db, session_id)

@router.delete("/{history_id}", response_model=bool)
async def delete_chat_history(history_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ChatHistoryRepository
    success = await repo.delete_by_id(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return success
