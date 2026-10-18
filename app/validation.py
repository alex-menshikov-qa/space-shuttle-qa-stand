"""Field rules shared by the API, the server-side forms and the JS checks.

The JS side gets the same limits, pattern and messages from client_rules(),
so the three can never disagree.
"""

import re

from app import strings

# "something@something.something" without spaces. Deliberately simple: the same
# pattern runs in the browser, so API and UI accept exactly the same emails.
EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
NAME_MAX_LENGTH = 50
EMAIL_MAX_LENGTH = 254
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128

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


# Lengths are counted in characters (code points), after normalization.


def name_error(name: str) -> str | None:
    if not name:
        return REQUIRED_MESSAGES["name"]
    if len(name) > NAME_MAX_LENGTH:
        return strings.NAME_TOO_LONG
    return None


def email_error(email: str) -> str | None:
    if not email:
        return REQUIRED_MESSAGES["email"]
    if len(email) > EMAIL_MAX_LENGTH:
        return strings.EMAIL_TOO_LONG
    if not _EMAIL_RE.match(email):
        return strings.EMAIL_INVALID
    return None


def password_error(password: str) -> str | None:
    if not password:
        return REQUIRED_MESSAGES["password"]
    if len(password) < PASSWORD_MIN_LENGTH:
        return strings.PASSWORD_INVALID
    if len(password) > PASSWORD_MAX_LENGTH:
        return strings.PASSWORD_TOO_LONG
    return None


def _collect(**checks: str | None) -> dict[str, str]:
    return {field: message for field, message in checks.items() if message}


def registration_errors(name: str, email: str, password: str) -> dict[str, str]:
    """Return {field: message} for every invalid field, in form order. Empty dict = valid.

    Expects already normalized name and email.
    """
    return _collect(name=name_error(name), email=email_error(email), password=password_error(password))


def login_errors(email: str, password: str) -> dict[str, str]:
    """Login only checks presence; anything else is just a failed login (401)."""
    return _collect(
        email=None if email else REQUIRED_MESSAGES["email"],
        password=None if password else REQUIRED_MESSAGES["password"],
    )


def email_only_errors(email: str) -> dict[str, str]:
    """Forgot-password form: the email must be a valid one."""
    return _collect(email=email_error(email))


def client_rules() -> dict:
    """Everything forms.js needs to run the same checks in the browser."""
    return {
        "emailPattern": EMAIL_PATTERN,
        "nameMax": NAME_MAX_LENGTH,
        "emailMax": EMAIL_MAX_LENGTH,
        "passwordMin": PASSWORD_MIN_LENGTH,
        "passwordMax": PASSWORD_MAX_LENGTH,
        "messages": {
            "nameRequired": strings.NAME_REQUIRED,
            "nameTooLong": strings.NAME_TOO_LONG,
            "emailRequired": strings.EMAIL_REQUIRED,
            "emailTooLong": strings.EMAIL_TOO_LONG,
            "emailInvalid": strings.EMAIL_INVALID,
            "passwordRequired": strings.PASSWORD_REQUIRED,
            "passwordInvalid": strings.PASSWORD_INVALID,
            "passwordTooLong": strings.PASSWORD_TOO_LONG,
        },
    }
