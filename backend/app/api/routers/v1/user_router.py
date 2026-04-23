from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.db.models.user import User
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    clerk_id: str

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    return await user_repo.create(db, **user.model_dump())

@router.get("/", response_model=list[User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    return await user_repo.get_all(db, skip, limit)

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    db_user = await user_repo.get_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: UUID, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    db_user = await user_repo.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await user_repo.update(db, db_user.clerk_id, **user.model_dump(exclude_unset=True))
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository
    success = await user_repo.delete_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return success
