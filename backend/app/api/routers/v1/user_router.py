from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.db.models.user import User
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# Pydantic schema for user response
class UserRead(BaseModel):
    id: UUID
    clerk_id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    default_github_repo: Optional[str] = None
    default_notion_db: Optional[str] = None
    timezone: Optional[str] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    mcp_tokens: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    clerk_id: str

router = APIRouter()


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    db_user = await user_repo.create(db, **user.model_dump())
    return db_user


@router.get("/", response_model=list[UserRead])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    users = await user_repo.get_all(db, skip, limit)
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    db_user = await user_repo.get_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    db_user = await user_repo.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await user_repo.update(db, db_user.id, **user.model_dump(exclude_unset=True))
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    success = await user_repo.delete_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return success
