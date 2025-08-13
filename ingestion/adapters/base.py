from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Iterator


class BaseAdapter(ABC):
    """Base class for ingestion adapters."""

    name: str

    @abstractmethod
    def fetch(self, cursor: Any | None = None) -> Iterator[Any]:
        """Yield raw records from the remote source."""

    @abstractmethod
    def transform(self, item: Any) -> Iterable[dict[str, Any]]:
        """Map a raw record to one or more rows for storage."""

    def run(
        self,
        conn: Any,
        upsert_fn: Callable[[Any, str, Iterable[dict[str, Any]], list[str]], int],
        target_table: str,
        conflict_keys: list[str],
        cursor: Any | None = None,
    ) -> None:
        """Execute an ingestion run and log to ``ingestion_runs``."""

        cur = conn.cursor()
        started = datetime.now(timezone.utc)
        cur.execute(
            "INSERT INTO ingestion_runs (dataset_id, started_at, status) "
            "VALUES (%s, %s, %s) RETURNING run_id",
            (None, started, "running"),
        )
        run_id = cur.fetchone()[0]
        ingested = 0
        status = "success"
        error: str | None = None
        try:
            for item in self.fetch(cursor):
                rows = list(self.transform(item))
                ingested += upsert_fn(conn, target_table, rows, conflict_keys)
        except Exception as exc:  # pragma: no cover - simple error logging
            status = "failed"
            error = str(exc)
            raise
        finally:
            ended = datetime.now(timezone.utc)
            cur.execute(
                "UPDATE ingestion_runs SET ended_at=%s, status=%s, rows_ingested=%s, "
                "error=%s WHERE run_id=%s",
                (ended, status, ingested, error, run_id),
            )
            conn.commit()
