from __future__ import annotations

import json
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db


class TradeFlow(str, Enum):
    import_ = "import"
    export = "export"
    all = "all"


router = APIRouter(tags=["logistics"])


@router.get("/logistics/trade")
async def get_trade_flows(
    reporter: str = Query(..., min_length=2, max_length=2),
    partner: str | None = Query(None, min_length=2, max_length=5),
    hs: str | None = Query(None, min_length=2, max_length=6),
    flow: TradeFlow = TradeFlow.all,
    period_start: str | None = Query(None, min_length=6, max_length=6),
    period_end: str | None = Query(None, min_length=6, max_length=6),
    page: Page = Depends(),
):
    key = (
        f"trade:{reporter}:{partner}:{hs}:{flow.value}:{period_start}:{period_end}:"
        f"{page.limit}:{page.offset}"
    )
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT reporter_iso2, partner_iso2, hs_code, flow, period, value_usd, quantity, quantity_unit "
        "FROM trade_flows "
        "WHERE reporter_iso2 = %(reporter)s "
        "AND (%(partner)s IS NULL OR partner_iso2 = %(partner)s) "
        "AND (%(flow)s = 'all' OR flow = %(flow)s) "
        "AND (%(hs)s IS NULL OR hs_code LIKE %(hs_like)s) "
        "AND (%(ps)s IS NULL OR period >= %(ps)s) "
        "AND (%(pe)s IS NULL OR period <= %(pe)s) "
        "ORDER BY period LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = (
        "SELECT COUNT(*) as count FROM trade_flows "
        "WHERE reporter_iso2 = %(reporter)s "
        "AND (%(partner)s IS NULL OR partner_iso2 = %(partner)s) "
        "AND (%(flow)s = 'all' OR flow = %(flow)s) "
        "AND (%(hs)s IS NULL OR hs_code LIKE %(hs_like)s) "
        "AND (%(ps)s IS NULL OR period >= %(ps)s) "
        "AND (%(pe)s IS NULL OR period <= %(pe)s)"
    )
    params = {
        "reporter": reporter.upper(),
        "partner": partner.upper() if partner else None,
        "hs": hs,
        "hs_like": f"{hs}%" if hs else None,
        "flow": flow.value,
        "ps": period_start,
        "pe": period_end,
        "limit": page.limit,
        "offset": page.offset,
    }
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, params)
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp), ttl=30)
    return resp
