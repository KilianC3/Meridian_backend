from __future__ import annotations

import os

import psycopg2
import pytest

from ingestion.metrics.news import update_density


def _get_conn():
    dsn = os.getenv(
        "POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    try:
        return psycopg2.connect(dsn)
    except Exception as exc:  # pragma: no cover - skip if DB not available
        pytest.skip(f"Postgres unavailable: {exc}")


def test_update_density() -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS news_mentions, factors")
    cur.execute(
        """
        CREATE TABLE factors (
            factor_id INT PRIMARY KEY,
            name TEXT,
            evidence_density DOUBLE PRECISION
        );
        CREATE TABLE news_mentions (
            mention_id SERIAL PRIMARY KEY,
            factor_id INT,
            published_at TIMESTAMPTZ
        );
        """
    )
    cur.execute("INSERT INTO factors (factor_id, name) VALUES (1, 'F1')")
    cur.execute("INSERT INTO news_mentions (factor_id, published_at) VALUES (1, NOW())")
    conn.commit()
    update_density(conn)
    cur.execute("SELECT evidence_density FROM factors WHERE factor_id=1")
    assert cur.fetchone()[0] == 1
    conn.close()
