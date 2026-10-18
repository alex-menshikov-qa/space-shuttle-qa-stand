"""Register, login and forgot-password forms.

Plain HTML forms: GET shows the form, POST either re-renders it with errors
(URL unchanged) or redirects (PRG). Validation is the same service code the API
uses; forms.js runs the same rules in the browser first.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import strings
from app.db import get_session
from app.models import User
from app.services import users
from app.web.session import optional_user, start_session
from app.web.templating import render

router = APIRouter()


@router.get("/register")
def register_form(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    return render(request, "register.html", user, values={}, errors={})


@router.post("/register", response_model=None)
def register_submit(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(optional_user),
) -> HTMLResponse | RedirectResponse:
    values = {"name": name, "email": email}  # the password is never echoed back
    try:
        users.register(session, name, email, password)
    except users.InvalidFields as exc:
        return render(request, "register.html", user, 400, values=values, errors=exc.errors)
    except users.EmailTaken:
        errors = {"email": strings.EMAIL_TAKEN}
        return render(request, "register.html", user, 409, values=values, errors=errors)
    return RedirectResponse("/login", status_code=303)  # no auto-login


@router.get("/login")
def login_form(request: Request, user: User | None = Depends(optional_user)) -> HTMLResponse:
    return render(request, "login.html", user, values={}, errors={})


@router.post("/login", response_model=None)
def login_submit(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(optional_user),
) -> HTMLResponse | RedirectResponse:
    values = {"email": email}
    try:
        authenticated = users.authenticate(session, email, password)
    except users.InvalidFields as exc:
        return render(request, "login.html", user, 400, values=values, errors=exc.errors)
    if authenticated is None:
        context = {"values": values, "errors": {}, "form_error": strings.LOGIN_FAILED}
        return render(request, "login.html", user, 401, **context)
    response = RedirectResponse("/", status_code=303)
    start_session(response, authenticated)
    return response


@router.get("/forgot-password")
def forgot_password_form(
    request: Request, user: User | None = Depends(optional_user)
) -> HTMLResponse:
    return render(request, "forgot_password.html", user, values={}, errors={})


@router.post("/forgot-password")
def forgot_password_submit(
    request: Request,
    email: str = Form(""),
    user: User | None = Depends(optional_user),
) -> HTMLResponse:
    values = {"email": email}
    try:
        users.request_password_reset(email)
    except users.InvalidFields as exc:
        return render(request, "forgot_password.html", user, 400, values=values, errors=exc.errors)
    return render(request, "forgot_password.html", user, values=values, errors={}, sent=True)
