from app.db.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from uuid import UUID

class TaskRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, task_id: UUID):
        result = await session.execute(select(Task).where(Task.id == task_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        task = Task(**kwargs)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        result = await session.execute(select(Task).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, task_id: UUID, **kwargs):
        task = await TaskRepository.get_by_id(session, task_id)
        if task:
            for key, value in kwargs.items():
                setattr(task, key, value)
            await session.commit()
            await session.refresh(task)
        return task

    @staticmethod
    async def delete_by_id(session: AsyncSession, task_id: UUID) -> bool:
        result = await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()
        return result.rowcount > 0
