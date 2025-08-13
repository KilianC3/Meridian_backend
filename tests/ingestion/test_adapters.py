from __future__ import annotations

import os

import psycopg2

from ingestion.adapters.aisstream import AISStreamAdapter
from ingestion.adapters.bdi_scraper import BDIScraperAdapter
from ingestion.adapters.cboe_vix import CBOEVixAdapter
from ingestion.adapters.comtrade import ComtradeAdapter
from ingestion.adapters.ecb_rss import ECBRSSAdapter
from ingestion.adapters.eia import EIAAdapter
from ingestion.adapters.federal_register import FederalRegisterAdapter
from ingestion.adapters.fred import FREDAdapter
from ingestion.adapters.gdelt_events import GDELTEventsAdapter
from ingestion.adapters.gdelt_mentions import GDELTMentionsAdapter
from ingestion.adapters.reliefweb import ReliefWebAdapter
from ingestion.adapters.sec import SECAdapter
from ingestion.adapters.worldbank import WorldBankAdapter
from ingestion.adapters.yfinance import YFinanceAdapter
from ingestion.loaders.postgres import bulk_upsert


def _get_conn() -> psycopg2.extensions.connection:
    dsn = os.getenv(
        "POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    return psycopg2.connect(dsn)


def _setup_tables(conn: psycopg2.extensions.connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS
            metrics_ts,
            commodities_ts,
            policy_events,
            cb_statements,
            geo_events,
            geo_mentions,
            trade_flows,
            freight_indices,
            indices_eod,
            prices_eod,
            ref_company_tickers,
            ais_raw,
            vessels,
            logistics_events,
            port_congestion_ts,
            chokepoint_ts,
            ingestion_runs
        """
    )
    cur.execute(
        """
        CREATE TABLE ingestion_runs (
            run_id SERIAL PRIMARY KEY,
            dataset_id INT,
            started_at TIMESTAMPTZ,
            ended_at TIMESTAMPTZ,
            status TEXT,
            rows_ingested INT,
            error TEXT,
            meta JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE metrics_ts (
            series_id TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            metric TEXT,
            ts TIMESTAMPTZ NOT NULL,
            value DOUBLE PRECISION,
            unit TEXT,
            source TEXT,
            attrs JSONB,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (series_id, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE commodities_ts (
            commodity_code TEXT NOT NULL,
            series_id TEXT,
            ts DATE NOT NULL,
            price DOUBLE PRECISION,
            unit TEXT,
            source TEXT,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (commodity_code, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE policy_events (
            event_id TEXT PRIMARY KEY,
            jurisdiction TEXT,
            source TEXT,
            source_id TEXT,
            published_at TIMESTAMPTZ,
            title TEXT,
            summary TEXT,
            url TEXT,
            topics TEXT,
            affected_countries TEXT,
            affected_sectors TEXT,
            affected_entities TEXT,
            severity TEXT,
            raw JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE cb_statements (
            statement_id TEXT PRIMARY KEY,
            central_bank TEXT,
            published_at TIMESTAMPTZ,
            type TEXT,
            title TEXT,
            url TEXT,
            text_excerpt TEXT,
            hawkish_dovish_score DOUBLE PRECISION,
            next_meeting_date DATE,
            raw JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE geo_events (
            event_id TEXT PRIMARY KEY,
            source TEXT,
            source_id TEXT,
            ts TIMESTAMPTZ,
            event_type TEXT,
            country TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            actor1 TEXT,
            actor2 TEXT,
            actor_roles TEXT,
            goldstein DOUBLE PRECISION,
            people_impacted INT,
            importance DOUBLE PRECISION,
            url TEXT,
            raw JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE geo_mentions (
            mention_id TEXT PRIMARY KEY,
            source TEXT,
            source_id TEXT,
            event_source_id TEXT,
            url TEXT,
            published_at TIMESTAMPTZ,
            language TEXT,
            source_country TEXT,
            snippet TEXT,
            raw JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE trade_flows (
            reporter_iso2 TEXT,
            partner_iso2 TEXT,
            hs_code TEXT,
            flow TEXT,
            period DATE,
            value_usd DOUBLE PRECISION,
            quantity DOUBLE PRECISION,
            quantity_unit TEXT,
            source TEXT,
            meta JSONB,
            PRIMARY KEY (reporter_iso2, partner_iso2, hs_code, flow, period)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE freight_indices (
            index_code TEXT,
            ts DATE,
            value DOUBLE PRECISION,
            source TEXT,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (index_code, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE prices_eod (
            symbol TEXT,
            ts DATE,
            open DOUBLE PRECISION,
            high DOUBLE PRECISION,
            low DOUBLE PRECISION,
            close DOUBLE PRECISION,
            adj_close DOUBLE PRECISION,
            volume DOUBLE PRECISION,
            source TEXT,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (symbol, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE indices_eod (
            index_symbol TEXT,
            ts DATE,
            open DOUBLE PRECISION,
            high DOUBLE PRECISION,
            low DOUBLE PRECISION,
            close DOUBLE PRECISION,
            adj_close DOUBLE PRECISION,
            volume DOUBLE PRECISION,
            source TEXT,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (index_symbol, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE ref_company_tickers (
            cik TEXT PRIMARY KEY,
            ticker TEXT,
            title TEXT,
            exchange TEXT,
            lei TEXT,
            sector_code TEXT,
            updated_at TIMESTAMPTZ
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE ais_raw (
            msg_id TEXT PRIMARY KEY,
            ts TIMESTAMPTZ,
            mmsi TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            sog_kn DOUBLE PRECISION,
            cog_deg DOUBLE PRECISION,
            nav_status TEXT,
            msg_type TEXT,
            channel TEXT,
            payload JSONB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE vessels (
            mmsi TEXT PRIMARY KEY,
            imo TEXT,
            call_sign TEXT,
            name TEXT,
            ship_type_code TEXT,
            ship_type_group TEXT,
            length_m DOUBLE PRECISION,
            width_m DOUBLE PRECISION,
            draught_m DOUBLE PRECISION,
            last_seen_ts TIMESTAMPTZ
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE logistics_events (
            event_type TEXT,
            ts TIMESTAMPTZ,
            mmsi TEXT,
            port_id TEXT,
            chokepoint_id TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            channel TEXT,
            attrs JSONB,
            dedupe_key TEXT PRIMARY KEY
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE port_congestion_ts (
            port_id TEXT,
            vessel_class TEXT,
            ts TIMESTAMPTZ,
            queue_length INT,
            avg_wait_hours DOUBLE PRECISION,
            throughput_departures DOUBLE PRECISION,
            congestion_index DOUBLE PRECISION,
            source TEXT,
            PRIMARY KEY (port_id, vessel_class, ts)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE chokepoint_ts (
            chokepoint_id TEXT,
            vessel_class TEXT,
            ts TIMESTAMPTZ,
            active_transits INT,
            avg_transit_minutes DOUBLE PRECISION,
            transit_delay_index DOUBLE PRECISION,
            source TEXT,
            PRIMARY KEY (chokepoint_id, vessel_class, ts)
        )
        """
    )
    conn.commit()


def test_worldbank_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    records = [
        {
            "source": "worldbank",
            "indicator": "NY.GDP.MKTP.CD",
            "country_iso3": "USA",
            "date": "2023",
            "value": 100,
        }
    ]
    adapter = WorldBankAdapter(records)
    adapter.run(conn, bulk_upsert, "metrics_ts", ["series_id", "ts"])
    adapter.run(conn, bulk_upsert, "metrics_ts", ["series_id", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM metrics_ts")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_fred_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    records = [
        {
            "source": "fred",
            "series": "DGS10",
            "date": "2024-01-02",
            "value": 4.0,
            "unit": "percent",
        }
    ]
    adapter = FREDAdapter(records)
    adapter.run(conn, bulk_upsert, "metrics_ts", ["series_id", "ts"])
    adapter.run(conn, bulk_upsert, "metrics_ts", ["series_id", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM metrics_ts")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_eia_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    records = [
        {
            "source": "eia",
            "commodity": "WTI",
            "date": "2024-01-01",
            "value": 80.0,
            "unit": "USD/bbl",
        }
    ]
    adapter = EIAAdapter(records)
    adapter.run(conn, bulk_upsert, "commodities_ts", ["commodity_code", "ts"])
    adapter.run(conn, bulk_upsert, "commodities_ts", ["commodity_code", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM commodities_ts")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_federal_register_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    records = [
        {
            "source": "federal_register",
            "id": "1",
            "title": "Rule",
            "summary": "",
            "published_at": "2024-01-01",
            "url": "http://fr/1",
        }
    ]
    adapter = FederalRegisterAdapter(records)
    adapter.run(conn, bulk_upsert, "policy_events", ["event_id"])
    adapter.run(conn, bulk_upsert, "policy_events", ["event_id"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM policy_events")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_cb_rss_adapters_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    records = [
        {
            "source": "ecb",
            "title": "Statement",
            "url": "http://ecb/1",
            "published_at": "2024-01-01T00:00:00Z",
            "summary": "",
        }
    ]
    adapter = ECBRSSAdapter(records)
    adapter.run(conn, bulk_upsert, "cb_statements", ["statement_id"])
    adapter.run(conn, bulk_upsert, "cb_statements", ["statement_id"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cb_statements")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_gdelt_adapters_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    events = [
        {
            "source": "gdelt_events",
            "GLOBALEVENTID": "1",
            "DATEADDED": "20240101",
            "EventType": "Protest",
            "ActionGeo_CountryCode": "US",
            "ActionGeo_Lat": 0,
            "ActionGeo_Long": 0,
            "Actor1Name": "A",
            "Actor2Name": "B",
            "Actor1Type1Code": "CVL",
            "Actor2Type1Code": "GOV",
            "GoldsteinScale": 1.0,
            "NumMentions": 1,
            "NumSources": 1,
            "NumArticles": 1,
        }
    ]
    adapter = GDELTEventsAdapter(events)
    adapter.run(conn, bulk_upsert, "geo_events", ["event_id"])
    adapter.run(conn, bulk_upsert, "geo_events", ["event_id"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM geo_events")
    assert cur.fetchone()[0] == 1
    mentions = [
        {
            "source": "gdelt_mentions",
            "GLOBALEVENTID": "1",
            "MentionIdentifier": "x",
            "MentionURL": "http://a",
            "MentionTimeDate": "20240101",
            "MentionDocLanguage": "en",
            "MentionDocCountryCode": "US",
            "MentionText": "t",
        }
    ]
    adapter2 = GDELTMentionsAdapter(mentions)
    adapter2.run(conn, bulk_upsert, "geo_mentions", ["mention_id"])
    adapter2.run(conn, bulk_upsert, "geo_mentions", ["mention_id"])
    cur.execute("SELECT COUNT(*) FROM geo_mentions")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_reliefweb_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [
        {
            "source": "reliefweb",
            "id": "r1",
            "date": "2024-01-01",
            "type": "flood",
            "country": "US",
            "lat": 0,
            "lon": 0,
            "url": "http://rw",
        }
    ]
    adapter = ReliefWebAdapter(recs)
    adapter.run(conn, bulk_upsert, "geo_events", ["event_id"])
    adapter.run(conn, bulk_upsert, "geo_events", ["event_id"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM geo_events")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_comtrade_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [
        {
            "source": "un_comtrade",
            "reporter": "US",
            "partner": "CN",
            "hs_code": "01",
            "flow": "import",
            "period": "202401",
            "value": 1,
            "quantity": 1,
            "quantity_unit": "kg",
        }
    ]
    adapter = ComtradeAdapter(recs)
    adapter.run(
        conn,
        bulk_upsert,
        "trade_flows",
        ["reporter_iso2", "partner_iso2", "hs_code", "flow", "period"],
    )
    adapter.run(
        conn,
        bulk_upsert,
        "trade_flows",
        ["reporter_iso2", "partner_iso2", "hs_code", "flow", "period"],
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM trade_flows")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_bdi_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [{"source": "bdi", "date": "2024-01-01", "value": 1000}]
    adapter = BDIScraperAdapter(recs)
    adapter.run(conn, bulk_upsert, "freight_indices", ["index_code", "ts"])
    adapter.run(conn, bulk_upsert, "freight_indices", ["index_code", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM freight_indices")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_sec_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [("ref_company_tickers", {"cik": "1", "ticker": "AAA"})]
    adapter = SECAdapter(recs)
    adapter.run(conn, bulk_upsert, "ref_company_tickers", ["cik"])
    adapter.run(conn, bulk_upsert, "ref_company_tickers", ["cik"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ref_company_tickers")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_yfinance_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [
        {
            "symbol": "AAPL",
            "ts": "2024-01-01",
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "adj_close": 1,
            "volume": 1,
            "source": "yfinance",
        }
    ]
    adapter = YFinanceAdapter(recs)
    adapter.run(conn, bulk_upsert, "prices_eod", ["symbol", "ts"])
    adapter.run(conn, bulk_upsert, "prices_eod", ["symbol", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM prices_eod")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_cboe_vix_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    recs = [
        {
            "index_symbol": "VIX",
            "ts": "2024-01-01",
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "adj_close": 1,
            "volume": 1,
            "source": "cboe",
        }
    ]
    adapter = CBOEVixAdapter(recs)
    adapter.run(conn, bulk_upsert, "indices_eod", ["index_symbol", "ts"])
    adapter.run(conn, bulk_upsert, "indices_eod", ["index_symbol", "ts"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM indices_eod")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_ais_adapter_idempotent() -> None:
    conn = _get_conn()
    _setup_tables(conn)
    msgs = [
        {
            "msg_id": "m1",
            "ts": "2024-01-01T00:00:00Z",
            "mmsi": "1",
            "lat": 0,
            "lon": 0,
            "nav_status": "at_anchor",
            "msg_type": "PositionReport",
        }
    ]
    adapter = AISStreamAdapter(msgs)
    adapter.run(conn, bulk_upsert, "ais_raw", ["msg_id"])
    adapter.run(conn, bulk_upsert, "ais_raw", ["msg_id"])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ais_raw")
    assert cur.fetchone()[0] == 1
    conn.close()
