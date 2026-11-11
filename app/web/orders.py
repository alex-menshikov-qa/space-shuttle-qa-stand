"""Order form (/order) and order status (/track).

The form is one page with two steps switched by order.js; it posts to
POST /api/v1/orders, so the API and the form share one validation. The status
page is rendered on the server from the same order service the API uses.
"""

from dataclasses import dataclass

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import clock, strings
from app.db import get_session
from app.models import Order, User
from app.services import orders
from app.web.session import optional_user
from app.web.templating import render

router = APIRouter()

DATE_FORMAT = "%d.%m.%Y"  # the format the order form shows and accepts


@router.get("/order")
def order_form(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    # The server's "today" drives the date picker, so the browser clock can
    # never disagree with the API about what "tomorrow" is.
    config = {"today": clock.today().isoformat(), "minDate": clock.tomorrow().isoformat()}
    return render(request, "order.html", user, order_config=config)


@dataclass(frozen=True)
class StatusStep:
    key: str  # testid suffix: "1".."5", or "delayed"
    title: str
    caption: str | None  # shown for the current step only
    state: str  # "done" | "current" | "upcoming"
    delayed: bool = False


def _format_moment(order: Order) -> tuple[str, str]:
    ends = orders.rental_ends_at(order).astimezone(clock.tz())
    return f"{ends.day} {ends:%B}", f"{ends:%H:%M}"


def status_steps(order: Order) -> list[StatusStep]:
    """The chain of five statuses with the current one marked. "Delayed" takes
    the place of step 2 (the autopilot should be on its way and is not on site)."""
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
    chain = [
        ("1", strings.TRACK_STATUS_HANGAR, strings.TRACK_STATUS_HANGAR_CAPTION),
        ("2", heading, strings.TRACK_STATUS_HEADING_CAPTION.format(phone=phone)),
        ("3", strings.TRACK_STATUS_ON_SITE, strings.TRACK_STATUS_ON_SITE_CAPTION),
        ("4", strings.TRACK_STATUS_FLYING, flying_caption),
        ("5", strings.TRACK_STATUS_ENDED, ended_caption),
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
    for index, (key, title, caption) in enumerate(chain):
        if index == position and status == orders.DELAYED:
            delayed_caption = strings.TRACK_STATUS_DELAYED_CAPTION.format(phone=phone)
            step = StatusStep("delayed", strings.TRACK_STATUS_DELAYED, delayed_caption, "current", True)
        elif index == position:
            step = StatusStep(key, title, caption, "current")
        else:
            step = StatusStep(key, title, None, "done" if index < position else "upcoming")
        steps.append(step)
    return steps


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
        context.update(
            steps=status_steps(order),
            delivery_date=order.delivery_date.strftime(DATE_FORMAT),
            rental_period=strings.RENTAL_PERIODS[order.rent_time - 1],
            colors=", ".join(
                label for value, label in strings.SHUTTLE_COLORS.items() if value in order.color
            ),
            # Cancel is offered until an autopilot accepts the order.
            can_cancel=order.accepted_at is None,
        )
    status_code = 404 if number and order is None else 200
    return render(request, "track.html", user, status_code, **context)
