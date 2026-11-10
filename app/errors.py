"""Unified error format: {"ok": false, "message": "<text>"} for every error.

Request validation errors are answered with 400 instead of FastAPI's default 422.
The one exception is a 404 outside /api/*: a browser gets an HTML page.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import strings
from app.validation import REQUIRED_MESSAGES
from app.web.pages import not_found_page

# A 404 under these paths stays JSON; anywhere else a browser gets an HTML page.
_API_PREFIXES = ("/api/", "/health")


def _is_api_path(path: str) -> bool:
    return path == "/api" or path.startswith(_API_PREFIXES)


class ErrorResponse(BaseModel):
    """Body of every error response (used for the OpenAPI docs)."""

    ok: bool = False
    message: str


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.message = message
        self.headers = headers


def error_response(
    status_code: int, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"ok": False, "message": message}, headers=headers
    )


def validation_message(exc: RequestValidationError) -> str:
    """One readable message for the first problem pydantic found.

    A missing or null field gets the same text as an empty one ("Name is required").
    """
    error = exc.errors()[0]
    loc = [part for part in error["loc"] if part != "body"]
    if not loc or error["type"] in {"json_invalid", "model_attributes_type", "dict_type"}:
        return strings.BODY_INVALID
    field = str(loc[0])
    if error["type"] == "missing" or error.get("input", "") is None:
        return REQUIRED_MESSAGES.get(field, strings.FIELD_REQUIRED.format(field=field))
    return strings.FIELD_INVALID.format(field=field)


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.status_code, exc.message, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(400, validation_message(exc))

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> Response:
        if exc.status_code == 404 and not _is_api_path(request.url.path):
            return await run_in_threadpool(not_found_page, request)
        return error_response(exc.status_code, str(exc.detail), exc.headers)

    # Starlette still re-raises the exception afterwards, so uvicorn logs the traceback.
    @app.exception_handler(Exception)
    async def unhandled_error(_: Request, __: Exception) -> JSONResponse:
        return error_response(500, strings.INTERNAL_ERROR)
