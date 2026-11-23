"""Rental order API: create, list, find by track, accept, finish, cancel."""

from typing import Any

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app import defects, strings
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.models import Order
from app.schemas import OkResponse, OrderResponse, OrdersResponse, PageInfo, TrackResponse
from app.services import autopilots, orders, stations

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
    """Field rules are the order form's (see docs/api.md). `station` is a station
    number, `rentTime` is 1-7 days, `deliveryDate` is YYYY-MM-DD and not earlier
    than tomorrow; `comment` and `color` are optional."""
    if not isinstance(body, dict):
        raise ApiError(400, strings.BODY_INVALID)
    try:
        order = orders.create(session, body)
    except orders.InvalidFields as exc:
        raise ApiError(400, exc.first_message) from None
    return TrackResponse(track=order.track)


_LIST_400 = (
    "`limit` is not a number from 1 to 30, `page` is not a number from 0, or "
    "`nearestStation` is not a JSON array of station numbers as strings or names "
    "a station that does not exist"
)


def _page_number(raw: str | None, default: int, low: int, high: int | None, message: str) -> int:
    """A paging parameter: absent means the default; anything else must be a
    plain number within [low, high]."""
    if raw is None:
        return default
    number = orders.parse_number(raw)
    if number is None or number < low or (high is not None and number > high):
        raise ApiError(400, message)
    return number


@router.get(
    "",
    responses={
        400: {"model": ErrorResponse, "description": _LIST_400},
        404: {"model": ErrorResponse, "description": "Unknown autopilotId"},
    },
)
def list_orders(
    autopilotId: str | None = Query(  # noqa: N803 - the public parameter name
        None,
        description="Only the orders accepted by this autopilot",
        examples=["1"],
    ),
    limit: str | None = Query(
        None,
        description=(
            f"Orders per page, 1-{orders.PAGE_LIMIT_MAX}; default {orders.PAGE_LIMIT_DEFAULT}"
        ),
        examples=["10"],
    ),
    page: str | None = Query(
        None, description="Page number, from 0; default 0", examples=["0"]
    ),
    nearestStation: str | None = Query(  # noqa: N803
        None,
        description=(
            "Only the orders at these stations: a JSON array of station numbers as "
            'strings, e.g. `["1","2"]`'
        ),
        examples=['["1","2"]'],
    ),
    session: Session = Depends(get_session),
) -> OrdersResponse:
    """Orders page by page, oldest first (by id). All filters are optional and
    combine. Canceled orders and orders of deleted autopilots are not listed.
    `pageInfo.total` counts every matching order, whatever the page; a page past
    the end is empty. Checks run in this order: `limit`, `page`,
    `nearestStation`, `autopilotId`."""
    # Seeded defect ORDERS_LIMIT_OVER_30: no upper bound for limit.
    limit_max = None if defects.is_enabled("ORDERS_LIMIT_OVER_30") else orders.PAGE_LIMIT_MAX
    page_limit = _page_number(
        limit, orders.PAGE_LIMIT_DEFAULT, 1, limit_max, strings.ORDERS_LIMIT_INVALID
    )
    page_number = _page_number(page, 0, 0, None, strings.ORDERS_PAGE_INVALID)

    all_stations = stations.search(session)
    station_numbers = None
    shown_stations = all_stations
    if nearestStation is not None:
        station_numbers = orders.parse_station_numbers(nearestStation)
        if station_numbers is None:
            raise ApiError(400, strings.ORDERS_STATIONS_INVALID)
        known = {station.number for station in all_stations}
        for number in station_numbers:
            if number not in known:
                raise ApiError(400, strings.ORDERS_STATION_UNKNOWN.format(station=number))
        wanted = set(station_numbers)
        shown_stations = [station for station in all_stations if station.number in wanted]

    autopilot_id = None
    if autopilotId is not None:
        autopilot_id = orders.parse_number(autopilotId)
        if autopilot_id is None or autopilots.get(session, autopilot_id) is None:
            raise ApiError(404, strings.AUTOPILOT_NOT_FOUND.format(autopilot_id=autopilotId))

    found = orders.list_orders(session, autopilot_id, station_numbers)
    shown_page = page_number
    if defects.is_enabled("ORDERS_PAGE_FROM_ONE"):
        shown_page = max(page_number - 1, 0)  # seeded defect: pages counted from one
    start = shown_page * page_limit
    return OrdersResponse(
        orders=[orders.as_dict(order) for order in found[start : start + page_limit]],
        pageInfo=PageInfo(page=page_number, total=len(found), limit=page_limit),
        availableStations=[stations.as_dict(station) for station in shown_stations],
    )


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
