"""Account operations. The JSON API and the web pages both go through here,
so validation and normalization are identical in both."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import security, validation
from app.models import User


class InvalidFields(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors  # {field: message}, in form order

    @property
    def first_message(self) -> str:
        return next(iter(self.errors.values()))


class EmailTaken(Exception):
    pass


def get_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == validation.normalize_email(email)))


def register(session: Session, name: str, email: str, password: str) -> User:
    """Validate, then create the user. Raises InvalidFields or EmailTaken."""
    name = validation.normalize_name(name)
    email = validation.normalize_email(email)
    errors = validation.registration_errors(name, email, password)
    if errors:
        raise InvalidFields(errors)
    if get_by_email(session, email) is not None:
        raise EmailTaken
    user = User(name=name, email=email, password_hash=security.hash_password(password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:  # a concurrent registration won the race
        session.rollback()
        raise EmailTaken from None
    return user


def authenticate(session: Session, email: str, password: str) -> User | None:
    """Return the user for a correct email/password pair, otherwise None.

    Raises InvalidFields if a field is empty. Wrong password and unknown email
    are indistinguishable to the caller.
    """
    email = validation.normalize_email(email)
    errors = validation.login_errors(email, password)
    if errors:
        raise InvalidFields(errors)
    user = get_by_email(session, email)
    if not security.verify_password(user.password_hash if user else None, password):
        return None
    return user


def request_password_reset(email: str) -> None:
    """Validate the email. Nothing is sent: the stand has no mail delivery.

    Raises InvalidFields. The result never reveals whether the email is registered.
    """
    errors = validation.email_only_errors(validation.normalize_email(email))
    if errors:
        raise InvalidFields(errors)


def get_by_token(session: Session, token: str) -> User | None:
    user_id = security.decode_access_token(token)
    return session.get(User, user_id) if user_id is not None else None


def delete(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()
