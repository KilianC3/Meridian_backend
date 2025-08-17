from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class MacroMetric(str, Enum):
    gdp_current_usd = "gdp_current_usd"
    cpi_yoy_percent = "cpi_yoy_percent"
    unemployment_percent = "unemployment_percent"
    policy_rate_percent = "policy_rate_percent"
    real_gdp_growth_percent = "real_gdp_growth_percent"
    gov_debt_gdp_percent = "gov_debt_gdp_percent"
    cpi_index = "cpi_index"
    fx_reserves_usd = "fx_reserves_usd"
    current_account_gdp_percent = "current_account_gdp_percent"


router = APIRouter(tags=["macro"])


@router.get("/macro")
async def get_macro_series(
    country: str = Query(..., min_length=3, max_length=3),
    metric: MacroMetric = Query(...),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"macro:{country}:{metric.value}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT series_id, entity_id, metric, ts, value, unit, source "
        "FROM metrics_ts "
        "WHERE entity_id = %(country)s AND metric = %(metric)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM metrics_ts "
        "WHERE entity_id = %(country)s AND metric = %(metric)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "country": country.upper(),
        "metric": metric.value,
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
