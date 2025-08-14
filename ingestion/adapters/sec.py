"""Adapter for SEC EDGAR data."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Tuple

from .base import BaseAdapter


class SECAdapter(BaseAdapter):
    """Simple adapter handling multiple SEC tables."""

    name = "sec"

    def __init__(self, records: Iterable[Tuple[str, Dict[str, Any]]]):
        """Records are tuples of (table_name, row)."""

        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[Tuple[str, Dict[str, Any]]]:
        yield from self.records

    def transform(self, item: Tuple[str, Dict[str, Any]]) -> List[dict[str, Any]]:
        table, row = item
        new_row = row.copy()
        new_row["_table"] = table
        return [new_row]

    def run(
        self,
        conn: Any,
        upsert_fn,
        target_table: str,
        conflict_keys: List[str],
        cursor: Any | None = None,
    ) -> None:  # pragma: no cover - thin wrapper around BaseAdapter logic
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingestion_runs (dataset_id, started_at, status) "
            "VALUES (NULL, NOW(), %s) RETURNING run_id",
            ("running",),
        )
        run_id = cur.fetchone()[0]
        ingested = 0
        try:
            for table, row in self.fetch(cursor):
                if table == "ref_company_tickers":
                    keys = ["cik"]
                elif table == "filings_index":
                    keys = ["accession"]
                elif table == "fundamentals_xbrl":
                    keys = ["fact_id"]
                elif table == "earnings_events":
                    keys = ["event_id"]
                else:
                    keys = conflict_keys
                ingested += upsert_fn(conn, table, [row], keys)
        finally:
            cur.execute(
                "UPDATE ingestion_runs SET ended_at=NOW(), status=%s, "
                "rows_ingested=%s, error=%s WHERE run_id=%s",
                ("success", ingested, None, run_id),
            )
            conn.commit()
