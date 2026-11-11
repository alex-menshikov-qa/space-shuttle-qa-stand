"""Rental order API: create, list, find by track, accept, finish, cancel."""

from typing import Any

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app import strings
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.models import Order
from app.schemas import OkResponse, OrderResponse, OrdersResponse, TrackResponse
from app.services import autopilots, orders

router = APIRouter(prefix="/orders", tags=["orders"])

_ORDER_EXAMPLE = {
    "firstName": "Mon",
    "lastName": "Mothma",
    "address": "Senate District, 500 Republica",
    "station": 2,
    "phone": "+10101010101",
    "rentTime": 3,
    "deliveryDate": "2027-01-15",
    "comment": "Ring twice",
    "color": ["PINKY_SWEAR"],
}

_400_SEARCH = {400: {"model": ErrorResponse, "description": "A required parameter is missing"}}


def _order_by_id(session: Session, order_id: str) -> Order:
    order = orders.find_by_id(session, order_id)
    if order is None:
        raise ApiError(404, strings.ORDER_NO_SUCH_ID)
    return order


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "A field breaks its rule"}},
)
def create(
    body: Any = Body(None, examples=[_ORDER_EXAMPLE]), session: Session = Depends(get_session)
) -> TrackResponse:
    """Field rules are the order form's (see README). `station` is a station
    number, `rentTime` is 1-7 days, `deliveryDate` is YYYY-MM-DD and not earlier
    than tomorrow; `comment` and `color` are optional."""
    if not isinstance(body, dict):
        raise ApiError(400, strings.BODY_INVALID)
    try:
        order = orders.create(session, body)
    except orders.InvalidFields as exc:
        raise ApiError(400, exc.first_message) from None
    return TrackResponse(track=order.track)


@router.get(
    "",
    responses={404: {"model": ErrorResponse, "description": "Unknown autopilotId"}},
)
def list_orders(
    autopilotId: str | None = None,  # noqa: N803 - the public parameter name
    session: Session = Depends(get_session),
) -> OrdersResponse:
    """All orders, or the ones accepted by `autopilotId`. Canceled orders and
    orders of deleted autopilots are not listed."""
    autopilot_id = None
    if autopilotId is not None:
        autopilot_id = orders.parse_number(autopilotId)
        if autopilot_id is None or autopilots.get(session, autopilot_id) is None:
            raise ApiError(404, strings.AUTOPILOT_NOT_FOUND.format(autopilot_id=autopilotId))
    found = orders.list_orders(session, autopilot_id)
    return OrdersResponse(orders=[orders.as_dict(order) for order in found])


@router.get(
    "/track",
    responses={**_400_SEARCH, 404: {"model": ErrorResponse, "description": "No such order"}},
)
def track(t: str | None = None, session: Session = Depends(get_session)) -> OrderResponse:
    if t is None or not t.strip():
        raise ApiError(400, strings.ORDER_SEARCH_INSUFFICIENT)
    order = orders.find_by_track(session, t)
    if order is None:
        raise ApiError(404, strings.ORDER_NOT_FOUND)
    return OrderResponse(order=orders.as_dict(order))


@router.put("/accept", include_in_schema=False)
@router.put("/accept/", include_in_schema=False)
@router.put("/finish", include_in_schema=False)
@router.put("/finish/", include_in_schema=False)
def action_without_id() -> None:
    raise ApiError(400, strings.ORDER_SEARCH_INSUFFICIENT)


@router.put(
    "/accept/{order_id}",
    responses={
        **_400_SEARCH,
        404: {"model": ErrorResponse, "description": "No such order or autopilot"},
        409: {"model": ErrorResponse, "description": "Order already accepted"},
    },
)
def accept(
    order_id: str,
    autopilotId: str | None = None,  # noqa: N803
    session: Session = Depends(get_session),
) -> OkResponse:
    """An autopilot takes the order. `order_id` is the order's `id`, not its track."""
    if autopilotId is None or not autopilotId.strip():
        raise ApiError(400, strings.ORDER_SEARCH_INSUFFICIENT)
    order = _order_by_id(session, order_id)
    autopilot_id = orders.parse_number(autopilotId)
    autopilot = autopilots.get(session, autopilot_id) if autopilot_id is not None else None
    if autopilot is None:
        raise ApiError(404, strings.AUTOPILOT_NO_SUCH_ID)
    try:
        orders.accept(session, order, autopilot)
    except orders.AlreadyInProgress:
        raise ApiError(409, strings.ORDER_IN_PROGRESS) from None
    return OkResponse()


@router.put(
    "/finish/{order_id}",
    responses={
        404: {"model": ErrorResponse, "description": "No such order"},
        409: {"model": ErrorResponse, "description": "Not accepted yet, or already finished"},
    },
)
def finish(order_id: str, session: Session = Depends(get_session)) -> OkResponse:
    """The autopilot has arrived and hands the shuttle over."""
    order = _order_by_id(session, order_id)
    try:
        orders.finish(session, order)
    except orders.CannotFinish:
        raise ApiError(409, strings.ORDER_CANNOT_FINISH) from None
    return OkResponse()


@router.put(
    "/cancel",
    responses={
        **_400_SEARCH,
        404: {"model": ErrorResponse, "description": "No such order"},
        409: {"model": ErrorResponse, "description": "Order already accepted"},
    },
)
def cancel(
    body: Any = Body(None, examples=[{"track": 12345}]), session: Session = Depends(get_session)
) -> OkResponse:
    """Cancels an order that no autopilot has accepted yet."""
    track_number = body.get("track") if isinstance(body, dict) else None
    if track_number is None or str(track_number).strip() == "":
        raise ApiError(400, strings.ORDER_SEARCH_INSUFFICIENT)
    order = orders.find_by_track(session, track_number)
    if order is None:
        raise ApiError(404, strings.ORDER_NOT_FOUND)
    try:
        orders.cancel(session, order)
    except orders.AlreadyInProgress:
        raise ApiError(409, strings.ORDER_IN_PROGRESS) from None
    return OkResponse()
