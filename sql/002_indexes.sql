CREATE INDEX IF NOT EXISTS ix_metrics_lookup ON metrics_ts(entity_id, metric, ts DESC);
CREATE INDEX IF NOT EXISTS ix_trade_period ON trade_flows(period);
CREATE INDEX IF NOT EXISTS ix_geo_ts ON geo_events(ts DESC);
CREATE INDEX IF NOT EXISTS ix_policy_ts ON policy_events(published_at DESC);
