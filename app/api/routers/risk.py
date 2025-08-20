from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import APIRouter, Query
from fastapi.concurrency import run_in_threadpool

from app.core import cache, db

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
    return resp
