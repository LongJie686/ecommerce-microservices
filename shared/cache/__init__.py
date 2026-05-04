"""Redis cache client with common patterns."""

from __future__ import annotations

import json
import logging
import random
from typing import Any

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class RedisClient:
    """Async Redis client with caching best practices."""

    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._url = url
        self._client: Any = None

    async def connect(self) -> None:
        if aioredis is None:
            raise ImportError("pip install redis")
        self._client = aioredis.from_url(self._url, decode_responses=True)
        logger.info("Redis connected: %s", self._url)

    async def close(self) -> None:
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def get_json(self, key: str) -> Any | None:
        val = await self.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        await self._client.set(key, value, ex=expire)

    async def set_json(self, key: str, value: Any, expire: int | None = None) -> None:
        await self.set(key, json.dumps(value, ensure_ascii=False), expire)

    async def delete(self, *keys: str) -> int:
        return await self._client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def cache_with_anti_penetration(self, key: str, value: Any, expire: int = 300, null_expire: int = 60) -> None:
        """Cache with cache penetration protection. Empty results cached with short TTL."""
        if value is None:
            await self.set_json(key, {"_null": True}, expire=null_expire)
        else:
            jitter = random.randint(0, 60)
            await self.set_json(key, value, expire=expire + jitter)

    async def get_with_anti_penetration(self, key: str) -> Any | None:
        """Get value, returns None for null-placeholders (penetration protection)."""
        val = await self.get_json(key)
        if val is None:
            return None
        if isinstance(val, dict) and val.get("_null"):
            return None
        return val

    async def acquire_lock(self, key: str, timeout: int = 10) -> bool:
        return bool(await self._client.set(key, "1", nx=True, ex=timeout))

    async def release_lock(self, key: str) -> None:
        await self._client.delete(key)
