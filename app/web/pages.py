"""Home page and the account page."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import User
from app.web.session import end_session, optional_user
from app.web.templating import render

router = APIRouter()


@router.get("/")
def home(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    return render(request, "home.html", user)


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
