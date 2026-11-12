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

    Every status has a caption; statuses 4 and 5 have a different one (or
    none) while they are not current. "Delayed" takes the place of step 2
    (the autopilot should be on its way and is not on site).
    """
    status = orders.status(order)
    name = order.autopilot_first_name
    heading = (
        strings.TRACK_STATUS_HEADING.format(first_name=name)
        if name
        else strings.TRACK_STATUS_HEADING_UNASSIGNED
    )
    phone = strings.SUPPORT_PHONE
    flying_caption = ended_caption = None
    if order.finished_at is not None:
        day, time = _format_moment(order)
        flying_caption = strings.TRACK_STATUS_FLYING_CAPTION.format(day=day, time=time)
        ended_caption = strings.TRACK_STATUS_ENDED_CAPTION.format(first_name=name)
    contact = strings.TRACK_STATUS_HEADING_CAPTION.format(phone=phone)
    # (key, title, caption while current, caption while not current)
    chain = [
        ("1", strings.TRACK_STATUS_HANGAR, *[strings.TRACK_STATUS_HANGAR_CAPTION] * 2),
        ("2", heading, contact, contact),
        ("3", strings.TRACK_STATUS_ON_SITE, *[strings.TRACK_STATUS_ON_SITE_CAPTION] * 2),
        (
            "4",
            strings.TRACK_STATUS_FLYING,
            flying_caption,
            strings.TRACK_STATUS_FLYING_CAPTION_INACTIVE,
        ),
        ("5", strings.TRACK_STATUS_ENDED, ended_caption, None),
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
    for index, (key, title, active_caption, inactive_caption) in enumerate(chain):
        if index == position and status == orders.DELAYED:
            caption = strings.TRACK_STATUS_DELAYED_CAPTION.format(phone=phone)
            step = StatusStep("delayed", strings.TRACK_STATUS_DELAYED, caption, "current", True)
        elif index == position:
            step = StatusStep(key, title, active_caption, "current")
        elif (
            key == "4" and status == orders.ENDED and defects.is_enabled("ENDED_STATUS_4_ACTIVE")
        ):
            # Seeded defect: status 4 stays highlighted next to status 5.
            step = StatusStep(key, title, active_caption, "current")
        else:
            state = "done" if index < position else "upcoming"
            step = StatusStep(key, title, inactive_caption, state)
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
    if defects.is_enabled("TRACK_DATE_MINUS_DAY"):
        delivery_date -= timedelta(days=1)
    colors = ", ".join(
        label for value, label in strings.SHUTTLE_COLORS.items() if value in order.color
    )
    if not colors and defects.is_enabled("TRACK_EMPTY_COLOR"):
        colors = strings.TRACK_EMPTY_COLOR_WRONG
    comment = order.comment
    if not comment and defects.is_enabled("TRACK_EMPTY_COMMENT"):
        comment = strings.TRACK_EMPTY_COMMENT_WRONG
    return {
        "steps": status_steps(order),
        "station_name": station_name,
        "station_color": station_color,
        "delivery_date": delivery_date.strftime(DATE_FORMAT),
        "rental_period": strings.RENTAL_PERIODS[order.rent_time - 1],
        # Canon: Rental Period closes the second group. Seeded defect: it opens the third.
        "period_group": 3 if defects.is_enabled("TRACK_PERIOD_GROUP") else 2,
        "colors": colors,
        "comment": comment,
        # Cancel works until an autopilot accepts the order.
        "can_cancel": order.accepted_at is None,
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
        context["not_found_image"] = not defects.is_enabled("TRACK_NO_IMAGE")
    status_code = 404 if number and order is None else 200
    return render(request, "track.html", user, status_code, **context)
