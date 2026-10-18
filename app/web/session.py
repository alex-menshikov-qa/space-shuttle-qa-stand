"""Browser session: an httpOnly cookie carrying the same JWT the API issues."""

from fastapi import Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import security
from app.config import get_settings
from app.db import get_session
from app.models import User
from app.services import users

COOKIE_NAME = "access_token"
_COOKIE_OPTIONS = {"path": "/", "httponly": True, "samesite": "lax"}


def optional_user(request: Request, session: Session = Depends(get_session)) -> User | None:
    """The logged-in user, or None for a guest (no, bad or expired cookie)."""
    token = request.cookies.get(COOKIE_NAME)
    return users.get_by_token(session, token) if token else None


def start_session(response: Response, user: User) -> None:
    response.set_cookie(
        COOKIE_NAME,
        security.create_access_token(user.id),
        max_age=get_settings().access_token_expire_minutes * 60,
        **_COOKIE_OPTIONS,
    )


def end_session(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, **_COOKIE_OPTIONS)
