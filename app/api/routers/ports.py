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


@router.get("/logistics/ports/series")
async def get_port_series(
    port_id: str,
    vessel_class: VesselClass = VesselClass.all,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"port_series:{port_id}:{vessel_class.value}:{start}:{end}:"
        f"{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT port_id, vessel_class, ts, congestion, waiting_time, "
        "arrivals, departures "
        "FROM port_congestion_ts "
        "WHERE port_id = %(port_id)s "
        "AND (%(vessel_class)s = 'all' OR vessel_class = %(vessel_class)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM port_congestion_ts "
        "WHERE port_id = %(port_id)s "
        "AND (%(vessel_class)s = 'all' OR vessel_class = %(vessel_class)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "port_id": port_id,
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


@router.get("/logistics/ports/snapshot")
async def get_port_snapshot(port_id: str, vessel_class: VesselClass = VesselClass.all):
    key = f"port_snapshot:{port_id}:{vessel_class.value}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    if vessel_class == VesselClass.all:
        sql = (
            "SELECT DISTINCT ON (vessel_class) port_id, vessel_class, ts, "
            "congestion, waiting_time, arrivals, departures "
            "FROM port_congestion_ts WHERE port_id = %(port_id)s "
            "ORDER BY vessel_class, ts DESC"
        )
        params = {"port_id": port_id}
    else:
        sql = (
            "SELECT port_id, vessel_class, ts, congestion, waiting_time, "
            "arrivals, departures "
            "FROM port_congestion_ts WHERE port_id = %(port_id)s "
            "AND vessel_class = %(vessel_class)s "
            "ORDER BY ts DESC LIMIT 1"
        )
        params = {"port_id": port_id, "vessel_class": vessel_class.value}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    resp = {"data": rows}
    await cache.cache_set(key, json.dumps(resp), ttl=15)
    return resp


@router.get("/logistics/ports/ref")
async def get_port_ref(port_id: str | None = None):
    sql = (
        "SELECT port_id, name, country FROM ref_ports "
        "WHERE (%(port_id)s IS NULL OR port_id = %(port_id)s)"
    )
    params = {"port_id": port_id}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    return {"data": rows}
