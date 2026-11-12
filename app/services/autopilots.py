"""Autopilots: droid employees with a login, a password and a first name.

A separate entity from web accounts: no tokens, own rules, own table.
"""

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import defects, security, validation
from app.models import Autopilot, Order


class InsufficientData(Exception):
    """A required field is missing or breaks its rule."""


class LoginTaken(Exception):
    pass


class Crashed(Exception):
    """Seeded defect AUTOPILOT_LOGIN_RULES: a boolean login breaks the service."""


class Unavailable(Exception):
    """Seeded defect LOGIN_NO_PASSWORD_504: the service "times out"."""


def get_by_login(session: Session, login: str) -> Autopilot | None:
    return session.scalar(select(Autopilot).where(Autopilot.login == login))


def get(session: Session, autopilot_id: int) -> Autopilot | None:
    return session.get(Autopilot, autopilot_id)


def _loose(value: Any) -> str | None:
    """What a "rules are not checked" defect lets through: any string with
    something in it besides whitespace, a number or a boolean (stored as its
    JSON text: 1234 -> "1234", true -> "true"). Missing, null, empty and
    whitespace-only values stay invalid, as they were in 2023."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return value if isinstance(value, str) and value.strip() else None


def _field(value: Any, valid: bool, defect: str) -> str | None:
    """The value to store, or None if it must be rejected."""
    if valid:
        return value
    return _loose(value) if defects.is_enabled(defect) else None


def create(session: Session, login: Any, password: Any, first_name: Any) -> Autopilot:
    """Raises InsufficientData or LoginTaken (and Crashed, with a seeded defect)."""
    if first_name is None and defects.is_enabled("MISSING_NAME_409"):
        raise LoginTaken  # seeded defect: the wrong error for a missing firstName
    if isinstance(login, bool) and defects.is_enabled("AUTOPILOT_LOGIN_RULES"):
        raise Crashed  # seeded defect, SSI-39: no 400, and nobody is registered
    login = _field(login, validation.autopilot_login_valid(login), "AUTOPILOT_LOGIN_RULES")
    password = _field(
        password, validation.autopilot_password_valid(password), "AUTOPILOT_PASSWORD_RULES"
    )
    first_name = _field(
        first_name, validation.autopilot_name_valid(first_name), "AUTOPILOT_NAME_RULES"
    )
    if login is None or password is None or first_name is None:
        raise InsufficientData
    if get_by_login(session, login) is not None:
        raise LoginTaken
    autopilot = Autopilot(
        login=login, password_hash=security.hash_password(password), first_name=first_name
    )
    session.add(autopilot)
    try:
        session.commit()
    except IntegrityError:  # a concurrent request took the login
        session.rollback()
        raise LoginTaken from None
    return autopilot


def authenticate(session: Session, login: Any, password: Any) -> Autopilot | None:
    """The autopilot for a correct login/password pair, otherwise None.

    Raises InsufficientData if either field is missing, empty or not a string.
    Autopilots created through a rules defect log in with the text of what
    was sent (the number 1234 as "1234").
    """
    if password in (None, "") and defects.is_enabled("LOGIN_NO_PASSWORD_504"):
        raise Unavailable
    if not (isinstance(login, str) and login and isinstance(password, str) and password):
        raise InsufficientData
    autopilot = get_by_login(session, login)
    if not security.verify_password(autopilot.password_hash if autopilot else None, password):
        return None
    return autopilot


def delete(session: Session, autopilot: Autopilot) -> None:
    """Hard delete (the login becomes free). The autopilot's orders stay in
    the table, flagged, and are no longer found by track or listed."""
    session.execute(
        update(Order).where(Order.autopilot_id == autopilot.id).values(autopilot_deleted=True)
    )
    session.delete(autopilot)
    session.commit()
