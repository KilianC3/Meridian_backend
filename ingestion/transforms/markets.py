from __future__ import annotations

from typing import Any, Iterable, Iterator

FRED_SERIES = {
    "DGS10": "us_10y_yield",
    "EFFR": "effr",
    "DEXUSEU": "usd_eur",
    "DEXJPUS": "usd_jpy",
    "DEXUSUK": "usd_gbp",
    "DEXCAUS": "usd_cad",
    "DEXCHUS": "usd_cny",
    "DEXMXUS": "usd_mxn",
    "DEXBZUS": "usd_brl",
    "DEXINUS": "usd_inr",
}


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Transform FRED rates and FX series into ``metrics_ts`` rows."""

    for rec in records:
        series = str(rec.get("series", ""))
        metric = FRED_SERIES.get(series)
        if not metric:
            continue
        yield {
            "series_id": metric,
            "entity_type": "macro",
            "entity_id": "macro",
            "metric": metric,
            "ts": rec.get("date"),
            "value": rec.get("value"),
            "unit": rec.get("unit"),
            "source": rec.get("source", "fred"),
            "attrs": None,
        }
