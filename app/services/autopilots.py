"""Autopilots: droid employees with a login, a password and a first name.

A separate entity from web accounts: no tokens, own rules, own table.
"""

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import security, validation
from app.models import Autopilot, Order


class InsufficientData(Exception):
    """A required field is missing or breaks its rule."""


class LoginTaken(Exception):
    pass


def get_by_login(session: Session, login: str) -> Autopilot | None:
    return session.scalar(select(Autopilot).where(Autopilot.login == login))


def get(session: Session, autopilot_id: int) -> Autopilot | None:
    return session.get(Autopilot, autopilot_id)


def create(session: Session, login: Any, password: Any, first_name: Any) -> Autopilot:
    """Raises InsufficientData or LoginTaken."""
    if not (
        validation.autopilot_login_valid(login)
        and validation.autopilot_password_valid(password)
        and validation.autopilot_name_valid(first_name)
    ):
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
    """
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
