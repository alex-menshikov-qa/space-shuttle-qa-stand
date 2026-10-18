"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import defects, errors, strings
from app.api import health, v1

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    defects.check_flags()  # refuses to start on a misspelled BUG_* flag
    enabled = defects.enabled_defects()
    log.info("Seeded defects enabled: %s", ", ".join(enabled) or "none")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=strings.APP_TITLE,
        description=strings.APP_DESCRIPTION,
        lifespan=lifespan,
    )
    errors.register_handlers(app)
    app.include_router(health.router)
    app.include_router(v1.router)
    _drop_422_from_openapi(app)
    return app


def _drop_422_from_openapi(app: FastAPI) -> None:
    """Validation errors are answered with 400 (see errors.py), so the 422
    responses FastAPI documents by default would mislead readers of /docs."""
    default_openapi = app.openapi

    def openapi() -> dict:
        if app.openapi_schema is None:
            schema = default_openapi()
            for operations in schema["paths"].values():
                for operation in operations.values():
                    operation["responses"].pop("422", None)
            for name in ("HTTPValidationError", "ValidationError"):
                schema.get("components", {}).get("schemas", {}).pop(name, None)
        return app.openapi_schema

    app.openapi = openapi


app = create_app()
