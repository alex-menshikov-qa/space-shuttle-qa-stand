"""Web-account API: register, login, current user, self-delete."""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import security, strings
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.models import User
from app.schemas import (
    LoginRequest,
    LoginResponse,
    OkResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.services import users

router = APIRouter(prefix="/auth", tags=["auth"])

_bearer = HTTPBearer(auto_error=False)
_WWW_AUTHENTICATE = {"WWW-Authenticate": "Bearer"}

_400 = {400: {"model": ErrorResponse, "description": "Missing, empty or invalid field"}}
_401 = {401: {"model": ErrorResponse, "description": "No token, bad token or deleted user"}}


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise ApiError(401, strings.NOT_AUTHENTICATED, _WWW_AUTHENTICATE)
    user = users.get_by_token(session, credentials.credentials)
    if user is None:
        raise ApiError(401, strings.TOKEN_INVALID, _WWW_AUTHENTICATE)
    return user


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={**_400, 409: {"model": ErrorResponse, "description": "Email already registered"}},
)
def register(body: RegisterRequest, session: Session = Depends(get_session)) -> RegisterResponse:
    """Name non-empty, valid email (unique, case-insensitive), password of 6+ characters."""
    try:
        user = users.register(session, body.name, body.email, body.password)
    except users.InvalidFields as exc:
        raise ApiError(400, exc.first_message) from None
    except users.EmailTaken:
        raise ApiError(409, strings.EMAIL_TAKEN) from None
    return RegisterResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        access_token=security.create_access_token(user.id),
    )


@router.post(
    "/login",
    responses={
        **_400,
        401: {"model": ErrorResponse, "description": "Wrong email or password"},
    },
)
def login(body: LoginRequest, session: Session = Depends(get_session)) -> LoginResponse:
    try:
        user = users.authenticate(session, body.email, body.password)
    except users.InvalidFields as exc:
        raise ApiError(400, exc.first_message) from None
    if user is None:
        raise ApiError(401, strings.LOGIN_FAILED)
    return LoginResponse(id=user.id, access_token=security.create_access_token(user.id))


@router.get("/me", responses=_401)
def me(user: User = Depends(current_user)) -> UserResponse:
    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.delete("/me", responses=_401)
def delete_me(
    user: User = Depends(current_user), session: Session = Depends(get_session)
) -> OkResponse:
    """Deletes the current user for good (used by tests to clean up)."""
    users.delete(session, user)
    return OkResponse()
