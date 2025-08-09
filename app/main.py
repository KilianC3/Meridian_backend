from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram

from app.api.routers import auth, datasources, health
from app.core.config import settings

REQUEST_COUNT = Counter(
    "request_count", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])


app = FastAPI(title=settings.app_name, version=settings.version)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(datasources.router)


@app.middleware("http")
async def metrics_middleware(request, call_next):  # type: ignore[no-untyped-def]
    from time import perf_counter

    start = perf_counter()
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(perf_counter() - start)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
