from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import CurrentUser, SessionDep, get_current_user, parse_uuid
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.db.models.user import User
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

# Pydantic schema for user response
class UserRead(BaseModel):
    id: UUID
    google_id: Optional[str] = None
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    default_github_repo: Optional[str] = None
    default_notion_db: Optional[str] = None
    timezone: Optional[str] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    mcp_tokens: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = Field(default=None, max_length=50)
    default_github_repo: str | None = Field(default=None, max_length=255)
    default_notion_db: str | None = Field(default=None, max_length=255)

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    google_id: str

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_me(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    uid = parse_uuid(user["user_id"], "user_id")
    db_user = await UserRepository.get_by_id(db, uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.patch("/me", response_model=UserRead)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    uid = parse_uuid(user["user_id"], "user_id")
    db_user = await UserRepository.get_by_id(db, uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = body.model_dump(exclude_unset=True)
    if data:
        updated_user = await UserRepository.update(db, db_user.id, **data)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user
        
    return db_user

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

@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    success = await user_repo.delete_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return success
