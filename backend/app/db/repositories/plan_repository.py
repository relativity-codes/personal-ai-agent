from app.db.models.plan import ExecutionPlan
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class PlanRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, plan_id: str):
        result = await session.execute(select(ExecutionPlan).where(ExecutionPlan.id == plan_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        plan = ExecutionPlan(**kwargs)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan
