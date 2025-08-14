"""Adapter for aisstream.io WebSocket messages."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import logistics

from .base import BaseAdapter


class AISStreamAdapter(BaseAdapter):
    name = "aisstream"

    def __init__(self, messages: Iterable[dict[str, Any]]):
        self.messages = list(messages)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.messages

    def transform(self, item: dict[str, Any]):
        return {
            "msg_id": item.get("msg_id"),
            "ts": item.get("ts"),
            "mmsi": item.get("mmsi"),
            "lat": item.get("lat"),
            "lon": item.get("lon"),
            "sog_kn": item.get("sog_kn"),
            "cog_deg": item.get("cog_deg"),
            "nav_status": item.get("nav_status"),
            "msg_type": item.get("msg_type"),
            "channel": item.get("channel"),
            "payload": item.get("raw"),
        }

    def run(
        self,
        conn,
        upsert_fn,
        target_table,
        conflict_keys,
        cursor=None,
    ):  # pragma: no cover
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingestion_runs (dataset_id, started_at, status) "
            "VALUES (NULL, NOW(), %s) RETURNING run_id",
            ("running",),
        )
        run_id = cur.fetchone()[0]
        ingested = 0
        try:
            for msg in self.fetch(cursor):
                raw_row = self.transform(msg)
                ingested += upsert_fn(conn, "ais_raw", [raw_row], ["msg_id"])
                vessel_row = {
                    k: msg.get(k)
                    for k in [
                        "mmsi",
                        "imo",
                        "call_sign",
                        "name",
                        "ship_type_code",
                        "ship_type_group",
                        "length_m",
                        "width_m",
                        "draught_m",
                    ]
                    if msg.get(k) is not None
                }
                if vessel_row:
                    upsert_fn(conn, "vessels", [vessel_row], ["mmsi"])
                for row in logistics.transform([dict(msg, source="ais")]):
                    if "event_type" in row:
                        upsert_fn(conn, "logistics_events", [row], ["dedupe_key"])
                    elif "queue_length" in row:
                        upsert_fn(
                            conn,
                            "port_congestion_ts",
                            [row],
                            ["port_id", "vessel_class", "ts"],
                        )
                    elif "active_transits" in row:
                        upsert_fn(
                            conn,
                            "chokepoint_ts",
                            [row],
                            ["chokepoint_id", "vessel_class", "ts"],
                        )
        finally:
            cur.execute(
                "UPDATE ingestion_runs SET ended_at=NOW(), status=%s, "
                "rows_ingested=%s WHERE run_id=%s",
                ("success", ingested, run_id),
            )
            conn.commit()
