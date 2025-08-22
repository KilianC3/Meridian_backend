CREATE INDEX IF NOT EXISTS ix_metrics_lookup ON metrics_ts(entity_id, metric, ts DESC);
CREATE INDEX IF NOT EXISTS ix_trade_period ON trade_flows(period);
CREATE INDEX IF NOT EXISTS ix_geo_ts ON geo_events(ts DESC);
CREATE INDEX IF NOT EXISTS ix_policy_ts ON policy_events(published_at DESC);
CREATE INDEX IF NOT EXISTS ix_observations_lookup ON observations(series_id, ts DESC);
CREATE INDEX IF NOT EXISTS ix_factor_edges_src_dst ON factor_edges(src_factor, dst_factor);
CREATE INDEX IF NOT EXISTS ix_risk_metrics_entity ON risk_metrics(entity_id);
CREATE INDEX IF NOT EXISTS ix_news_mentions_factor_ts ON news_mentions(factor_id, published_at DESC);
