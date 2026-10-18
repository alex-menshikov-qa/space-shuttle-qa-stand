"""Liveness/readiness check used by Docker, CI and the test suites."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_session

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    responses={
        200: {"content": {"application/json": {"example": {"status": "ok"}}}},
        503: {"content": {"application/json": {"example": {"status": "error"}}}},
    },
)
def health(session: Session = Depends(get_session)) -> JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "error"})
    return JSONResponse(content={"status": "ok"})
