"""Jinja2 setup shared by all pages."""

from dataclasses import dataclass
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import strings, validation
from app.models import User


@dataclass(frozen=True)
class NavItem:
    label: str
    href: str
    testid: str


# Header links after the logo. "Account" is added by the template, because its
# target depends on the session. A new site section is one more item here.
NAV_ITEMS = [
    NavItem(label=strings.NAV_BUILDER, href="/", testid="header-builder-link"),
]

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
templates.env.globals.update(
    t=strings,
    nav_items=NAV_ITEMS,
    validation_rules=validation.client_rules(),
)


def render(
    request: Request, template: str, user: User | None, status_code: int = 200, **context
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, template, {"user": user, **context}, status_code=status_code
    )
