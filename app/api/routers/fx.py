from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class FXPair(str, Enum):
    usd_eur = "usd_eur"
    usd_jpy = "usd_jpy"
    usd_gbp = "usd_gbp"
    usd_cad = "usd_cad"
    usd_cny = "usd_cny"
    usd_mxn = "usd_mxn"
    usd_brl = "usd_brl"
    usd_inr = "usd_inr"


router = APIRouter(tags=["fx"])


@router.get("/fx")
async def get_fx_series(
    pair: FXPair,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    metric = pair.value
    key = f"fx:{metric}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT series_id, entity_id, metric, ts, value, unit, source "
        "FROM metrics_ts "
        "WHERE entity_id = 'US' AND metric = %(metric)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM metrics_ts "
        "WHERE entity_id = 'US' AND metric = %(metric)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "metric": metric,
        "start": start,
        "end": end,
        "limit": page.limit,
        "offset": page.offset,
    }
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, params)
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp))
    return resp
