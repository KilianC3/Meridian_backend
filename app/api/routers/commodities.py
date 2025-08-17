from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi import Query

from app.api.schemas.common import Page
from app.core import cache, db


class CommodityCode(str, Enum):
    WTI = "WTI"
    BRENT = "BRENT"
    HENRY_HUB = "HENRY_HUB"
    DIESEL_US = "DIESEL_US"
    GASOLINE_US = "GASOLINE_US"
    JET_US = "JET_US"
    COPPER = "COPPER"
    ALUMINUM = "ALUMINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    WHEAT = "WHEAT"
    CORN = "CORN"
    SOY = "SOY"


router = APIRouter()


@router.get("/commodities", tags=["commodities"])
async def get_commodity_prices(
    code: CommodityCode = Query(...),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"commodities:{code.value}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT commodity_code, ts, price, unit, source "
        "FROM commodities_ts "
        "WHERE commodity_code = %(code)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM commodities_ts "
        "WHERE commodity_code = %(code)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "code": code.value,
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


@router.get("/freight/bdi", tags=["freight"])
async def get_bdi_index(
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"bdi:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT index_code, ts, value, source "
        "FROM freight_indices "
        "WHERE index_code = 'BDI' "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM freight_indices "
        "WHERE index_code = 'BDI' "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
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
