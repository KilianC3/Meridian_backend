from __future__ import annotations

import json
from pathlib import Path

from ingestion.transforms import (
    commodities,
    geopolitics,
    logistics,
    macro,
    markets,
    policy,
)

TEST_DIR = Path(__file__).parent
GOLDEN = TEST_DIR / "golden"


def _load(name: str):
    with open(GOLDEN / f"{name}.json", "r", encoding="utf8") as f:
        return json.load(f)


def test_macro_transform():
    records = [
        {
            "source": "worldbank",
            "indicator": "NY.GDP.MKTP.CD",
            "country_iso3": "USA",
            "date": "2023",
            "value": 100,
        },
        {
            "source": "imf",
            "indicator": "NGDP_RPCH",
            "country_iso3": "USA",
            "date": "2023",
            "value": 1.5,
        },
    ]
    out = list(macro.transform(records))
    assert out == _load("macro")


def test_markets_transform():
    records = [
        {
            "source": "fred",
            "series": "DGS10",
            "date": "2024-01-02",
            "value": 4.0,
            "unit": "percent",
        },
        {
            "source": "fred",
            "series": "DEXUSEU",
            "date": "2024-01-02",
            "value": 1.1,
            "unit": "rate",
        },
    ]
    out = list(markets.transform(records))
    assert out == _load("markets")


def test_commodities_transform():
    records = [
        {
            "source": "eia",
            "commodity": "WTI",
            "date": "2024-01-01",
            "value": 80.0,
            "unit": "USD/bbl",
        },
        {
            "source": "fred",
            "commodity": "COPPER",
            "date": "2024-01-01",
            "value": 9000,
            "unit": "USD/ton",
        },
        {"source": "bdi", "date": "2024-01-01", "value": 1800},
    ]
    out = list(commodities.transform(records))
    assert out == _load("commodities")


def test_policy_transform():
    records = [
        {
            "source": "fed",
            "title": "FOMC Statement",
            "url": "http://fed.example/statement",
            "published_at": "2024-01-01T00:00:00Z",
            "summary": "Fed statement",
        },
        {
            "source": "federal_register",
            "id": "123",
            "title": "New Rule",
            "summary": "Summary",
            "published_at": "2024-01-02",
            "url": "http://fr.gov/123",
        },
    ]
    out = list(policy.transform(records))
    assert out == _load("policy")


def test_geopolitics_transform():
    records = [
        {
            "source": "gdelt_events",
            "GLOBALEVENTID": "1",
            "DATEADDED": "20240101",
            "EventType": "Protest",
            "ActionGeo_CountryCode": "US",
            "ActionGeo_Lat": 10.0,
            "ActionGeo_Long": 20.0,
            "Actor1Name": "Protesters",
            "Actor2Name": "Government",
            "Actor1Type1Code": "CVL",
            "Actor2Type1Code": "GOV",
            "GoldsteinScale": 1.0,
            "NumMentions": 2,
            "NumSources": 1,
            "NumArticles": 1,
        },
        {
            "source": "gdelt_mentions",
            "GLOBALEVENTID": "1",
            "MentionIdentifier": "abc",
            "MentionURL": "http://example.com",
            "MentionTimeDate": "20240101",
            "MentionDocLanguage": "en",
            "MentionDocCountryCode": "US",
            "MentionText": "snippet",
        },
        {
            "source": "reliefweb",
            "id": "rw1",
            "date": "2024-01-03",
            "type": "earthquake",
            "country": "US",
            "lat": 30.0,
            "lon": 40.0,
            "people_impacted": 100,
            "url": "http://reliefweb.int/1",
        },
    ]
    out = list(geopolitics.transform(records))
    assert out == _load("geopolitics")


def test_logistics_transform():
    records = [
        {
            "source": "un_comtrade",
            "reporter": "US",
            "partner": "CN",
            "hs_code": "0101",
            "flow": "import",
            "period": "202401",
            "value": 1000,
            "quantity": 10,
            "quantity_unit": "kg",
            "meta": {"foo": "bar"},
        },
        {
            "source": "gdelt_transport",
            "GLOBALEVENTID": "2",
            "DATEADDED": "20240102",
            "ActionGeo_Lat": 10.0,
            "ActionGeo_Long": 20.0,
        },
    ]
    out = list(logistics.transform(records))
    assert out == _load("logistics")


def test_ais_derivations():
    messages = [
        {
            "source": "ais",
            "mmsi": "1",
            "ts": "2024-01-01T00:00:00Z",
            "nav_status": "at_anchor",
            "port_id": "PORTA",
            "lat": 0,
            "lon": 0,
            "draught_m": 10,
        },
        {
            "source": "ais",
            "mmsi": "1",
            "ts": "2024-01-01T01:00:00Z",
            "nav_status": "moored",
            "port_id": "PORTA",
            "lat": 0,
            "lon": 0,
            "draught_m": 10,
        },
        {
            "source": "ais",
            "mmsi": "1",
            "ts": "2024-01-01T02:00:00Z",
            "nav_status": "under_way",
            "port_id": None,
            "lat": 0,
            "lon": 0,
            "draught_m": 12,
        },
        {
            "source": "ais",
            "mmsi": "2",
            "ts": "2024-01-01T03:00:00Z",
            "nav_status": "under_way",
            "chokepoint_id": "SUEZ",
            "lat": 1,
            "lon": 1,
        },
        {
            "source": "ais",
            "mmsi": "2",
            "ts": "2024-01-01T04:00:00Z",
            "nav_status": "under_way",
            "chokepoint_id": None,
            "lat": 1,
            "lon": 1,
        },
    ]
    out = list(logistics.transform(messages))
    assert out == _load("ais")
