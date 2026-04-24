from __future__ import annotations

import uuid
from typing import Any

from app.db.models.plan import ExecutionPlan
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from uuid import UUID

from app.db.session import async_session_factory, async_session_scope


def _plan_to_dict(row: ExecutionPlan) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "user_id": str(row.user_id),
        "session_id": row.session_id,
        "intent_type": row.intent_type,
        "status": row.status,
        "tasks": row.tasks or [],
        "task_status": dict(row.task_status or {}),
        "task_results": dict(row.task_results or {}),
        "task_errors": dict(row.task_errors or {}),
        "execution_order": list(row.execution_order or []),
    }

        
class PlanRepository:
    @staticmethod
    async def get(plan_id: str) -> dict[str, Any] | None:
        from sqlalchemy.orm import selectinload
        pid = uuid.UUID(plan_id)
        async with async_session_factory() as session:
            stmt = select(ExecutionPlan).where(ExecutionPlan.id == pid).options(selectinload(ExecutionPlan.tasks))
            result = await session.execute(stmt)
            row = result.scalars().first()
            if row is None:
                return None
            return _plan_to_dict(row)

    @staticmethod
    async def create(plan_data: dict[str, Any]) -> None:
        from app.db.models.task import Task
        async with async_session_scope() as session:
            ep = ExecutionPlan(
                id=uuid.UUID(plan_data["id"]),
                user_id=uuid.UUID(plan_data["user_id"]),
                session_id=plan_data["session_id"],
                intent_type=plan_data["intent_type"],
                status=plan_data.get("status", "pending"),
                task_status=plan_data.get("task_status", {}),
                task_results=plan_data.get("task_results", {}),
                task_errors=plan_data.get("task_errors", {}),
                execution_order=plan_data.get("execution_order", []),
            )
            
            # Convert tasks to Task instances
            tasks = []
            for t_data in plan_data.get("tasks", []):
                tasks.append(Task(
                    id=uuid.UUID(t_data["task_id"]),
                    session_id=plan_data["session_id"],
                    plan_id=ep.id,
                    step=t_data["step"],
                    description=t_data["description"],
                    mcp_server=t_data["mcp_server"],
                    tool=t_data["tool"],
                    parameters=t_data["arguments"],
                    depends_on=t_data.get("depends_on", []),
                    status=t_data.get("status", "pending")
                ))
            ep.tasks = tasks
            session.add(ep)

    @staticmethod
    async def update_task_status(
        plan_id: str,
        task_id: str,
        status: str,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        pid = uuid.UUID(plan_id)
        async with async_session_scope() as session:
            row = await session.get(ExecutionPlan, pid)
            if row is None:
                return
            ts = dict(row.task_status or {})
            ts[task_id] = status
            row.task_status = ts
            tr = dict(row.task_results or {})
            if result is not None:
                tr[task_id] = result
            row.task_results = tr
            te = dict(row.task_errors or {})
            if error:
                te[task_id] = error
            row.task_errors = te

    @staticmethod
    async def get_by_id(session: AsyncSession, plan_id: UUID):
        result = await session.execute(select(ExecutionPlan).where(ExecutionPlan.id == plan_id))
        return result.scalars().first()

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
