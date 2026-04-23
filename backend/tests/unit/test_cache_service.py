import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.cache_service import RedisCache


@pytest.mark.asyncio
async def test_cache_json_without_redis_no_crash():
    cache = RedisCache()
    assert await cache.get_json("any") is None
    await cache.set_json("any", {"a": 1}, ttl=60)


@pytest.mark.asyncio
async def test_cache_json_roundtrip_mocked():
    cache = RedisCache()
    mock_redis = MagicMock()
    store: dict[str, str] = {}

    async def mock_get(key: str):
        return store.get(key)

    async def mock_setex(key: str, ttl: int, value: str):
        store[key] = value

    mock_redis.get = AsyncMock(side_effect=mock_get)
    mock_redis.setex = AsyncMock(side_effect=mock_setex)
    mock_redis.ping = AsyncMock()
    cache._client = mock_redis

    await cache.set_json("k1", {"n": 42}, ttl=10)
    out = await cache.get_json("k1")
    assert out == {"n": 42}
    mock_redis.setex.assert_called_once()
    key, ttl, payload = mock_redis.setex.call_args[0]
    assert key == "k1"
    assert ttl == 10
    assert json.loads(payload) == {"n": 42}
