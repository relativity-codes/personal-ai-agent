
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.db.repositories.plan_repository import PlanRepository

router = APIRouter()


class PlanStatusResponse(BaseModel):
    plan_id: uuid.UUID
    status: str
    intent: str
    tasks: List[Dict[str, Any]]
    task_status: Dict[str, str]
    task_results: Dict[str, Any]
    created_at: Any
    completed_at: Optional[Any] = None


@router.get("/{plan_id}/status", response_model=PlanStatusResponse)
async def get_plan_status(
    plan_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    plan_repo: PlanRepository = Depends(PlanRepository),
):
    """
    Retrieves the status of a specific execution plan for the current user.
    """
    plan = await plan_repo.get(plan_id)

    # Security check: Ensure the requested plan belongs to the current user.
    if not plan or str(plan.user_id) != user.get("user_id"):
        raise HTTPException(status_code=404, detail="Plan not found or access denied")

    return {
        "plan_id": plan.id,
        "status": plan.status,
        "intent": plan.intent_type,
        "tasks": plan.tasks,
        "task_status": plan.task_status,
        "task_results": plan.task_results,
        "created_at": plan.created_at,
        "completed_at": plan.completed_at,
    }
