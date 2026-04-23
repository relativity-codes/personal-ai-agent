from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)


def verify_clerk_signature(body: bytes, headers: dict[str, str]) -> dict[str, Any]:
    if not (settings.CLERK_WEBHOOK_SECRET or "").strip():
        raise ValueError("CLERK_WEBHOOK_SECRET is not set")
    from svix.webhooks import Webhook

    wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
    return wh.verify(body, headers)


def _primary_email(user: dict[str, Any]) -> str:
    primary_id = user.get("primary_email_address_id")
    for entry in user.get("email_addresses") or []:
        if not isinstance(entry, dict):
            continue
        if primary_id and entry.get("id") == primary_id:
            return str(entry.get("email_address") or "")
    for entry in user.get("email_addresses") or []:
        if isinstance(entry, dict) and entry.get("email_address"):
            return str(entry["email_address"])
    return ""


async def process_clerk_webhook(payload: dict[str, Any]) -> None:
    etype = str(payload.get("type") or "")
    data = payload.get("data")
    if not isinstance(data, dict):
        logger.warning("clerk webhook ignored: missing data object type=%s", etype)
        return

    if etype in ("user.created", "user.updated"):
        clerk_id = str(data.get("id") or "")
        if not clerk_id:
            return
        email = _primary_email(data) or "unknown@users.clerk"
        first = data.get("first_name")
        last = data.get("last_name")
        name_parts = [p for p in (first, last) if p]
        name = (
            " ".join(str(p) for p in name_parts) if name_parts else data.get("username")
        )
        image = data.get("image_url") or data.get("profile_image_url")

        async with async_session_factory() as session:
            await UserRepository.upsert_from_clerk(
                session,
                clerk_id=clerk_id,
                email=email,
                name=str(name) if name else None,
                avatar_url=str(image) if image else None,
            )
            await session.commit()
        logger.info("clerk webhook synced user type=%s clerk_id=%s", etype, clerk_id)
        return

    if etype == "user.deleted":
        clerk_id = str(data.get("id") or "")
        if not clerk_id:
            return
        async with async_session_factory() as session:
            user = await UserRepository.get_by_clerk_id(session, clerk_id)
            if user is not None:
                user.is_active = False
                await session.commit()
        logger.info("clerk webhook deactivated user clerk_id=%s", clerk_id)
