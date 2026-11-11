"""Shipyard API: the parts catalog and build orders of the current web account."""

from typing import Any

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.auth import current_user
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.models import User
from app.schemas import ShipyardOrderCreated, ShipyardOrdersResponse, ShipyardPartsResponse
from app.services import shipyard

router = APIRouter(prefix="/shipyard", tags=["shipyard"])

_401 = {401: {"model": ErrorResponse, "description": "No token, bad token or deleted user"}}


@router.get("/parts")
def parts(session: Session = Depends(get_session)) -> ShipyardPartsResponse:
    """The catalog, in display order. Public."""
    catalog = shipyard.list_parts(session)
    return ShipyardPartsResponse(parts=[shipyard.part_as_dict(part) for part in catalog])


@router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "No hull, two hulls or an unknown part id"},
        **_401,
    },
)
def create_order(
    body: Any = Body(None, examples=[{"parts": [1, 4, 8]}]),
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> ShipyardOrderCreated:
    """Orders a build: exactly one hull plus any engines and modules, in build
    order; a part may repeat. The total is computed by the server and the hull
    counts twice (top and belly plating)."""
    part_ids = body.get("parts") if isinstance(body, dict) else None
    try:
        order = shipyard.create_order(session, user, part_ids)
    except shipyard.InvalidBuild as exc:
        raise ApiError(400, exc.message) from None
    return ShipyardOrderCreated(number=order.number, total=order.total)


@router.get("/orders", responses=_401)
def list_orders(
    user: User = Depends(current_user), session: Session = Depends(get_session)
) -> ShipyardOrdersResponse:
    """Build orders of the current account, oldest first."""
    orders = shipyard.list_orders(session, user)
    return ShipyardOrdersResponse(orders=[shipyard.order_as_dict(order) for order in orders])
