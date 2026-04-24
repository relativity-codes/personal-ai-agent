from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, SessionDep, get_current_user, parse_uuid
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


class UserMeResponse(BaseModel):
    id: str
    google_id: str | None
    email: str
    name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    default_github_repo: str | None = None
    default_notion_db: str | None = None
    is_active: bool = True
    created_at: datetime | None = None


class UserMeUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = Field(default=None, max_length=50)
    default_github_repo: str | None = Field(default=None, max_length=255)
    default_notion_db: str | None = Field(default=None, max_length=255)


@router.get("/me", response_model=UserMeResponse)
async def read_me(
    session: SessionDep,
    user: CurrentUser = Depends(get_current_user),
):
    uid = parse_uuid(user["user_id"], "user_id")
    row = await UserRepository.get_by_id(session, uid)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserMeResponse(
        id=str(row.id),
        google_id=row.google_id,
        email=row.email,
        name=row.name,
        avatar_url=row.avatar_url,
        timezone=row.timezone,
        default_github_repo=row.default_github_repo,
        default_notion_db=row.default_notion_db,
        is_active=bool(row.is_active),
        created_at=row.created_at,
    )


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    session: SessionDep,
    body: UserMeUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    uid = parse_uuid(user["user_id"], "user_id")
    row = await UserRepository.get_by_id(session, uid)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    data = body.model_dump(exclude_unset=True)
    if data:
        await UserRepository.update(session, row.id, **data)
        await session.commit()
        await session.refresh(row)
        
    return UserMeResponse(
        id=str(row.id),
        google_id=row.google_id,
        email=row.email,
        name=row.name,
        avatar_url=row.avatar_url,
        timezone=row.timezone,
        default_github_repo=row.default_github_repo,
        default_notion_db=row.default_notion_db,
        is_active=bool(row.is_active),
        created_at=row.created_at,
    )
