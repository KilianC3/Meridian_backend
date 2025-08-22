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

CREATE TABLE IF NOT EXISTS series (
    series_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT,
    frequency TEXT,
    geography TEXT,
    sector TEXT,
    transform TEXT,
    first_ts TIMESTAMPTZ,
    last_ts TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS observations (
    series_id TEXT NOT NULL REFERENCES series(series_id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION,
    PRIMARY KEY (series_id, ts)
);

CREATE TABLE IF NOT EXISTS factors (
    factor_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    series_id TEXT REFERENCES series(series_id),
    note TEXT,
    evidence_density DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS factor_edges (
    edge_id SERIAL PRIMARY KEY,
    src_factor INT NOT NULL REFERENCES factors(factor_id) ON DELETE CASCADE,
    dst_factor INT NOT NULL REFERENCES factors(factor_id) ON DELETE CASCADE,
    sign INT,
    lag_days INT,
    beta DOUBLE PRECISION,
    p_value DOUBLE PRECISION,
    transfer_entropy DOUBLE PRECISION,
    method TEXT,
    regime TEXT,
    confidence DOUBLE PRECISION,
    sample_start DATE,
    sample_end DATE,
    evidence_count INT,
    evidence_density DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS evidence_links (
    link_id SERIAL PRIMARY KEY,
    factor_id INT REFERENCES factors(factor_id) ON DELETE CASCADE,
    edge_id INT REFERENCES factor_edges(edge_id) ON DELETE CASCADE,
    mongo_doc_id TEXT NOT NULL,
    weight DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS news_mentions (
    mention_id SERIAL PRIMARY KEY,
    factor_id INT REFERENCES factors(factor_id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    url TEXT,
    title TEXT,
    published_at TIMESTAMPTZ,
    snippet TEXT,
    raw JSONB,
    UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS risk_metrics (
    entity_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value DOUBLE PRECISION,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (entity_id, metric)
);

CREATE TABLE IF NOT EXISTS risk_snapshots (
    factor_id INT NOT NULL REFERENCES factors(factor_id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL,
    node_vol DOUBLE PRECISION,
    node_shock_sigma DOUBLE PRECISION,
    impact_pct DOUBLE PRECISION,
    systemic_contrib DOUBLE PRECISION,
    PRIMARY KEY (factor_id, ts)
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

-- Seed reference data
INSERT INTO ref_ports (port_id, name, country_iso2) VALUES
    (1, 'Port of Shanghai', 'CN'),
    (2, 'Port of Singapore', 'SG')
ON CONFLICT DO NOTHING;

INSERT INTO ref_chokepoints (chokepoint_id, name, notes) VALUES
    (1, 'Suez Canal', NULL),
    (2, 'Panama Canal', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO ref_company_tickers (cik, ticker, title, exchange, lei, sector_code, updated_at) VALUES
    ('0000320193', 'AAPL', 'Apple Inc.', 'NASDAQ', NULL, NULL, NOW()),
    ('0000789019', 'MSFT', 'Microsoft Corp.', 'NASDAQ', NULL, NULL, NOW())
ON CONFLICT (cik) DO NOTHING;

-- Seed sample factor web
INSERT INTO factors (factor_id, name, series_id, note, evidence_density) VALUES
    (1, 'Oil Prices', NULL, NULL, 0.0),
    (2, 'Inflation', NULL, NULL, 0.0)
ON CONFLICT DO NOTHING;

INSERT INTO factor_edges (edge_id, src_factor, dst_factor, sign, lag_days, beta, confidence, evidence_count, evidence_density)
VALUES (1, 1, 2, 1, 30, 0.8, 1.0, 1, 0.0)
ON CONFLICT DO NOTHING;

INSERT INTO evidence_links (factor_id, edge_id, mongo_doc_id, weight)
VALUES (1, NULL, 'sample_doc', 1.0)
ON CONFLICT DO NOTHING;
