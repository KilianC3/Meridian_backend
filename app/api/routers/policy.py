from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class Jurisdiction(str, Enum):
    US = "US"
    EU = "EU"
    UK = "UK"


class PolicySource(str, Enum):
    federal_register = "federal_register"
    eur_lex = "eur_lex"
    uk_legislation = "uk_legislation"
    ofac = "ofac"
    eu_sanctions = "eu_sanctions"
    uk_hmt = "uk_hmt"
    un_sanctions = "un_sanctions"
    bis_entity_list = "bis_entity_list"


router = APIRouter(tags=["policy"])


@router.get("/policy")
async def get_policy_events(
    jurisdiction: Jurisdiction = Query(...),
    source: PolicySource | None = None,
    q: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"policy:{jurisdiction.value}:"
        f"{source.value if source else None}:"
        f"{q}:{start}:{end}:{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT event_id, jurisdiction, source, published_at, title, summary, url, "
        "topics "
        "FROM policy_events "
        "WHERE jurisdiction = %(jurisdiction)s "
        "AND (%(source)s IS NULL OR source = %(source)s) "
        "AND (%(start)s IS NULL OR published_at >= %(start)s) "
        "AND (%(end)s IS NULL OR published_at <= %(end)s) "
        "AND (%(q)s IS NULL OR title ILIKE %(q_like)s OR summary ILIKE %(q_like)s) "
        "ORDER BY published_at DESC LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM policy_events "
        "WHERE jurisdiction = %(jurisdiction)s "
        "AND (%(source)s IS NULL OR source = %(source)s) "
        "AND (%(start)s IS NULL OR published_at >= %(start)s) "
        "AND (%(end)s IS NULL OR published_at <= %(end)s) "
        "AND (%(q)s IS NULL OR title ILIKE %(q_like)s OR summary ILIKE %(q_like)s)"
    )
    params = {
        "jurisdiction": jurisdiction.value,
        "source": source.value if source else None,
        "q": q,
        "q_like": f"%{q}%" if q else None,
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
