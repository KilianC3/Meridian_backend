from __future__ import annotations

import logging
from typing import Any, Iterable

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: SimpleConnectionPool | None = None


def init_pool() -> None:
    global _pool
    if _pool is not None:
        return
    try:
        _pool = SimpleConnectionPool(1, 5, dsn=settings.postgres_dsn)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to init DB pool: %s", exc)
        _pool = None


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


def get_conn():
    if _pool is None:  # pragma: no cover - defensive
        raise RuntimeError("DB pool not initialized")
    return _pool.getconn()


def release_conn(conn) -> None:
    if _pool is None:  # pragma: no cover - defensive
        conn.close()
        return
    _pool.putconn(conn)


def fetch_all(sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return list(rows)
    finally:
        release_conn(conn)


def fetch_one(sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
        return dict(row) if row else None
    finally:
        release_conn(conn)
