"""Field rules shared by the API, the server-side forms and the JS checks.

The JS side gets the same limits, pattern and messages from client_rules(),
so the three can never disagree.
"""

import re
from datetime import date
from typing import Any

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
        "order": {
            "namePattern": ORDER_NAME_PATTERN,
            "lastNamePattern": ORDER_LAST_NAME_PATTERN,
            "addressPattern": ORDER_ADDRESS_PATTERN,
            "phonePattern": ORDER_PHONE_PATTERN,
            "commentPattern": ORDER_COMMENT_PATTERN,
            "messages": {
                "firstName": strings.ORDER_NAME_INVALID,
                "lastName": strings.ORDER_LAST_NAME_INVALID,
                "address": strings.ORDER_ADDRESS_INVALID,
                "station": strings.ORDER_STATION_INVALID,
                "phone": strings.ORDER_PHONE_INVALID,
                "deliveryDate": strings.ORDER_DATE_INVALID,
                "rentTime": strings.ORDER_PERIOD_INVALID,
                "comment": strings.ORDER_COMMENT_INVALID,
                "submitFailed": strings.ORDER_SUBMIT_FAILED,
            },
        },
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


# --- Autopilots (API only) ---------------------------------------------------
# "Aurebesh" letters are Latin letters. Values must be JSON strings: a number
# or null is invalid even if it would look right as text.

AUTOPILOT_LOGIN_PATTERN = r"^[A-Za-z]{2,10}$"
AUTOPILOT_PASSWORD_PATTERN = r"^[0-9]{4}$"
AUTOPILOT_NAME_PATTERN = r"^[A-Za-z]{2,10}$"


def _matches(pattern: str, value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def autopilot_login_valid(value: Any) -> bool:
    return _matches(AUTOPILOT_LOGIN_PATTERN, value)


def autopilot_password_valid(value: Any) -> bool:
    return _matches(AUTOPILOT_PASSWORD_PATTERN, value)


def autopilot_name_valid(value: Any) -> bool:
    return _matches(AUTOPILOT_NAME_PATTERN, value)


# --- Orders (API and the order form) ------------------------------------------

ORDER_NAME_PATTERN = r"^[A-Za-z -]{2,15}$"
ORDER_LAST_NAME_PATTERN = r"^[A-Za-z]{2,15}$"
ORDER_ADDRESS_PATTERN = r"^[A-Za-z0-9 .,-]{5,50}$"
ORDER_PHONE_PATTERN = r"^[0-9+]{10,12}$"
ORDER_COMMENT_PATTERN = r"^[A-Za-z .,-]{0,24}$"
RENT_TIME_MIN = 1
RENT_TIME_MAX = 7
ORDER_COLORS = ("PINKY_SWEAR", "GRAY_RAINBOW")


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def parse_delivery_date(value: Any) -> date | None:
    """A strict YYYY-MM-DD string -> date, anything else -> None."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def order_errors(data: dict[str, Any], station_numbers: set[int], tomorrow: date) -> dict[str, str]:
    """Return {field: message} for every invalid order field, in form order.

    Expects the address already trimmed. `comment` and `color` are optional
    (missing, null, "" / [] all mean "none").
    """
    delivery_date = parse_delivery_date(data.get("deliveryDate"))
    comment = data.get("comment")
    color = data.get("color")
    return _collect(
        firstName=None
        if _matches(ORDER_NAME_PATTERN, data.get("firstName"))
        else strings.ORDER_NAME_INVALID,
        lastName=None
        if _matches(ORDER_LAST_NAME_PATTERN, data.get("lastName"))
        else strings.ORDER_LAST_NAME_INVALID,
        address=None
        if _matches(ORDER_ADDRESS_PATTERN, data.get("address"))
        else strings.ORDER_ADDRESS_INVALID,
        station=None
        if _is_int(data.get("station")) and data["station"] in station_numbers
        else strings.ORDER_STATION_INVALID,
        phone=None
        if _matches(ORDER_PHONE_PATTERN, data.get("phone"))
        else strings.ORDER_PHONE_INVALID,
        deliveryDate=None
        if delivery_date is not None and delivery_date >= tomorrow
        else strings.ORDER_DATE_INVALID,
        rentTime=None
        if _is_int(data.get("rentTime")) and RENT_TIME_MIN <= data["rentTime"] <= RENT_TIME_MAX
        else strings.ORDER_PERIOD_INVALID,
        color=None
        if color is None
        or (
            isinstance(color, list)
            and all(isinstance(item, str) and item in ORDER_COLORS for item in color)
            and len(set(color)) == len(color)
        )
        else strings.ORDER_COLOR_INVALID,
        comment=None
        if comment is None or _matches(ORDER_COMMENT_PATTERN, comment)
        else strings.ORDER_COMMENT_INVALID,
    )
