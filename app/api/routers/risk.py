from __future__ import annotations

import json
from time import perf_counter
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.common import Page
from app.core import cache, db
from app.core.config import settings
from app.core.telemetry import RISK_COMPUTE_COUNT, RISK_COMPUTE_LATENCY
from risk_engine.cascade import propagate_shock

router = APIRouter(tags=["risk"])

_DEFAULT_METRICS = ["macro", "market", "commodity", "geo", "logistics"]


@router.get("/risk")
async def get_risk_score(
    country: str = Query(..., min_length=3, max_length=3),
) -> Dict[str, Any]:
    """Return simple aggregated risk scores for a given country.

    The endpoint queries a set of pre-computed risk metrics and returns their
    weighted average. If a metric is missing it is treated as ``0``.
    """
    start = perf_counter()
    key = f"risk:{country.upper()}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached

    sql = (
        "SELECT metric, value FROM risk_metrics "
        "WHERE entity_id = %(country)s AND metric = ANY(%(metrics)s)"
    )
    params = {"country": country.upper(), "metrics": _DEFAULT_METRICS}
    rows = await run_in_threadpool(db.fetch_all, sql, params)

    scores = {m: 0.0 for m in _DEFAULT_METRICS}
    for row in rows:
        metric = row.get("metric")
        value = row.get("value", 0.0)
        if metric in scores:
            scores[metric] = value

    risk = sum(scores.values()) / len(scores) if scores else 0.0
    resp = {"country": country.upper(), "scores": scores, "risk": risk}
    await cache.cache_set(key, json.dumps(resp))
    elapsed = perf_counter() - start
    RISK_COMPUTE_COUNT.inc()
    RISK_COMPUTE_LATENCY.observe(elapsed)
    return resp


@router.get("/factors")
async def list_factors(page: Page = Depends()) -> Dict[str, Any]:
    key = f"factors:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT factor_id, name, series_id, note, evidence_density FROM factors "
        "ORDER BY factor_id LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = "SELECT COUNT(*) as count FROM factors"
    params = {"limit": page.limit, "offset": page.offset}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, {})
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp))
    return resp


@router.get("/factors/{factor_id}")
async def get_factor(factor_id: int) -> Dict[str, Any] | None:
    key = f"factor:{factor_id}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT factor_id, name, series_id, note, evidence_density FROM factors "
        "WHERE factor_id = %(fid)s"
    )
    row = await run_in_threadpool(db.fetch_one, sql, {"fid": factor_id})
    await cache.cache_set(key, json.dumps(row))
    return row


@router.get("/edges")
async def list_edges(page: Page = Depends()) -> Dict[str, Any]:
    key = f"edges:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT edge_id, src_factor, dst_factor, sign, lag_days, beta, p_value, "
        "transfer_entropy, method, regime, confidence, sample_start, sample_end, "
        "evidence_count, evidence_density FROM factor_edges "
        "ORDER BY edge_id LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = "SELECT COUNT(*) as count FROM factor_edges"
    params = {"limit": page.limit, "offset": page.offset}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, {})
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp))
    return resp


@router.get("/risk_snapshots")
async def list_risk_snapshots(page: Page = Depends()) -> Dict[str, Any]:
    key = f"risk_snaps:{page.limit}:{page.offset}"
    cached = await cache.cache_get(key)
    if cached:
        if isinstance(cached, (bytes, str)):
            return json.loads(cached)
        return cached
    sql = (
        "SELECT factor_id, ts, node_vol, node_shock_sigma, impact_pct, "
        "systemic_contrib FROM risk_snapshots ORDER BY ts DESC "
        "LIMIT %(limit)s OFFSET %(offset)s"
    )
    count_sql = "SELECT COUNT(*) as count FROM risk_snapshots"
    params = {"limit": page.limit, "offset": page.offset}
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    count_row = await run_in_threadpool(db.fetch_one, count_sql, {})
    resp = {"data": rows, "count": count_row.get("count", 0) if count_row else 0}
    await cache.cache_set(key, json.dumps(resp))
    return resp


@router.get("/simulate_shock")
async def simulate_shock(
    factor_id: int,
    shock_size: float = settings.default_shock_sigma,
    horizon: int = 3,
) -> Dict[str, Any]:
    sql = "SELECT src_factor, dst_factor, beta, lag_days, confidence FROM factor_edges"
    edges = await run_in_threadpool(db.fetch_all, sql, {})
    impacts = propagate_shock(edges, factor_id, shock_size, horizon)
    return {"factor_id": factor_id, "impacts": impacts}
