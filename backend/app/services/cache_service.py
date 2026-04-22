import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        try:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            if self._client is not None:
                await self._client.ping()
        except Exception as exc:
            logger.warning("redis unavailable: %s", exc)
            self._client = None

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def health(self) -> str:
        if self._client is None:
            return "skipped"
        try:
            await self._client.ping()
            return "connected"
        except Exception as exc:
            return f"error: {exc}"

    async def get_json(self, key: str) -> Any:
        return None

    async def set_json(self, key: str, value: Any, ttl: int = 3600) -> None:
        return None


redis_client = RedisCache()
