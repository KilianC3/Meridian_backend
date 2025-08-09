from __future__ import annotations

from fastapi import Request


async def rate_limit(_: Request) -> None:
    """No-op rate limiter dependency."""
    return None
