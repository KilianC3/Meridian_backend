from __future__ import annotations

from fastapi import APIRouter

from . import (
    alerts,
    assets,
    cb,
    chokepoints,
    commodities,
    fx,
    geo,
    macro,
    policy,
    portfolio,
    ports,
    rates,
    trade,
    watchlist,
)

router = APIRouter(prefix="/v1")
router.include_router(macro.router)
router.include_router(rates.router)
router.include_router(fx.router)
router.include_router(commodities.router)
router.include_router(policy.router)
router.include_router(cb.router)
router.include_router(geo.router)
router.include_router(trade.router)
router.include_router(ports.router)
router.include_router(chokepoints.router)
router.include_router(assets.router)
router.include_router(portfolio.router)
router.include_router(watchlist.router)
router.include_router(alerts.router)
