from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, Set


def _parse_period(period: str) -> str:
    if len(period) == 6:
        return datetime.strptime(period, "%Y%m").date().isoformat()
    if len(period) == 8:
        return datetime.strptime(period, "%Y%m%d").date().isoformat()
    return period


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map logistics-related records to various tables."""

    vessel_state: Dict[str, dict[str, Any]] = {}
    port_queues: Dict[str, Set[str]] = {}
    chokepoint_transits: Dict[str, Set[str]] = {}

    for rec in records:
        source = rec.get("source")
        if source == "un_comtrade":
            yield {
                "reporter_iso2": rec.get("reporter"),
                "partner_iso2": rec.get("partner"),
                "hs_code": rec.get("hs_code"),
                "flow": rec.get("flow"),
                "period": _parse_period(str(rec.get("period"))),
                "value_usd": rec.get("value"),
                "quantity": rec.get("quantity"),
                "quantity_unit": rec.get("quantity_unit"),
                "source": source,
                "meta": rec.get("meta"),
            }
            continue

        if source == "gdelt_transport":
            gid = rec.get("GLOBALEVENTID")
            yield {
                "event_type": "transport_disruption",
                "ts": _parse_period(str(rec.get("DATEADDED"))),
                "mmsi": None,
                "port_id": None,
                "chokepoint_id": None,
                "lat": rec.get("ActionGeo_Lat"),
                "lon": rec.get("ActionGeo_Long"),
                "channel": None,
                "attrs": None,
                "dedupe_key": f"gdelt_transport:{gid}",
            }
            continue

        if source == "ais":
            mmsi = str(rec.get("mmsi"))
            ts = rec.get("ts")
            nav_status = rec.get("nav_status")
            port_id = rec.get("port_id")
            chokepoint_id = rec.get("chokepoint_id")
            draught = rec.get("draught_m")
            prev = vessel_state.get(mmsi, {})

            if (
                prev.get("nav_status") != "at_anchor"
                and nav_status == "at_anchor"
                and port_id
            ):
                port_queues.setdefault(port_id, set()).add(mmsi)
                yield {
                    "event_type": "AnchorageQueueEnter",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": port_id,
                    "chokepoint_id": None,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:AnchorageQueueEnter:{ts}",
                }
                yield {
                    "port_id": port_id,
                    "vessel_class": "all",
                    "ts": ts,
                    "queue_length": len(port_queues[port_id]),
                    "avg_wait_hours": None,
                    "throughput_departures": None,
                    "congestion_index": None,
                    "source": "aisstream",
                }

            if (
                prev.get("nav_status") == "at_anchor"
                and nav_status != "at_anchor"
                and port_id
                and mmsi in port_queues.get(port_id, set())
            ):
                port_queues[port_id].remove(mmsi)
                yield {
                    "event_type": "AnchorageQueueExit",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": port_id,
                    "chokepoint_id": None,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:AnchorageQueueExit:{ts}",
                }
                yield {
                    "port_id": port_id,
                    "vessel_class": "all",
                    "ts": ts,
                    "queue_length": len(port_queues[port_id]),
                    "avg_wait_hours": None,
                    "throughput_departures": None,
                    "congestion_index": None,
                    "source": "aisstream",
                }

            if (
                nav_status == "moored"
                and prev.get("nav_status") != "moored"
                and port_id
            ):
                yield {
                    "event_type": "PortCall",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": port_id,
                    "chokepoint_id": None,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:PortCall:{ts}",
                }

            if prev.get("port_id") and port_id is None and nav_status == "under_way":
                yield {
                    "event_type": "PortDepart",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": prev.get("port_id"),
                    "chokepoint_id": None,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:PortDepart:{ts}",
                }

            if prev.get("chokepoint_id") is None and chokepoint_id:
                chokepoint_transits.setdefault(chokepoint_id, set()).add(mmsi)
                yield {
                    "event_type": "TransitStart",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": None,
                    "chokepoint_id": chokepoint_id,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:TransitStart:{ts}",
                }
                yield {
                    "chokepoint_id": chokepoint_id,
                    "vessel_class": "all",
                    "ts": ts,
                    "active_transits": len(chokepoint_transits[chokepoint_id]),
                    "avg_transit_minutes": None,
                    "transit_delay_index": None,
                    "source": "aisstream",
                }

            if (
                prev.get("chokepoint_id")
                and chokepoint_id is None
                and prev.get("chokepoint_id") in chokepoint_transits
            ):
                cp = prev["chokepoint_id"]
                chokepoint_transits[cp].discard(mmsi)
                yield {
                    "event_type": "TransitEnd",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": None,
                    "chokepoint_id": cp,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": None,
                    "dedupe_key": f"{mmsi}:TransitEnd:{ts}",
                }
                yield {
                    "chokepoint_id": cp,
                    "vessel_class": "all",
                    "ts": ts,
                    "active_transits": len(chokepoint_transits[cp]),
                    "avg_transit_minutes": None,
                    "transit_delay_index": None,
                    "source": "aisstream",
                }

            if (
                prev.get("draught") is not None
                and draught is not None
                and draught != prev.get("draught")
            ):
                yield {
                    "event_type": "DraftChange",
                    "ts": ts,
                    "mmsi": mmsi,
                    "port_id": port_id,
                    "chokepoint_id": None,
                    "lat": rec.get("lat"),
                    "lon": rec.get("lon"),
                    "channel": None,
                    "attrs": {"from": prev.get("draught"), "to": draught},
                    "dedupe_key": f"{mmsi}:DraftChange:{ts}",
                }

            vessel_state[mmsi] = {
                "nav_status": nav_status,
                "port_id": port_id,
                "chokepoint_id": chokepoint_id,
                "draught": draught,
            }
