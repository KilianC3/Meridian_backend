from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db

router = APIRouter(tags=["assets"])


@router.get("/assets/prices")
async def get_asset_prices(
    symbol: str = Query(..., example="AAPL"),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"asset_prices:{symbol}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT symbol, ts, open, high, low, close, volume FROM prices_eod "
        "WHERE symbol = %(symbol)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM prices_eod WHERE symbol = %(symbol)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "symbol": symbol.upper(),
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


@router.get("/assets/indices")
async def get_index_prices(
    index_symbol: str = Query(..., example="SPX"),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"index_prices:{index_symbol}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT index_symbol, ts, value FROM indices_eod "
        "WHERE index_symbol = %(index_symbol)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM indices_eod WHERE index_symbol = %(index_symbol)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "index_symbol": index_symbol.upper(),
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


@router.get("/assets/fundamentals")
async def get_fundamentals(
    cik: str = Query(..., example="0000320193"),
    fact: str = Query(..., example="Assets"),
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = f"fundamentals:{cik}:{fact}:{start}:{end}:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT cik, fact, ts, value, unit FROM fundamentals_xbrl "
        "WHERE cik = %(cik)s AND fact = %(fact)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM fundamentals_xbrl "
        "WHERE cik = %(cik)s AND fact = %(fact)s "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "cik": cik,
        "fact": fact,
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


@router.get("/assets/earnings")
async def get_earnings_events(
    cik: str | None = Query(None, example="0000320193"),
    ticker: str | None = Query(None, example="AAPL"),
    q: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    page: Page = Depends(),
):
    key = (
        f"earnings:{cik}:{ticker}:{q}:{start}:{end}:{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT cik, ticker, ts, headline, url FROM earnings_events "
        "WHERE (%(cik)s IS NULL OR cik = %(cik)s) "
        "AND (%(ticker)s IS NULL OR ticker = %(ticker)s) "
        "AND (%(q)s IS NULL OR headline ILIKE %(q_like)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s) "
        "ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM earnings_events "
        "WHERE (%(cik)s IS NULL OR cik = %(cik)s) "
        "AND (%(ticker)s IS NULL OR ticker = %(ticker)s) "
        "AND (%(q)s IS NULL OR headline ILIKE %(q_like)s) "
        "AND (%(start)s IS NULL OR ts >= %(start)s) "
        "AND (%(end)s IS NULL OR ts <= %(end)s)"
    )
    params = {
        "cik": cik,
        "ticker": ticker.upper() if ticker else None,
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
    await cache.cache_set(key, json.dumps(resp), ttl=30)
    return resp
