-- Initial Meridian data hub schema

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    label TEXT,
    source TEXT,
    cadence TEXT,
    schema_version TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id SERIAL PRIMARY KEY,
    dataset_id INT REFERENCES datasets(dataset_id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    status TEXT,
    rows_ingested INT,
    error TEXT,
    meta JSONB
);

CREATE TABLE IF NOT EXISTS metrics_ts (
    series_id TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    metric TEXT,
    ts TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION,
    unit TEXT,
    source TEXT,
    attrs JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (series_id, ts)
);

CREATE TABLE IF NOT EXISTS prices_eod (
    symbol TEXT NOT NULL,
    ts DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,
    source TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (symbol, ts)
);

CREATE TABLE IF NOT EXISTS indices_eod (
    index_symbol TEXT NOT NULL,
    ts DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,
    source TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (index_symbol, ts)
);

CREATE TABLE IF NOT EXISTS commodities_ts (
    commodity_code TEXT NOT NULL,
    series_id TEXT,
    ts DATE NOT NULL,
    price DOUBLE PRECISION,
    unit TEXT,
    source TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (commodity_code, ts)
);

CREATE TABLE IF NOT EXISTS freight_indices (
    index_code TEXT NOT NULL,
    ts DATE NOT NULL,
    value DOUBLE PRECISION,
    source TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (index_code, ts)
);

CREATE TABLE IF NOT EXISTS trade_flows (
    reporter_iso2 CHAR(2) NOT NULL,
    partner_iso2 CHAR(2) NOT NULL,
    hs_code TEXT NOT NULL,
    flow TEXT NOT NULL,
    period DATE NOT NULL,
    value_usd NUMERIC,
    quantity NUMERIC,
    quantity_unit TEXT,
    source TEXT,
    meta JSONB,
    PRIMARY KEY (reporter_iso2, partner_iso2, hs_code, flow, period)
);

CREATE TABLE IF NOT EXISTS policy_events (
    event_id SERIAL PRIMARY KEY,
    jurisdiction TEXT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    title TEXT,
    summary TEXT,
    url TEXT,
    topics TEXT[],
    affected_countries TEXT[],
    affected_sectors TEXT[],
    affected_entities TEXT[],
    severity TEXT,
    raw JSONB,
    UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS cb_statements (
    statement_id SERIAL PRIMARY KEY,
    central_bank TEXT,
    published_at TIMESTAMPTZ,
    type TEXT,
    title TEXT,
    url TEXT,
    text_excerpt TEXT,
    hawkish_dovish_score NUMERIC,
    next_meeting_date DATE,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS geo_events (
    event_id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    ts TIMESTAMPTZ,
    event_type TEXT,
    country TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    actor1 TEXT,
    actor2 TEXT,
    actor_roles TEXT[],
    goldstein NUMERIC,
    people_impacted INT,
    importance NUMERIC,
    url TEXT,
    raw JSONB,
    UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS geo_mentions (
    mention_id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    event_source_id TEXT,
    url TEXT,
    published_at TIMESTAMPTZ,
    language TEXT,
    source_country TEXT,
    snippet TEXT,
    raw JSONB,
    UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS ais_raw (
    msg_id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ,
    mmsi BIGINT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    sog_kn DOUBLE PRECISION,
    cog_deg DOUBLE PRECISION,
    nav_status TEXT,
    msg_type INT,
    channel TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS vessels (
    mmsi BIGINT PRIMARY KEY,
    imo BIGINT,
    call_sign TEXT,
    name TEXT,
    ship_type_code TEXT,
    ship_type_group TEXT,
    length_m DOUBLE PRECISION,
    width_m DOUBLE PRECISION,
    draught_m DOUBLE PRECISION,
    last_seen_ts TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ref_ports (
    port_id SERIAL PRIMARY KEY,
    name TEXT,
    country_iso2 CHAR(2)
);

CREATE TABLE IF NOT EXISTS ref_chokepoints (
    chokepoint_id SERIAL PRIMARY KEY,
    name TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS logistics_events (
    event_id SERIAL PRIMARY KEY,
    event_type TEXT,
    ts TIMESTAMPTZ,
    mmsi BIGINT,
    port_id INT,
    chokepoint_id INT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    channel TEXT,
    attrs JSONB,
    dedupe_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS port_congestion_ts (
    port_id INT NOT NULL,
    vessel_class TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    queue_length INT,
    avg_wait_hours DOUBLE PRECISION,
    throughput_departures INT,
    congestion_index DOUBLE PRECISION,
    source TEXT,
    PRIMARY KEY (port_id, vessel_class, ts)
);

CREATE TABLE IF NOT EXISTS chokepoint_ts (
    chokepoint_id INT NOT NULL,
    vessel_class TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    active_transits INT,
    avg_transit_minutes DOUBLE PRECISION,
    transit_delay_index DOUBLE PRECISION,
    source TEXT,
    PRIMARY KEY (chokepoint_id, vessel_class, ts)
);

CREATE TABLE IF NOT EXISTS ref_company_tickers (
    cik TEXT PRIMARY KEY,
    ticker TEXT,
    title TEXT,
    exchange TEXT,
    lei TEXT,
    sector_code TEXT,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS filings_index (
    accession TEXT PRIMARY KEY,
    cik TEXT,
    form TEXT,
    filing_date DATE,
    period_end DATE,
    company_name TEXT,
    files JSONB,
    url_primary TEXT,
    raw_s3_uri TEXT,
    source TEXT,
    inserted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fundamentals_xbrl (
    fact_id BIGSERIAL PRIMARY KEY,
    cik TEXT,
    fact TEXT,
    unit TEXT,
    value TEXT,
    period_start DATE,
    period_end DATE,
    fy INT,
    fq TEXT,
    accn TEXT,
    frame TEXT,
    taxonomy TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS earnings_events (
    event_id SERIAL PRIMARY KEY,
    cik TEXT,
    ticker TEXT,
    filing_accession TEXT,
    filing_date DATE,
    period TEXT,
    headline TEXT,
    guidance_flag BOOLEAN,
    url TEXT,
    raw JSONB
);
