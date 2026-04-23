from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.session_repository import SessionRepository
from app.db.models.session import Session
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=Session)
async def create_session(user_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository
    return await repo.create(db, user_id=user_id)

@router.get("/{session_id}", response_model=Session)
async def read_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository
    db_session = await repo.get_by_id(db, session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.get("/user/{user_id}", response_model=list[Session])
async def read_sessions_by_user(user_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository
    return await repo.get_all_by_user_id(db, user_id, skip, limit)

@router.delete("/{session_id}", response_model=bool)
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository
    success = await repo.delete_by_id(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return success
