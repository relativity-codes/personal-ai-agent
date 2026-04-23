from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.audit_repository import AuditRepository
from app.api.schemas import AuditLogRead
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=list[AuditLogRead])
async def read_audit_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    audit_repo = AuditRepository
    return await audit_repo.get_all(db, skip, limit)

@router.get("/{log_id}", response_model=AuditLogRead)
async def read_audit_log(log_id: UUID, db: AsyncSession = Depends(get_db)):
    audit_repo = AuditRepository
    db_log = await audit_repo.get_by_id(db, log_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return db_log

@router.get("/user/{user_id}", response_model=list[AuditLogRead])
async def read_audit_logs_by_user(user_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    audit_repo = AuditRepository
    return await audit_repo.get_by_user(db, user_id, limit)
