from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    async def get_or_create_user_from_google(
        session: AsyncSession, google_user_info: dict
    ) -> User:
        """
        Get or create a user from Google user info.
        """
        user = await UserRepository.get_by_google_id(
            session, google_user_info["sub"]
        )
        if not user:
            user = await UserRepository.get_by_email(session, google_user_info["email"])
            if user:
                await UserRepository.update(
                    session, user.id, google_id=google_user_info["sub"]
                )
            else:
                user = await UserRepository.create(
                    session,
                    google_id=google_user_info["sub"],
                    email=google_user_info["email"],
                    name=google_user_info.get("name"),
                    avatar_url=google_user_info.get("picture"),
                )
        await session.commit()
        return user
