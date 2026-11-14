"""Autopilot API: create, log in, delete. No tokens.

Bodies are read as raw JSON and checked by app/validation.py, so a missing
field, null or a number all get the documented 400 message.
"""

from typing import Any

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import strings
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.schemas import AutopilotIdResponse, OkResponse
from app.services import autopilots, orders

router = APIRouter(prefix="/autopilot", tags=["autopilot"])

_CREATE_EXAMPLE = {"login": "ilves", "password": "0101", "firstName": "Ilves"}
_LOGIN_EXAMPLE = {"login": "ilves", "password": "0101"}


def as_object(body: Any) -> dict:
    """Anything that is not a JSON object counts as "no fields sent"."""
    return body if isinstance(body, dict) else {}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OkResponse,
    responses={
        400: {"model": ErrorResponse, "description": "A field is missing or breaks its rule"},
        409: {"model": ErrorResponse, "description": "Login already in use"},
    },
)
def create(
    body: Any = Body(None, examples=[_CREATE_EXAMPLE]), session: Session = Depends(get_session)
) -> Any:
    """login: 2-10 Latin letters; password: exactly 4 digits (as a string);
    firstName: 2-10 Latin letters. All three are required strings."""
    data = as_object(body)
    try:
        autopilots.create(session, data.get("login"), data.get("password"), data.get("firstName"))
    except autopilots.InsufficientData:
        raise ApiError(400, strings.AUTOPILOT_CREATE_INSUFFICIENT) from None
    except autopilots.LoginTaken:
        raise ApiError(409, strings.AUTOPILOT_LOGIN_TAKEN) from None
    except autopilots.Crashed:
        # Seeded defect, SSI-39: the raw database error in a body of its own
        # shape, not the stand's {"ok": false, "message": ...}.
        return JSONResponse(
            status_code=500, content={"code": 500, "message": strings.AUTOPILOT_CRASH_MESSAGE}
        )
    return OkResponse()


@router.post(
    "/login",
    responses={
        400: {"model": ErrorResponse, "description": "login or password is missing"},
        404: {"model": ErrorResponse, "description": "Wrong pair or unknown login"},
    },
)
def login(
    body: Any = Body(None, examples=[_LOGIN_EXAMPLE]), session: Session = Depends(get_session)
) -> AutopilotIdResponse:
    data = as_object(body)
    try:
        autopilot = autopilots.authenticate(session, data.get("login"), data.get("password"))
    except autopilots.InsufficientData:
        raise ApiError(400, strings.AUTOPILOT_LOGIN_INSUFFICIENT) from None
    except autopilots.Unavailable:
        raise ApiError(504, strings.SERVICE_UNAVAILABLE) from None
    if autopilot is None:
        raise ApiError(404, strings.AUTOPILOT_ACCOUNT_NOT_FOUND)
    return AutopilotIdResponse(id=autopilot.id)


@router.delete("", include_in_schema=False)
@router.delete("/", include_in_schema=False)
def delete_without_id() -> None:
    raise ApiError(400, strings.AUTOPILOT_DELETE_INSUFFICIENT)


@router.delete(
    "/{autopilot_id}",
    responses={
        400: {"model": ErrorResponse, "description": "No id in the path"},
        404: {"model": ErrorResponse, "description": "No autopilot with this id"},
    },
)
def delete(autopilot_id: str, session: Session = Depends(get_session)) -> OkResponse:
    """Deletes the autopilot. Orders it had accepted are no longer found by track."""
    number = orders.parse_number(autopilot_id)
    autopilot = autopilots.get(session, number) if number is not None else None
    if autopilot is None:
        raise ApiError(404, strings.AUTOPILOT_NO_SUCH_ID)
    autopilots.delete(session, autopilot)
    return OkResponse()
