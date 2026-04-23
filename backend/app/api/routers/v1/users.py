from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, SessionDep, get_current_user, parse_uuid
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


class UserMeResponse(BaseModel):
    id: str
    clerk_id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    is_active: bool = True


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
        clerk_id=row.clerk_id,
        email=row.email,
        name=row.name,
        avatar_url=row.avatar_url,
        timezone=row.timezone,
        is_active=bool(row.is_active),
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
        await UserRepository.update(session, row, **data)
        await session.commit()
    return UserMeResponse(
        id=str(row.id),
        clerk_id=row.clerk_id,
        email=row.email,
        name=row.name,
        avatar_url=row.avatar_url,
        timezone=row.timezone,
        is_active=bool(row.is_active),
    )
