from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        if self._client is not None:
            await self.disconnect()
        try:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            if self._client is not None:
                await self._client.ping()
        except Exception as exc:
            logger.warning("redis unavailable: %s", exc)
            self._client = None

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def health(self) -> str:
        if self._client is None:
            return "skipped"
        try:
            await self._client.ping()
            return "connected"
        except Exception as exc:
            return f"error: {exc}"

    async def get_json(self, key: str) -> Any | None:
        if self._client is None:
            return None
        try:
            raw = await self._client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.debug("redis get_json %s: %s", key, exc)
            return None

    async def set_json(self, key: str, value: Any, ttl: int = 3600) -> None:
        if self._client is None:
            return
        try:
            payload = json.dumps(value, default=str)
            if ttl > 0:
                await self._client.setex(key, ttl, payload)
            else:
                await self._client.set(key, payload)
        except Exception as exc:
            logger.debug("redis set_json %s: %s", key, exc)


redis_client = RedisCache()
