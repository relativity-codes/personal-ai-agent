class AuditRepository:
    pass
from app.db.models.audit_log import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
