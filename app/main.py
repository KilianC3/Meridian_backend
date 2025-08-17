from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import rate_limit
from app.api.routers import auth, datasources, health, jobs, v1
from app.core.config import settings
from app.core import db
from app.core import cache
from app.core.logging import configure_logging
from app.core.telemetry import metrics_middleware
from app.core.telemetry import router as telemetry_router
from app.core.tracing import setup_tracing

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    dependencies=[Depends(rate_limit)],
)

setup_tracing(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(datasources.router)
app.include_router(jobs.router)
app.include_router(v1.router)
app.include_router(telemetry_router)

app.middleware("http")(metrics_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    db.init_pool()
    await cache.init_cache()


@app.on_event("shutdown")
async def _shutdown() -> None:
    db.close_pool()
    cache.close_cache()


@app.middleware("http")  # type: ignore[misc]
async def security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response
