from __future__ import annotations

import os

import psycopg2
import pytest

from ingestion.loaders.postgres import bulk_upsert


def _get_conn() -> psycopg2.extensions.connection:
    dsn = os.getenv(
        "POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    try:
        return psycopg2.connect(dsn)
    except Exception as exc:
        pytest.skip(f"Postgres unavailable: {exc}")


def test_bulk_upsert_idempotent() -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS upsert_test")
    cur.execute("CREATE TABLE upsert_test (id INT PRIMARY KEY, val TEXT)")
    conn.commit()

    rows = [{"id": 1, "val": "a"}]
    bulk_upsert(conn, "upsert_test", rows, ["id"])
    bulk_upsert(conn, "upsert_test", [{"id": 1, "val": "b"}], ["id"])

    cur.execute("SELECT val FROM upsert_test WHERE id=1")
    result = cur.fetchone()
    assert result and result[0] == "b"
    conn.close()
