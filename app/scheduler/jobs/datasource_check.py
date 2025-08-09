from __future__ import annotations

import logging

from app.services import datasource_service

logger = logging.getLogger(__name__)


async def run() -> None:
    status = await datasource_service.status()
    logger.info("datasource_check", extra=status)
