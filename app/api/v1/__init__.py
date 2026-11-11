"""JSON API, version 1."""

from fastapi import APIRouter

from app.api.v1 import auth, autopilot, orders, shipyard, stations, testing
from app.config import get_settings

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(autopilot.router)
router.include_router(stations.router)
router.include_router(orders.router)
router.include_router(shipyard.router)
if get_settings().test_hooks:
    router.include_router(testing.router)
