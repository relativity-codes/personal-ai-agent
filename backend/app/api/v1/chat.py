from fastapi import APIRouter, Depends

from app.api.deps import get_current_user

router = APIRouter()


@router.post("/")
async def chat_placeholder(user: dict = Depends(get_current_user)):
    return {"detail": "boilerplate", "user": user["user_id"]}
