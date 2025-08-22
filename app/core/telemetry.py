from __future__ import annotations

from time import perf_counter
from typing import Awaitable, Callable

from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

router = APIRouter()

REQUEST_COUNT = Counter(
    "request_count", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])

RISK_COMPUTE_COUNT = Counter("risk_compute_total", "Risk computations")
RISK_COMPUTE_LATENCY = Histogram(
    "risk_compute_latency_seconds", "Risk computation latency"
)
GRAPH_UPDATE_COUNT = Counter("graph_update_total", "Factor graph updates")
CASCADE_SIM_COUNT = Counter("cascade_sim_total", "Cascade simulations")


def record_graph_update() -> None:
    GRAPH_UPDATE_COUNT.inc()


def record_cascade_sim() -> None:
    CASCADE_SIM_COUNT.inc()


@router.get("/metrics")  # type: ignore[misc]
def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


async def metrics_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = perf_counter()
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(perf_counter() - start)
    return response
