from __future__ import annotations

from typing import Any, Iterable, Iterator

WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.CD": ("gdp_current_usd", "USD"),
    "FP.CPI.TOTL.ZG": ("cpi_yoy_percent", "percent"),
    "SL.UEM.TOTL.ZS": ("unemployment_percent", "percent"),
    "FR.INR.RINR": ("policy_rate_percent", "percent"),
}

IMF_INDICATORS = {
    "NGDP_RPCH": ("real_gdp_growth_percent", "percent"),
    "GGXWDG_NGDP": ("gov_debt_gdp_percent", "percent"),
    "PCPI_IX": ("cpi_index", "index"),
    "TXGOFXD_USD": ("fx_reserves_usd", "USD"),
    "BCA_NGDPD": ("current_account_gdp_percent", "percent"),
}


def _parse_ts(val: str) -> str:
    """Return ISO date from a YYYY or YYYY-MM-DD string."""
    if len(val) == 4:
        return f"{val}-01-01"
    return val


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Transform macroeconomic records into ``metrics_ts`` rows."""

    for rec in records:
        source = rec.get("source")
        indicator = str(rec.get("indicator", ""))
        country = rec.get("country_iso3") or rec.get("country")
        date = rec.get("date")
        value = rec.get("value")

        mapping: tuple[str, str] | None = None
        if source == "worldbank":
            mapping = WORLD_BANK_INDICATORS.get(indicator)
        elif source == "imf":
            mapping = IMF_INDICATORS.get(indicator)

        if not mapping or not country or date is None:
            continue

        metric, unit = mapping
        yield {
            "series_id": f"{country}_{metric}",
            "entity_type": "country",
            "entity_id": country,
            "metric": metric,
            "ts": _parse_ts(str(date)),
            "value": value,
            "unit": unit,
            "source": source,
            "attrs": None,
        }
