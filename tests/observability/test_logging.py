import json
import logging

from _pytest.capture import CaptureFixture
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from app.core.logging import configure_logging


def test_structured_log_contains_trace_id(capfd: CaptureFixture[str]) -> None:
    configure_logging()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    logger = logging.getLogger("test")
    with tracer.start_as_current_span("test-span"):
        logger.info("hello")
    captured = capfd.readouterr().out.strip().splitlines()
    data = json.loads(captured[-1])
    assert data["message"] == "hello"
    assert "trace_id" in data and data["trace_id"] != "0" * 32
