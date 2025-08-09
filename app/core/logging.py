from __future__ import annotations

import json
import logging
import sys
from typing import Any

import sentry_sdk
from opentelemetry import trace
from sentry_sdk.integrations.logging import LoggingIntegration

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        trace_id = trace.get_current_span().get_span_context().trace_id
        payload: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
        }
        if trace_id:
            payload["trace_id"] = f"{trace_id:032x}"
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    if settings.sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO, event_level=logging.ERROR
        )
        sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[sentry_logging])
