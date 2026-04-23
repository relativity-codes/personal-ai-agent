from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.task_repository import TaskRepository
from app.api.schemas import TaskRead
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=TaskRead)
async def create_task(task_data: dict, db: AsyncSession = Depends(get_db)):
    repo = TaskRepository
    return await repo.create(db, **task_data)

@router.get("/", response_model=list[TaskRead])
async def read_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = TaskRepository
    return await repo.get_all(db, skip, limit)

@router.get("/{task_id}", response_model=TaskRead)
async def read_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TaskRepository
    db_task = await repo.get_by_id(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, task_data: dict, db: AsyncSession = Depends(get_db)):
    repo = TaskRepository
    db_task = await repo.update(db, task_id, **task_data)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}", response_model=bool)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TaskRepository
    success = await repo.delete_by_id(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return success
