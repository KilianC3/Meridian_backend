from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import rate_limit
from app.api.routers import auth, datasources, health, jobs
from app.core.config import settings
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
app.include_router(telemetry_router)

app.middleware("http")(metrics_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")  # type: ignore[misc]
async def security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response
