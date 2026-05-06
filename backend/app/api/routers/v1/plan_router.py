from fastapi import APIRouter, HTTPException
from app.db.repositories.plan_repository import PlanRepository
from app.api.schemas import ExecutionPlanRead
from uuid import UUID

router = APIRouter()

@router.get("/{plan_id}", response_model=ExecutionPlanRead)
async def read_plan(plan_id: UUID):
    db_plan = await PlanRepository.get(str(plan_id))
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.delete("/{plan_id}", response_model=bool)
async def delete_plan(plan_id: UUID):
    success = await PlanRepository.delete_by_id(str(plan_id))
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return success

# Note: create_plan, read_plans, and update_plan are typically handled by agents 
# or specific workflow logic now that plans are ephemeral and stored in Redis.
# We keep the GET and DELETE for observability/cleanup via API.
