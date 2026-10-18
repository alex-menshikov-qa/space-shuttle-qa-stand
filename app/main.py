"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import defects, strings
from app.api import health

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    enabled = defects.enabled_defects()
    log.info("Seeded defects enabled: %s", ", ".join(enabled) or "none")
    for flag in defects.unknown_flags():
        log.warning("Ignoring %s: no such seeded defect", flag)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=strings.APP_TITLE,
        description=strings.APP_DESCRIPTION,
        lifespan=lifespan,
    )
    app.include_router(health.router)
    return app


app = create_app()
