from __future__ import annotations
from typing import Any

# Global in-memory storage for plans
_PLAN_STORAGE: dict[str, dict[str, Any]] = {}

class PlanRepository:
    """
    In-memory Plan Repository for maximum performance.
    Plans are stored in a global dictionary.
    """
    
    @staticmethod
    async def get(plan_id: str) -> dict[str, Any] | None:
        """Fetch plan from memory."""
        return _PLAN_STORAGE.get(plan_id)

    @staticmethod
    async def create(plan_data: dict[str, Any]) -> None:
        """Store plan in memory."""
        plan_id = str(plan_data.get("id"))
        _PLAN_STORAGE[plan_id] = plan_data

    @staticmethod
    async def update_task_status(
        plan_id: str,
        task_id: str,
        status: str,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        """Update task status directly in memory."""
        plan = _PLAN_STORAGE.get(plan_id)
        if not plan:
            return

        # Update task status
        if "task_status" not in plan:
            plan["task_status"] = {}
        plan["task_status"][task_id] = status

        # Update results
        if result is not None:
            if "task_results" not in plan:
                plan["task_results"] = {}
            plan["task_results"][task_id] = result

        # Update errors
        if error:
            if "task_errors" not in plan:
                plan["task_errors"] = {}
            plan["task_errors"][task_id] = error

    @staticmethod
    async def delete_by_id(plan_id: str) -> bool:
        """Remove plan from memory."""
        if plan_id in _PLAN_STORAGE:
            del _PLAN_STORAGE[plan_id]
            return True
        return False
