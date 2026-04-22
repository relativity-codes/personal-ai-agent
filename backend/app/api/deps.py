from fastapi import Header, HTTPException

from app.config import settings


async def get_current_user(authorization: str | None = Header(default=None, alias="Authorization")):
    if settings.DEV_AUTH_BYPASS:
        return {"user_id": "dev-user", "email": "dev@localhost"}
    raise HTTPException(status_code=401, detail="Authentication not configured")
