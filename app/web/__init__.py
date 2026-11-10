"""Server-rendered pages. Each site section adds its router here."""

from fastapi import APIRouter

from app.web import auth, pages

router = APIRouter(include_in_schema=False)
router.include_router(pages.router)
router.include_router(auth.router)
