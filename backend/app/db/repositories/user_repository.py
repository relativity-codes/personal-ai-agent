from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID | str) -> User | None:
        uid = uuid.UUID(str(user_id))
        return await session.get(User, uid)

    @staticmethod
    async def get_by_clerk_id(session: AsyncSession, clerk_id: str) -> User | None:
        result = await session.execute(select(User).where(User.clerk_id == clerk_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs: Any) -> User:
        user = User(**kwargs)
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, user: User, **kwargs: Any) -> User:
        for k, v in kwargs.items():
            if hasattr(user, k) and v is not None:
                setattr(user, k, v)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def upsert_from_clerk(
        session: AsyncSession,
        *,
        clerk_id: str,
        email: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        existing = await UserRepository.get_by_clerk_id(session, clerk_id)
        if existing:
            existing.email = email or existing.email
            if name is not None:
                existing.name = name
            if avatar_url is not None:
                existing.avatar_url = avatar_url
            await session.flush()
            await session.refresh(existing)
            return existing
        return await UserRepository.create(
            session,
            clerk_id=clerk_id,
            email=email or "unknown@users.clerk",
            name=name,
            avatar_url=avatar_url,
        )
