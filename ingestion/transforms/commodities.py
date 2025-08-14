from __future__ import annotations

from typing import Any, Iterable, Iterator

COMMODITY_CODES = {
    "WTI": "WTI",
    "BRENT": "BRENT",
    "HENRY_HUB": "HENRY_HUB",
    "DIESEL_US": "DIESEL_US",
    "GASOLINE_US": "GASOLINE_US",
    "JET_US": "JET_US",
    "COPPER": "COPPER",
    "ALUMINUM": "ALUMINUM",
    "GOLD": "GOLD",
    "SILVER": "SILVER",
    "WHEAT": "WHEAT",
    "CORN": "CORN",
    "SOY": "SOY",
}


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map commodity records to ``commodities_ts`` or ``freight_indices``."""

    for rec in records:
        source = rec.get("source")
        if source == "bdi":
            yield {
                "index_code": "BDI",
                "ts": rec.get("date"),
                "value": rec.get("value"),
                "source": source,
            }
            continue

        commodity = COMMODITY_CODES.get(str(rec.get("commodity", "")))
        if not commodity:
            continue
        yield {
            "commodity_code": commodity,
            "series_id": commodity,
            "ts": rec.get("date"),
            "price": rec.get("value"),
            "unit": rec.get("unit"),
            "source": source,
        }
