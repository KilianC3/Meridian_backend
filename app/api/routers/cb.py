from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi import Query

from app.api.schemas.common import Page
from app.core import cache, db


class CBBank(str, Enum):
    FED = "FED"
    ECB = "ECB"
    BOE = "BOE"


class CBType(str, Enum):
    decision = "decision"
    statement = "statement"
    minutes = "minutes"
    speech = "speech"
    any = "any"


router = APIRouter(tags=["central_bank"])


@router.get("/cb")
async def get_cb_statements(
    bank: CBBank = Query(...),
    type: CBType = CBType.any,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"cb:{bank.value}:{type.value}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT statement_id, central_bank, type, published_at, title, url, hawkish_dovish_score "
        "FROM cb_statements "
        "WHERE central_bank = %(bank)s "
        "AND (%(type)s = 'any' OR type = %(type)s) "
        "AND (%(start)s IS NULL OR published_at >= %(start)s) "
        "AND (%(end)s IS NULL OR published_at <= %(end)s) "
        "ORDER BY published_at DESC LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM cb_statements "
        "WHERE central_bank = %(bank)s "
        "AND (%(type)s = 'any' OR type = %(type)s) "
        "AND (%(start)s IS NULL OR published_at >= %(start)s) "
        "AND (%(end)s IS NULL OR published_at <= %(end)s)"
    )
    params = {
        "bank": bank.value,
        "type": type.value,
        "start": start,
        "end": end,
        "limit": page.limit,
        "offset": page.offset,
    }
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, params)
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp), ttl=60)
    return resp
