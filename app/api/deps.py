from __future__ import annotations

from fastapi import HTTPException, Request

from app.api.errors import problem
from app.core.config import Settings, get_settings
from app.db import redis


def get_app_settings() -> Settings:
    return get_settings()


RATE_LIMIT = 5
WINDOW = 60


async def rate_limit(request: Request) -> None:
    """Simple Redis-backed rate limiter."""
    try:
        client = await redis.init_client()
        identifier = request.client.host
        key = f"rl:{identifier}"
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, WINDOW)
        if count > RATE_LIMIT:
            raise problem(429, "Too Many Requests", "Rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        # If Redis is unavailable, disable rate limiting gracefully
        return None
    return None
