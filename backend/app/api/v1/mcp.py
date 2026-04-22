from fastapi import APIRouter

router = APIRouter()


@router.get("/servers")
async def mcp_servers():
    return {"detail": "boilerplate", "servers": []}
