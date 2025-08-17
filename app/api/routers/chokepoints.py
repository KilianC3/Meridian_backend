from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class VesselClass(str, Enum):
    container = "container"
    tanker = "tanker"
    bulk = "bulk"
    all = "all"


router = APIRouter(tags=["logistics"])


@router.get("/logistics/chokepoints/series")
async def get_chokepoint_series(
    chokepoint_id: str,
    vessel_class: VesselClass = VesselClass.all,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"chokepoint_series:{chokepoint_id}:{vessel_class.value}:{start}:{end}:{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT chokepoint_id, vessel_class, ts, delay_hours "
        "FROM chokepoint_delay_ts "
        "WHERE chokepoint_id = %(chokepoint_id)s "
        "AND (%(vessel_class)s = 'all' OR vessel_class = %(vessel_class)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM chokepoint_delay_ts "
        "WHERE chokepoint_id = %(chokepoint_id)s "
        "AND (%(vessel_class)s = 'all' OR vessel_class = %(vessel_class)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "chokepoint_id": chokepoint_id,
        "vessel_class": vessel_class.value,
        "start": start,
        "end": end,
        "limit": page.limit,
        "offset": page.offset,
    }
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, params)
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp), ttl=30)
    return resp


@router.get("/logistics/chokepoints/snapshot")
async def get_chokepoint_snapshot(
    chokepoint_id: str, vessel_class: VesselClass = VesselClass.all
):
    key = f"chokepoint_snapshot:{chokepoint_id}:{vessel_class.value}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    if vessel_class == VesselClass.all:
        sql = (
            "SELECT DISTINCT ON (vessel_class) chokepoint_id, vessel_class, ts, delay_hours "
            "FROM chokepoint_delay_ts WHERE chokepoint_id = %(chokepoint_id)s "
            "ORDER BY vessel_class, ts DESC"
        )
        params = {"chokepoint_id": chokepoint_id}
    else:
        sql = (
            "SELECT chokepoint_id, vessel_class, ts, delay_hours "
            "FROM chokepoint_delay_ts WHERE chokepoint_id = %(chokepoint_id)s AND vessel_class = %(vessel_class)s "
            "ORDER BY ts DESC LIMIT 1"
        )
        params = {"chokepoint_id": chokepoint_id, "vessel_class": vessel_class.value}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    resp = {"data": rows}
    await cache.cache_set(key, json.dumps(resp), ttl=15)
    return resp


@router.get("/logistics/chokepoints/ref")
async def get_chokepoint_ref(chokepoint_id: str | None = None):
    sql = (
        "SELECT chokepoint_id, name, country FROM ref_chokepoints "
        "WHERE (%(chokepoint_id)s IS NULL OR chokepoint_id = %(chokepoint_id)s)"
    )
    params = {"chokepoint_id": chokepoint_id}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    return {"data": rows}
