from __future__ import annotations

import pytest

from app.scheduler import scheduler as scheduler_module
from app.scheduler.jobs import heartbeat


@pytest.mark.asyncio
async def test_scheduler_lifecycle() -> None:
    scheduler_module.start()
    scheduler_module.shutdown()


@pytest.mark.asyncio
async def test_heartbeat_job() -> None:
    await heartbeat.run()
