"""Shipyard page (/shipyard) and its cookie-authenticated order route.

The browser cannot read the httpOnly session cookie, so the page posts its
build to POST /shipyard/orders here, which calls the same service as the
Bearer-only POST /api/v1/shipyard/orders.
"""

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from app import defects, strings
from app.db import get_session
from app.errors import error_response
from app.models import User
from app.services import shipyard
from app.web.session import optional_user
from app.web.templating import render

router = APIRouter()


@router.get("/shipyard")
def shipyard_page(
    request: Request,
    user: User | None = Depends(optional_user),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    parts = shipyard.list_parts(session)
    sections = [
        {
            "slug": slug,
            "title": title,
            "parts": [part for part in parts if part.category == category],
        }
        for category, (slug, title) in strings.SHIPYARD_CATEGORIES.items()
    ]
    config = {
        "parts": [shipyard.part_as_dict(part) for part in parts],
        "loggedIn": user is not None,
        "staleTotalOnAdd": defects.is_enabled("ADD_BUTTON_STALE_TOTAL"),
        "strings": {
            "hullTop": strings.SHIPYARD_HULL_TOP,
            "hullBottom": strings.SHIPYARD_HULL_BOTTOM,
            "credits": strings.SHIPYARD_CREDITS,
            "remove": strings.SHIPYARD_REMOVE,
            "noHull": strings.SHIPYARD_NO_HULL,
            "orderSuccess": strings.SHIPYARD_ORDER_SUCCESS,
            "orderFailed": strings.SHIPYARD_ORDER_FAILED,
        },
    }
    return render(request, "shipyard.html", user, sections=sections, shipyard_config=config)


@router.post("/shipyard/orders")
def shipyard_order(
    body: Any = Body(None),
    user: User | None = Depends(optional_user),
    session: Session = Depends(get_session),
) -> JSONResponse:
    if user is None:
        return error_response(401, strings.NOT_AUTHENTICATED)
    part_ids = body.get("parts") if isinstance(body, dict) else None
    try:
        order = shipyard.create_order(session, user, part_ids)
    except shipyard.InvalidBuild as exc:
        return error_response(400, exc.message)
    return JSONResponse(status_code=201, content={"number": order.number, "total": order.total})
