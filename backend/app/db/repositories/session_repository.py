from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.db.models.session import Session

class SessionRepository:
    @staticmethod
    async def create(session: AsyncSession, user_id: UUID) -> Session:
        new_session = Session(user_id=user_id)
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        return new_session

    @staticmethod
    async def get_by_id(session: AsyncSession, session_id: UUID) -> Session | None:
        result = await session.execute(select(Session).where(Session.id == session_id))
        return result.scalars().first()

    @staticmethod
    async def get_all_by_user_id(session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Session]:
        result = await session.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_by_id(session: AsyncSession, session_id: UUID) -> bool:
        result = await session.execute(delete(Session).where(Session.id == session_id))
        await session.commit()
        return result.rowcount > 0
