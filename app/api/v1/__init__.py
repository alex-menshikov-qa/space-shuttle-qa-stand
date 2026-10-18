"""JSON API, version 1. Future routers (pilots, flights) are included here too."""

from fastapi import APIRouter

from app.api.v1 import auth

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
