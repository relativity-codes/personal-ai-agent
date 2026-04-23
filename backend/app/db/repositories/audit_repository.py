from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.db.models.audit_log import AuditLog


class AuditRepository:
    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        log = AuditLog(**kwargs)
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    @staticmethod
    async def get_by_user(session: AsyncSession, user_id: str, limit: int = 20):
        result = await session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        result = await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, log_id: UUID):
        result = await session.execute(select(AuditLog).where(AuditLog.id == log_id))
        return result.scalars().first()
