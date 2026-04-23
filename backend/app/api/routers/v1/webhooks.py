from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.services.webhook_service import process_clerk_webhook, verify_clerk_signature

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/clerk")
async def clerk_webhook(request: Request) -> dict[str, bool]:
    if not (settings.CLERK_WEBHOOK_SECRET or "").strip():
        raise HTTPException(status_code=503, detail="CLERK_WEBHOOK_SECRET is not configured")
    body = await request.body()
    headers = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }
    try:
        payload = verify_clerk_signature(body, headers)
    except Exception as exc:
        logger.debug("clerk webhook verify failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook signature") from exc

    await process_clerk_webhook(payload)
    return {"ok": True}
