"""Ping: is the API alive? No database involved (see /health for that)."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app import strings

router = APIRouter(tags=["ping"])


@router.get(
    "/ping",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/plain": {"example": strings.PING_REPLY}}}},
)
def ping() -> str:
    """Answers `pong` as plain text while the API is up. Does not touch the database."""
    return strings.PING_REPLY
