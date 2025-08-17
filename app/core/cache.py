from __future__ import annotations

import time
from typing import Any, Dict, Optional

from app.core.config import settings

try:  # pragma: no cover - optional dependency
    import redis.asyncio as redis
except Exception:  # pragma: no cover - fallback
    redis = None  # type: ignore


class LocalCache:
    def __init__(self) -> None:
        self._store: Dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        exp, value = item
        if exp < time.time():
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        self._store[key] = (time.time() + ttl, value)


_client: Any | None = None
_local_cache = LocalCache()


async def init_cache() -> None:
    global _client
    if settings.redis_dsn and redis is not None:
        try:
            _client = redis.from_url(settings.redis_dsn)
            await _client.ping()
            return
        except Exception:  # pragma: no cover - fall back
            _client = None
    _client = None


def close_cache() -> None:
    global _client
    if _client is not None:
        try:
            _client.close()  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            pass
        _client = None


async def cache_get(key: str) -> Any | None:
    if _client is not None:
        return await _client.get(key)
    return _local_cache.get(key)


async def cache_set(key: str, value: Any, ttl: int = 30) -> None:
    if _client is not None:
        await _client.setex(key, ttl, value)
    else:
        _local_cache.set(key, value, ttl)
