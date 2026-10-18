"""Field rules shared by the API and the web forms (and rendered into the JS checks)."""

import re

from app import strings

# "something@something.something" without spaces. Deliberately simple: the same
# pattern runs in the browser, so API and UI accept exactly the same emails.
EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
PASSWORD_MIN_LENGTH = 6

_EMAIL_RE = re.compile(EMAIL_PATTERN)

# A missing field gets the same message as an empty one.
REQUIRED_MESSAGES = {
    "name": strings.NAME_REQUIRED,
    "email": strings.EMAIL_REQUIRED,
    "password": strings.PASSWORD_REQUIRED,
}


def normalize_name(name: str) -> str:
    return name.strip()


def normalize_email(email: str) -> str:
    """Applied on register AND login, so emails compare case-insensitively."""
    return email.strip().lower()


def registration_errors(name: str, email: str, password: str) -> dict[str, str]:
    """Return {field: message} for every invalid field, in form order. Empty dict = valid.

    Expects already normalized name and email.
    """
    errors = {}
    if not name:
        errors["name"] = REQUIRED_MESSAGES["name"]
    if not email:
        errors["email"] = REQUIRED_MESSAGES["email"]
    elif not _EMAIL_RE.match(email):
        errors["email"] = strings.EMAIL_INVALID
    if not password:
        errors["password"] = REQUIRED_MESSAGES["password"]
    elif len(password) < PASSWORD_MIN_LENGTH:
        errors["password"] = strings.PASSWORD_INVALID
    return errors


def login_errors(email: str, password: str) -> dict[str, str]:
    """Login only checks presence; a wrong format is just a failed login (401)."""
    errors = {}
    if not email:
        errors["email"] = REQUIRED_MESSAGES["email"]
    if not password:
        errors["password"] = REQUIRED_MESSAGES["password"]
    return errors
