from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.plan_repository import PlanRepository
from app.db.models.plan import ExecutionPlan
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=ExecutionPlan)
async def create_plan(plan_data: dict, db: AsyncSession = Depends(get_db)):
    repo = PlanRepository
    return await repo.create(db, **plan_data)

@router.get("/", response_model=list[ExecutionPlan])
async def read_plans(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = PlanRepository
    return await repo.get_all(db, skip, limit)

@router.get("/{plan_id}", response_model=ExecutionPlan)
async def read_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = PlanRepository
    db_plan = await repo.get_by_id(db, plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.put("/{plan_id}", response_model=ExecutionPlan)
async def update_plan(plan_id: UUID, plan_data: dict, db: AsyncSession = Depends(get_db)):
    repo = PlanRepository
    db_plan = await repo.update(db, plan_id, **plan_data)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.delete("/{plan_id}", response_model=bool)
async def delete_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = PlanRepository
    success = await repo.delete_by_id(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return success
