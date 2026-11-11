"""Landing, HoloNet stub, the account page and the HTML 404.
The order form and order status live in web/orders.py, the shipyard in web/shipyard.py."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import story_data
from app.db import SessionLocal
from app.models import User
from app.services import users
from app.web.session import COOKIE_NAME, end_session, optional_user
from app.web.templating import render

router = APIRouter()

# Set by landing.js when the visitor accepts the cookie banner.
COOKIES_ACCEPTED_COOKIE = "cookies_accepted"


@router.get("/")
def home(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    return render(
        request,
        "home.html",
        user,
        faq=story_data.load("faq"),
        cookies_accepted=COOKIES_ACCEPTED_COOKIE in request.cookies,
    )


@router.get("/holonet")
def holonet(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    return render(request, "holonet.html", user)


@router.get("/account", response_model=None)
def account(
    request: Request, user: User | None = Depends(optional_user)
) -> HTMLResponse | RedirectResponse:
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return render(request, "account.html", user)


@router.post("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse("/login", status_code=303)
    end_session(response)
    return response


def not_found_page(request: Request) -> HTMLResponse:
    """HTML 404 for browser paths. Called from the error handler, outside
    dependency injection, so the session user is resolved by hand."""
    token = request.cookies.get(COOKIE_NAME)
    user = None
    if token:
        with SessionLocal() as session:
            user = users.get_by_token(session, token)
    return render(request, "not_found.html", user, 404)
