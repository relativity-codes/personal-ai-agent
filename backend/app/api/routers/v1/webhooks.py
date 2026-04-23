from fastapi import APIRouter

router = APIRouter()


@router.post("/clerk")
async def clerk_webhook_placeholder():
    return {"detail": "boilerplate"}
