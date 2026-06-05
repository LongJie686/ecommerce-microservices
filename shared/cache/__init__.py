"""Redis cache client with multi-level caching and common patterns."""

from __future__ import annotations

import json
import logging
import random
import time
import threading
from typing import Any

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class LocalCache:
    """L1 in-process cache with TTL support.

    Used as the first level of a two-tier cache (L1 local + L2 Redis).
    Reduces Redis round-trips for frequently accessed hot data.
    Thread-safe via locking.
    """

    def __init__(self, max_size: int = 1000):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expire_at = entry
            if time.time() > expire_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                self._evict_expired()
                if len(self._store) >= self._max_size:
                    oldest = min(self._store, key=lambda k: self._store[k][1])
                    del self._store[oldest]
            self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


class RedisClient:
    """Async Redis client with multi-level caching (L1 local + L2 Redis)."""

    def __init__(self, url: str = "redis://localhost:6379/0", l1_max_size: int = 500):
        self._url = url
        self._client: Any = None
        self._l1 = LocalCache(max_size=l1_max_size)

    async def connect(self) -> None:
        if aioredis is None:
            raise ImportError("pip install redis")
        self._client = aioredis.from_url(self._url, decode_responses=True)
        logger.info("Redis connected: %s", self._url)

    async def close(self) -> None:
        if self._client:
            await self._client.close()

    def _ensure_connected(self) -> None:
        if self._client is None:
            raise RuntimeError("RedisClient is not connected. Call await connect() first.")

    async def get(self, key: str) -> str | None:
        self._ensure_connected()
        return await self._client.get(key)

    async def get_json(self, key: str) -> Any | None:
        val = await self.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        self._ensure_connected()
        await self._client.set(key, value, ex=expire)

    async def set_json(self, key: str, value: Any, expire: int | None = None) -> None:
        await self.set(key, json.dumps(value, ensure_ascii=False), expire)

    async def delete(self, *keys: str) -> int:
        self._ensure_connected()
        return await self._client.delete(*keys)

    async def exists(self, key: str) -> bool:
        self._ensure_connected()
        return bool(await self._client.exists(key))

    async def eval_script(self, script: str, numkeys: int, *args: str) -> Any:
        """Execute a Redis Lua script. Wraps redis.eval for encapsulation."""
        self._ensure_connected()
        return await self._client.eval(script, numkeys, *args)

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

    async def get_or_set_with_mutex(self, key: str, fetch_func, expire: int = 300,
                                     lock_timeout: int = 10) -> Any:
        """Cache breakdown protection: mutex lock pattern.

        When cache misses, only one request acquires the lock to fetch from DB.
        Other requests wait and retry, preventing DB overload from cache breakdown.
        """
        import asyncio

        cached = await self.get_with_anti_penetration(key)
        if cached is not None:
            return cached

        lock_key = f"lock:{key}"
        identifier = await self.acquire_lock(lock_key, timeout=lock_timeout)
        if identifier is None:
            # Another request is fetching, wait and retry
            for _ in range(3):
                await asyncio.sleep(0.5)
                cached = await self.get_with_anti_penetration(key)
                if cached is not None:
                    return cached
            return None

        try:
            # Double-check cache after acquiring lock
            cached = await self.get_with_anti_penetration(key)
            if cached is not None:
                return cached

            value = await fetch_func()
            await self.cache_with_anti_penetration(key, value, expire=expire)
            return value
        finally:
            await self.release_lock(lock_key, identifier)

    async def acquire_lock(self, key: str, timeout: int = 10, identifier: str | None = None) -> str | None:
        """Acquire distributed lock. Returns identifier if success, None if failed.

        Uses SET NX EX with unique identifier for safe release via Lua script.
        """
        import uuid
        if identifier is None:
            identifier = str(uuid.uuid4())
        result = await self._client.set(key, identifier, nx=True, ex=timeout)
        return identifier if result else None

    async def release_lock(self, key: str, identifier: str) -> bool:
        """Release distributed lock safely via Lua script.

        Only releases if the value matches our identifier, preventing
        accidental release of a lock re-acquired by another process.
        """
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = await self._client.eval(lua_script, 1, key, identifier)
        return result != 0

    async def get_multi_level(self, key: str) -> Any | None:
        """Two-tier cache read: L1 local cache -> L2 Redis.

        L1 has shorter TTL than L2 to ensure eventual consistency.
        """
        value = self._l1.get(key)
        if value is not None:
            return value
        value = await self.get_json(key)
        if value is not None:
            self._l1.set(key, value, ttl=30)
        return value

    async def set_multi_level(self, key: str, value: Any, expire: int = 300) -> None:
        """Write-through to both L1 and L2 caches."""
        self._l1.set(key, value, ttl=30)
        await self.set_json(key, value, expire=expire)

    async def delete_multi_level(self, key: str) -> None:
        """Invalidate both L1 and L2 caches."""
        self._l1.delete(key)
        await self.delete(key)
