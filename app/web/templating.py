"""Jinja2 setup shared by all pages."""

from dataclasses import dataclass
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import defects, strings, validation
from app.models import User


@dataclass(frozen=True)
class NavItem:
    label: str
    href: str
    testid: str


# Plain header links after the logo and the partner mark. The "Order" and
# "Order Status" buttons and "Account" (whose target depends on the session)
# are added by the template. A new site section is one more item here.
NAV_ITEMS = [
    NavItem(label=strings.NAV_SHIPYARD, href="/shipyard", testid="header-shipyard-link"),
]


def header_search_placeholder() -> str:
    if defects.is_enabled("HEADER_SEARCH_PLACEHOLDER"):
        return strings.NAV_ORDER_NUMBER_WRONG
    return strings.NAV_ORDER_NUMBER


def header_search_button() -> bool:
    """Canon: the header search has no button, Enter starts it. Seeded defect: "Go!"."""
    return defects.is_enabled("HEADER_SEARCH_EXTRA_BUTTON")


templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
templates.env.globals.update(
    t=strings,
    nav_items=NAV_ITEMS,
    header_search_placeholder=header_search_placeholder,
    header_search_button=header_search_button,
    validation_rules=validation.client_rules(),
)


def render(
    request: Request, template: str, user: User | None, status_code: int = 200, **context
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, template, {"user": user, **context}, status_code=status_code
    )
