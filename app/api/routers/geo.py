from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class GeoSource(str, Enum):
    gdelt_events = "gdelt_events"
    reliefweb = "reliefweb"
    any = "any"


router = APIRouter(tags=["geo"])


@router.get("/geo/events")
async def get_geo_events(
    source: GeoSource = GeoSource.any,
    country: str | None = Query(None, min_length=2, max_length=2),
    event_type: str | None = None,
    goldstein_min: float | None = None,
    goldstein_max: float | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"geo_events:{source.value}:{country}:{event_type}:{goldstein_min}:{goldstein_max}:"
        f"{start}:{end}:{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT source, source_id, ts, event_type, country, lat, lon, actor1, actor2, "
        "actor_roles, goldstein, people_impacted, importance, url "
        "FROM geo_events "
        "WHERE (%(source)s = 'any' OR source = %(source)s) "
        "AND (%(country)s IS NULL OR country = %(country)s) "
        "AND (%(event_type)s IS NULL OR event_type = %(event_type)s) "
        "AND (%(goldstein_min)s IS NULL OR goldstein >= %(goldstein_min)s) "
        "AND (%(goldstein_max)s IS NULL OR goldstein <= %(goldstein_max)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM geo_events "
        "WHERE (%(source)s = 'any' OR source = %(source)s) "
        "AND (%(country)s IS NULL OR country = %(country)s) "
        "AND (%(event_type)s IS NULL OR event_type = %(event_type)s) "
        "AND (%(goldstein_min)s IS NULL OR goldstein >= %(goldstein_min)s) "
        "AND (%(goldstein_max)s IS NULL OR goldstein <= %(goldstein_max)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "source": source.value,
        "country": country.upper() if country else None,
        "event_type": event_type,
        "goldstein_min": goldstein_min,
        "goldstein_max": goldstein_max,
        "start": start,
        "end": end,
        "limit": page.limit,
        "offset": page.offset,
    }
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, params)
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp), ttl=15)
    return resp


@router.get("/geo/mentions")
async def get_geo_mentions(
    event_source_id: str | None = None,
    lang: str | None = Query(None, min_length=2, max_length=2),
    source_country: str | None = Query(None, min_length=2, max_length=2),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"geo_mentions:{event_source_id}:{lang}:{source_country}:{start}:{end}:"
        f"{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT event_source_id, ts, lang, source_country, snippet, url "
        "FROM geo_mentions "
        "WHERE (%(event_source_id)s IS NULL OR event_source_id = %(event_source_id)s) "
        "AND (%(lang)s IS NULL OR lang = %(lang)s) "
        "AND (%(source_country)s IS NULL OR source_country = %(source_country)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM geo_mentions "
        "WHERE (%(event_source_id)s IS NULL OR event_source_id = %(event_source_id)s) "
        "AND (%(lang)s IS NULL OR lang = %(lang)s) "
        "AND (%(source_country)s IS NULL OR source_country = %(source_country)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "event_source_id": event_source_id,
        "lang": lang.lower() if lang else None,
        "source_country": source_country.upper() if source_country else None,
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
