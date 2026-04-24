from __future__ import annotations

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
async def webhook_status() -> dict[str, str]:
    """Status endpoint for webhooks."""
    return {"status": "active"}
