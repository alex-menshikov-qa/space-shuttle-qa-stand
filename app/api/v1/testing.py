"""Testing hooks. The router is mounted only when TEST_HOOKS is on;
otherwise every path here is a plain 404.

Time shift: each order has its own clock. Moving it forward makes the
time-dependent statuses (delayed, flying, ended) reachable without waiting,
and affects nothing but that one order.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app import strings
from app.db import get_session
from app.errors import ApiError, ErrorResponse
from app.schemas import OrderResponse
from app.services import orders

router = APIRouter(prefix="/testing", tags=["testing"])

_UNITS = ("days", "hours", "minutes")
_MAX_SHIFT = timedelta(days=3650)


@router.post(
    "/orders/{track}/time-shift",
    responses={
        400: {"model": ErrorResponse, "description": "No usable days / hours / minutes"},
        404: {"model": ErrorResponse, "description": "No such order"},
    },
)
def time_shift(
    track: str,
    body: Any = Body(None, examples=[{"hours": 25}]),
    session: Session = Depends(get_session),
) -> OrderResponse:
    """Moves the order's own clock by `days` + `hours` + `minutes` (numbers,
    at least one; negative values move it back). Shifts add up. Returns the
    order with its status at the new moment."""
    data = body if isinstance(body, dict) else {}
    parts = {unit: data[unit] for unit in _UNITS if unit in data}
    numeric = all(
        isinstance(value, int | float) and not isinstance(value, bool) for value in parts.values()
    )
    if not parts or not numeric:
        raise ApiError(400, strings.TIME_SHIFT_INVALID)
    try:
        delta = timedelta(**parts)
    except (OverflowError, ValueError):
        raise ApiError(400, strings.TIME_SHIFT_INVALID) from None
    order = orders.find_by_track(session, track)
    if order is None:
        raise ApiError(404, strings.ORDER_NOT_FOUND)
    if abs(timedelta(seconds=order.clock_offset_seconds) + delta) > _MAX_SHIFT:
        raise ApiError(400, strings.TIME_SHIFT_INVALID)
    orders.shift_clock(session, order, delta)
    return OrderResponse(order=orders.as_dict(order))
