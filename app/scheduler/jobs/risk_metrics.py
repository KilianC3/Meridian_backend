"""Scheduled job to recompute aggregated risk metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

import pandas as pd
from fastapi.concurrency import run_in_threadpool

from app.core import db
from app.core.config import settings
from risk_engine.volatility import ewma_volatility


async def run() -> None:
    """Recompute risk snapshots and aggregate risk metrics.

    The job iterates over factors linked to time series, computes EWMA
    volatility for each series, stores it in ``risk_snapshots``, and then
    aggregates the latest volatilities into a global ``risk_metrics`` record.
    """
    factors: Sequence[dict[str, Any]] = await run_in_threadpool(
        db.fetch_all,
        "SELECT factor_id, series_id FROM factors WHERE series_id IS NOT NULL",
    )
    now = datetime.utcnow()
    for row in factors:
        obs: Sequence[dict[str, Any]] = await run_in_threadpool(
            db.fetch_all,
            "SELECT ts, value FROM observations WHERE series_id = %(sid)s ORDER BY ts",
            {"sid": row["series_id"]},
        )
        if not obs:
            continue
        series = pd.Series([o["value"] for o in obs], index=[o["ts"] for o in obs])
        vol = ewma_volatility(series, span=settings.risk_window_days)
        params = {
            "factor_id": row["factor_id"],
            "ts": now,
            "node_vol": vol,
            "node_shock_sigma": vol,
        }
        await run_in_threadpool(
            db.fetch_one,
            """
            INSERT INTO risk_snapshots (
                factor_id, ts, node_vol, node_shock_sigma, impact_pct, systemic_contrib
            )
            VALUES (%(factor_id)s, %(ts)s, %(node_vol)s, %(node_shock_sigma)s, 0, 0)
            ON CONFLICT (factor_id, ts) DO UPDATE
            SET node_vol = EXCLUDED.node_vol,
                node_shock_sigma = EXCLUDED.node_shock_sigma
            RETURNING factor_id
            """,
            params,
        )

    vols: Sequence[dict[str, Any]] = await run_in_threadpool(
        db.fetch_all,
        """
        SELECT node_vol FROM risk_snapshots
        WHERE ts = (SELECT MAX(ts) FROM risk_snapshots)
        """,
    )
    if vols:
        avg_vol = sum(v["node_vol"] for v in vols if v.get("node_vol")) / len(vols)
        await run_in_threadpool(
            db.fetch_one,
            """
            INSERT INTO risk_metrics (entity_id, metric, value, updated_at)
            VALUES ('GLOBAL', 'macro', %(val)s, %(ts)s)
            ON CONFLICT (entity_id, metric) DO UPDATE
            SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at
            RETURNING entity_id
            """,
            {"val": avg_vol, "ts": now},
        )
