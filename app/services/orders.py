"""Rental orders: create, find, accept, finish, cancel, and the status chain.

The status is never stored. It is a pure function of the order's timestamps
and the order's own clock, so the testing hook can move one order through
time without touching anything else.
"""

import secrets
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import clock, defects, validation
from app.config import get_settings
from app.models import Autopilot, Order, Station

TRACK_MIN = 10000
TRACK_MAX = 99999

# Status values, in chain order; DELAYED stands apart.
HANGAR = "hangar"
HEADING = "heading"
ON_SITE = "on_site"
FLYING = "flying"
ENDED = "ended"
DELAYED = "delayed"


class InvalidFields(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors  # {field: message}, in form order

    @property
    def first_message(self) -> str:
        return next(iter(self.errors.values()))


class AlreadyInProgress(Exception):
    pass


class CannotFinish(Exception):
    pass


# --- time and status -----------------------------------------------------------


def order_now(order: Order) -> datetime:
    """The current moment on this order's own clock."""
    return clock.now() + timedelta(seconds=order.clock_offset_seconds)


def rental_ends_at(order: Order) -> datetime | None:
    """Rental runs from the hand-over (finish) for rent_time days."""
    if order.finished_at is None:
        return None
    return order.finished_at + timedelta(days=order.rent_time)


def status(order: Order) -> str:
    now = order_now(order)
    if order.finished_at is not None:
        if now >= rental_ends_at(order):
            return ENDED
        if now >= order.finished_at + timedelta(minutes=get_settings().pickup_minutes):
            return FLYING
        # Seeded defect: "on site" never comes, the previous status holds.
        return HEADING if defects.is_enabled("STATUS_ON_SITE_SKIPPED") else ON_SITE
    deadline = order.delivery_date
    if defects.is_enabled("DELAYED_ONE_DAY_EARLY"):
        deadline -= timedelta(days=1)  # seeded defect: late from 00:00 of the delivery day
    if now >= clock.end_of_day(deadline):
        return DELAYED
    return HEADING if order.accepted_at is not None else HANGAR


def earliest_delivery_date() -> date:
    """The first day a shuttle can be ordered for: tomorrow."""
    if defects.is_enabled("FORM_DATE_TODAY"):
        return clock.today()  # seeded defect: today is accepted as well
    return clock.tomorrow()


# --- lookups -------------------------------------------------------------------


def _is_visible(order: Order, by_track: bool = False) -> bool:
    """Canceled orders and orders of a deleted autopilot are gone for clients.

    Two seeded defects leave such orders findable by track number (on the
    status page and in GET /orders/track); nothing else sees them.
    """
    canceled = order.canceled_at is not None
    orphaned = order.autopilot_deleted
    if by_track:
        canceled = canceled and not defects.is_enabled("CANCELED_ORDER_VISIBLE")
        orphaned = orphaned and not defects.is_enabled("TRACK_DELETED_AUTOPILOT")
    return not (canceled or orphaned)


def parse_number(raw: Any) -> int | None:
    """Track numbers and ids arrive as text or JSON; anything but a plain
    non-negative integer is simply "not found"."""
    if isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not (text.isascii() and text.isdigit()) or len(text) > 9:
        return None
    return int(text)


def find_by_track(session: Session, track: Any) -> Order | None:
    number = parse_number(track)
    if number is None:
        return None
    order = session.scalar(select(Order).where(Order.track == number))
    return order if order is not None and _is_visible(order, by_track=True) else None


def find_by_id(session: Session, order_id: Any) -> Order | None:
    number = parse_number(order_id)
    if number is None:
        return None
    order = session.get(Order, number)
    return order if order is not None and _is_visible(order) else None


def list_orders(session: Session, autopilot_id: int | None = None) -> list[Order]:
    query = select(Order).order_by(Order.id)
    if autopilot_id is not None:
        query = query.where(Order.autopilot_id == autopilot_id)
    return [order for order in session.scalars(query) if _is_visible(order)]


# --- commands ------------------------------------------------------------------


def create(session: Session, data: dict[str, Any]) -> Order:
    """Validate and store a new order. Raises InvalidFields."""
    data = dict(data)
    if isinstance(data.get("address"), str):
        data["address"] = data["address"].strip()
    stations = {station.number: station for station in session.scalars(select(Station))}
    errors = validation.order_errors(data, set(stations), earliest_delivery_date())
    if errors:
        raise InvalidFields(errors)
    station = stations[data["station"]]
    for _ in range(50):
        order = Order(
            track=TRACK_MIN + secrets.randbelow(TRACK_MAX - TRACK_MIN + 1),
            first_name=data["firstName"],
            last_name=data["lastName"],
            address=data["address"],
            station_number=station.number,
            station_name=station.name,
            station_color=station.color,
            phone=data["phone"],
            rent_time=data["rentTime"],
            delivery_date=validation.parse_delivery_date(data["deliveryDate"]),
            comment=data.get("comment") or "",
            color=list(data.get("color") or []),
        )
        session.add(order)
        try:
            session.commit()
        except IntegrityError:  # the random track is taken: draw another
            session.rollback()
            continue
        return order
    raise RuntimeError("Could not allocate a free track number")


def accept(session: Session, order: Order, autopilot: Autopilot) -> None:
    """Raises AlreadyInProgress if some autopilot has already taken the order."""
    if order.accepted_at is not None:
        raise AlreadyInProgress
    order.accepted_at = order_now(order)
    order.autopilot_id = autopilot.id
    order.autopilot_first_name = autopilot.first_name
    session.commit()


def finish(session: Session, order: Order) -> None:
    """The autopilot is on site. Raises CannotFinish unless accepted and not yet finished."""
    if order.accepted_at is None or order.finished_at is not None:
        raise CannotFinish
    order.finished_at = order_now(order)
    session.commit()


def cancel(session: Session, order: Order) -> None:
    """Soft delete. Raises AlreadyInProgress once an autopilot has accepted the order."""
    if order.accepted_at is not None:
        raise AlreadyInProgress
    order.canceled_at = order_now(order)
    session.commit()


def shift_clock(session: Session, order: Order, delta: timedelta) -> None:
    """Testing hook: move this order's clock (forward for a positive delta)."""
    order.clock_offset_seconds += int(delta.total_seconds())
    session.commit()


# --- representation ------------------------------------------------------------


def _iso(moment: datetime | None) -> str | None:
    return moment.isoformat(timespec="seconds") if moment is not None else None


def as_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "track": order.track,
        "firstName": order.first_name,
        "lastName": order.last_name,
        "address": order.address,
        "station": {
            "number": order.station_number,
            "name": order.station_name,
            "color": order.station_color,
        },
        "phone": order.phone,
        "rentTime": order.rent_time,
        "deliveryDate": order.delivery_date.isoformat(),
        "comment": order.comment,
        "color": order.color,
        "status": status(order),
        "autopilotId": order.autopilot_id,
        "autopilotFirstName": order.autopilot_first_name,
        "createdAt": _iso(order.created_at),
        "acceptedAt": _iso(order.accepted_at),
        "finishedAt": _iso(order.finished_at),
        "rentalEndsAt": _iso(rental_ends_at(order)),
    }
