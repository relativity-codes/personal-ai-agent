from app.db.models.plan import ExecutionPlan
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from uuid import UUID

class PlanRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, plan_id: UUID):
        result = await session.execute(select(ExecutionPlan).where(ExecutionPlan.id == plan_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        plan = ExecutionPlan(**kwargs)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        result = await session.execute(select(ExecutionPlan).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, plan_id: UUID, **kwargs):
        plan = await PlanRepository.get_by_id(session, plan_id)
        if plan:
            for key, value in kwargs.items():
                setattr(plan, key, value)
            await session.commit()
            await session.refresh(plan)
        return plan

    @staticmethod
    async def delete_by_id(session: AsyncSession, plan_id: UUID) -> bool:
        result = await session.execute(delete(ExecutionPlan).where(ExecutionPlan.id == plan_id))
        await session.commit()
        return result.rowcount > 0
