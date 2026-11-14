"""Order form (/order) and order status (/track).

The form is one page with two steps switched by order.js; it posts to
POST /api/v1/orders, so the API and the form share one validation. The status
page is rendered on the server from the same order service the API uses.
"""

from dataclasses import dataclass
from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import clock, defects, strings
from app.db import get_session
from app.models import Order, User
from app.services import orders, stations
from app.web.session import optional_user
from app.web.templating import render

router = APIRouter()

DATE_FORMAT = "%d.%m.%Y"  # the format the order form shows and accepts
LONG_NAME = 10  # autopilot names from this length on are "long" (the rule allows 2-10)


@router.get("/order")
def order_form(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    # The server's "today" drives the date picker, so the browser clock can
    # never disagree with the API about what "tomorrow" is.
    config = {
        "today": clock.today().isoformat(),
        "minDate": orders.earliest_delivery_date().isoformat(),
    }
    return render(request, "order.html", user, order_config=config)


@dataclass(frozen=True)
class StatusStep:
    key: str  # testid suffix: "1".."5", or "delayed"
    title: str
    caption: str | None
    state: str  # "done" | "current" | "upcoming"
    delayed: bool = False


def _format_moment(order: Order) -> tuple[str, str]:
    ends = orders.rental_ends_at(order).astimezone(clock.tz())
    return f"{ends.day} {ends:%B}", f"{ends:%H:%M}"


def status_steps(order: Order) -> list[StatusStep]:
    """The chain of five statuses with the current one marked.

    Every status has a caption. Status 4 says "Until the rental is over"
    before the flight and "Rental ends on ..." from then on, also once it is
    passed; status 5 has a caption only while current. "Delayed" takes the
    place of step 2 (the autopilot should be on its way and is not on site).
    """
    status = orders.status(order)
    name = order.autopilot_first_name
    shown_name = name
    if (
        name
        and len(name) >= LONG_NAME
        and defects.is_enabled("TRACK_AUTOPILOT_NAME_TRUNCATED")
    ):
        # Seeded defect: a long name is cut to its first two characters.
        shown_name = name[:2] + strings.TRACK_NAME_ELLIPSIS
    heading = (
        strings.TRACK_STATUS_HEADING.format(first_name=shown_name)
        if name
        else strings.TRACK_STATUS_HEADING_UNASSIGNED
    )
    phone = strings.SUPPORT_PHONE
    flying_caption = flown_caption = ended_caption = None
    if order.finished_at is not None:
        day, time = _format_moment(order)
        flying_caption = strings.TRACK_STATUS_FLYING_CAPTION.format(day=day, time=time)
        flown_caption = flying_caption
        if defects.is_enabled("ENDED_STATUS_4_CAPTION"):
            # Seeded defect: a passed status 4 takes the next status's text.
            flown_caption = strings.TRACK_STATUS_ENDED
        ended_caption = strings.TRACK_STATUS_ENDED_CAPTION.format(first_name=name)
    contact = strings.TRACK_STATUS_HEADING_CAPTION.format(phone=phone)
    hangar = strings.TRACK_STATUS_HANGAR_CAPTION
    on_site = strings.TRACK_STATUS_ON_SITE_CAPTION
    upcoming_flight = strings.TRACK_STATUS_FLYING_CAPTION_UPCOMING
    # (key, title, caption while current, once passed, while still ahead)
    chain = [
        ("1", strings.TRACK_STATUS_HANGAR, hangar, hangar, hangar),
        ("2", heading, contact, contact, contact),
        ("3", strings.TRACK_STATUS_ON_SITE, on_site, on_site, on_site),
        ("4", strings.TRACK_STATUS_FLYING, flying_caption, flown_caption, upcoming_flight),
        ("5", strings.TRACK_STATUS_ENDED, ended_caption, None, None),
    ]
    position = {
        orders.HANGAR: 0,
        orders.HEADING: 1,
        orders.DELAYED: 1,
        orders.ON_SITE: 2,
        orders.FLYING: 3,
        orders.ENDED: 4,
    }[status]
    steps = []
    for index, (key, title, current, passed, ahead) in enumerate(chain):
        if index == position and status == orders.DELAYED:
            caption = strings.TRACK_STATUS_DELAYED_CAPTION.format(phone=phone)
            step = StatusStep("delayed", strings.TRACK_STATUS_DELAYED, caption, "current", True)
        elif index == position:
            step = StatusStep(key, title, current, "current")
        elif index < position:
            step = StatusStep(key, title, passed, "done")
        else:
            step = StatusStep(key, title, ahead, "upcoming")
        steps.append(step)
    return steps


def _shown_station(session: Session, order: Order) -> tuple[str, str]:
    """(name, colour) of the station the status page shows for the order."""
    if defects.is_enabled("TRACK_WRONG_STATION"):
        # Seeded defect: the next station by number, the first one after the last.
        known = stations.search(session, None)
        later = [station for station in known if station.number > order.station_number]
        wrong = (later or known or [None])[0]
        if wrong is not None:
            return wrong.name, wrong.color
    return order.station_name, order.station_color


def _order_view(session: Session, order: Order) -> dict:
    """What the status page shows for a found order (seeded defects included)."""
    station_name, station_color = _shown_station(session, order)
    delivery_date = order.delivery_date
    if defects.is_enabled("TRACK_DATE_PLUS_DAY"):
        delivery_date += timedelta(days=1)  # seeded defect: one day late
    colors = ", ".join(
        label for value, label in strings.SHUTTLE_COLORS.items() if value in order.color
    )
    if not colors and defects.is_enabled("TRACK_EMPTY_COLOR"):
        colors = strings.TRACK_EMPTY_COLOR_WRONG
    date_label = strings.ORDER_FIELD_DATE
    if defects.is_enabled("TRACK_DATE_LABEL"):
        date_label = strings.TRACK_DATE_LABEL_WRONG
    accepted = order.accepted_at is not None
    return {
        "steps": status_steps(order),
        "station_name": station_name,
        "station_color": station_color,
        "delivery_date": delivery_date.strftime(DATE_FORMAT),
        "rental_period": strings.RENTAL_PERIODS[order.rent_time - 1],
        "date_label": date_label,
        "colors": colors,
        # Canon: the comment row is always there, empty without a comment.
        # Seeded defect: without a comment there is no row at all.
        "comment_row": bool(order.comment) or not defects.is_enabled("TRACK_EMPTY_COMMENT"),
        # Cancel works until an autopilot accepts the order; after that the
        # button stays, disabled. Seeded defect: it disappears.
        "can_cancel": not accepted,
        "cancel_button": not (accepted and defects.is_enabled("TRACK_CANCEL_HIDDEN_ON_ACCEPT")),
    }


@router.get("/track")
def track(
    request: Request,
    t: str = "",
    user: User | None = Depends(optional_user),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """Three variants: no number yet (search row only), found, not found."""
    number = t.strip()
    order = orders.find_by_track(session, number) if number else None
    context: dict = {"number": number, "order": order}
    if order is not None:
        context.update(_order_view(session, order))
    else:
        context["runway"] = not defects.is_enabled("TRACK_IMAGE_NO_RUNWAY")
    status_code = 404 if number and order is None else 200
    return render(request, "track.html", user, status_code, **context)
