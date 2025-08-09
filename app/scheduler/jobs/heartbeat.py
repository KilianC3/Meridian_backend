from __future__ import annotations

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def run() -> None:
    logger.info("heartbeat", extra={"ts": datetime.utcnow().isoformat()})
