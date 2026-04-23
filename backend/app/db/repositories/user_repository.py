from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from uuid import UUID

class UserRepository:
    @staticmethod
    async def get_by_clerk_id(session: AsyncSession, clerk_id: str):
        result = await session.execute(select(User).where(User.clerk_id == clerk_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        user = User(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, clerk_id: str, **kwargs):
        query = (
            update(User)
            .where(User.clerk_id == clerk_id)
            .values(**kwargs)
            .returning(User)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalars().first()

    @staticmethod
    async def get_or_create(session: AsyncSession, **kwargs):
        user = await UserRepository.get_by_clerk_id(session, kwargs["clerk_id"])
        if user:
            return user
        return await UserRepository.create(session, **kwargs)

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        result = await session.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: UUID):
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def delete_by_id(session: AsyncSession, user_id: UUID) -> bool:
        result = await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def delete_by_clerk_id(session: AsyncSession, clerk_id: str) -> bool:
        result = await session.execute(delete(User).where(User.clerk_id == clerk_id))
        await session.commit()
        return result.rowcount > 0
