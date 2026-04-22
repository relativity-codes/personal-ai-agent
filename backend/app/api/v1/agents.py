from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def agents_status():
    return {"detail": "boilerplate"}
