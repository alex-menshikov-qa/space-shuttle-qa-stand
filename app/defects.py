"""Seeded defects: intentional, switchable bugs for test-automation practice.

Every defect is registered in KNOWN_DEFECTS and switched on with the env
variable BUG_<NAME>=1 (also accepted: true / yes / on). All defects are off by
default. Each one is documented in the "Known defects" table in README.md.

A typo must never silently disable a defect, so check_flags() (called on app
startup) rejects BUG_* variables with an unknown name or an unrecognised value,
and is_enabled() rejects unknown names.

Usage at the place where the bug lives:

    if defects.is_enabled("SOME_NAME"):
        ...  # buggy behaviour
"""

import os

ENV_PREFIX = "BUG_"
_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"", "0", "false", "no", "off"}

# name -> one-line description (keep in sync with README.md)
KNOWN_DEFECTS: dict[str, str] = {
    "AUTOPILOT_LOGIN_RULES": "POST /autopilot accepts a login that breaks the rules",
    "AUTOPILOT_PASSWORD_RULES": "POST /autopilot accepts a password that breaks the rules",
    "AUTOPILOT_NAME_RULES": "POST /autopilot accepts a firstName that breaks the rules",
    "MISSING_NAME_409": "POST /autopilot without firstName answers 409 instead of 400",
    "LOGIN_NO_PASSWORD_504": "POST /autopilot/login without password answers 504 instead of 400",
    "TRACK_DELETED_AUTOPILOT": "an order of a deleted autopilot is still found by track",
    "CANCELED_ORDER_VISIBLE": "a canceled order is still found by track",
    "STATUS_SEARCH_ENTER": "Enter does not start the order search in the header",
    "HEADER_SEARCH_PLACEHOLDER": "the header order search has the wrong placeholder",
    "HEADER_SEARCH_EXTRA_BUTTON": "the header order search has an extra 'Go!' button",
    "TRACK_IMAGE_NO_RUNWAY": "the 'order not found' picture has no runway",
    "ORDER_HOVER_VULPTEX": "in Firefox the header Order button does not react to hover",
    "TRACK_WRONG_STATION": "the status page shows the next station instead of the ordered one",
    "TRACK_DATE_LABEL": "the status page captions the delivery date 'Delivery Date'",
    "TRACK_DATE_PLUS_DAY": "the status page shows the delivery date one day late",
    "TRACK_EMPTY_COLOR": "the status page shows 'any' for an order without a colour",
    "TRACK_EMPTY_COMMENT": "the status page has no comment row for an order without a comment",
    "TRACK_AUTOPILOT_NAME_TRUNCATED": "the status page cuts a long autopilot name to two letters",
    "TRACK_CANCEL_HIDDEN_ON_ACCEPT": "'Cancel order' disappears once an autopilot accepts the order",
    "TRACK_NO_WRAP": "long values on the status page do not wrap",
    "STATUS_ON_SITE_SKIPPED": "the 'on site' status never comes: 'heading' lasts until 'flying'",
    "CANCELED_MODAL_FULLSCREEN": "the 'Order canceled' window is full-screen",
    "DELAYED_ONE_DAY_EARLY": "an order becomes 'delayed' a day early",
    "ENDED_STATUS_4_CAPTION": "the caption of status 4 changes after the rental has ended",
    "FORM_NAME_DASH": "the order Name rejects a hyphen",
    "FORM_LAST_NAME_16": "the order Last Name accepts 16 characters",
    "FORM_ADDRESS_REQUIRED": "the order Address may be empty",
    "FORM_ADDRESS_50": "the order Address of exactly 50 characters is rejected",
    "FORM_PHONE_10": "the order Phone of 10 characters is rejected",
    "FORM_PHONE_13": "the order Phone accepts 13 characters",
    "FORM_COMMENT_CHARSET": "the order Comment accepts any characters",
    "FORM_COMMENT_LENGTH": "the order Comment has no length limit",
    "FORM_DATE_PAST": "today and past dates are accepted as the delivery date",
    "FORM_CONFIRM_YES_DEAD": "'Yes' in the order confirmation window does nothing",
    "FORM_DATE_PICK_NO_HIGHLIGHT": "the date field is not highlighted after a day is picked",
    "FORM_STATION_HOVER": "the order Shuttle Station field turns blue on hover",
    "FORM_TYPING_BORDER": "order field borders turn black as soon as typing starts",
    "FORM_NEXT_LABEL": "the order form button reads 'Continue' instead of 'Next'",
    "FORM_STATION_PLACEHOLDER_DARK": "the Shuttle Station placeholder is dark gray",
    "FORM_COLOR_UNTICKED_BLACK": "the unticked shuttle colour turns black when the other is ticked",
    "FORM_CALENDAR_LOWERCASE": "month and weekday names in the calendar are in lowercase",
    "FORM_CALENDAR_BLACK": "all text in the calendar is black",
    "FORM_PERIOD_LIST_NARROW": "the Rental Period list is narrower than the field",
    "FORM_ERROR_LAYOUT_SHIFT": "an error text under an order field pushes the form down",
    "ADD_BUTTON_STALE_TOTAL": "the shipyard Add button does not update the total",
}


class DefectFlagError(RuntimeError):
    """A BUG_* variable is misspelled or has a value that is neither on nor off."""


def is_enabled(name: str) -> bool:
    """Return True if the defect is switched on. Unknown names fail loudly."""
    if name not in KNOWN_DEFECTS:
        raise DefectFlagError(f"Unknown seeded defect: {name!r}")
    return os.getenv(ENV_PREFIX + name, "").strip().lower() in _TRUTHY


def enabled_defects() -> list[str]:
    return sorted(name for name in KNOWN_DEFECTS if is_enabled(name))


def check_flags() -> None:
    """Raise DefectFlagError listing every invalid BUG_* variable in the environment."""
    problems = []
    for key in sorted(os.environ):
        if not key.startswith(ENV_PREFIX):
            continue
        value = os.environ[key].strip().lower()
        if key[len(ENV_PREFIX) :] not in KNOWN_DEFECTS:
            problems.append(f"{key}: no such seeded defect")
        elif value not in _TRUTHY | _FALSY:
            problems.append(f"{key}={os.environ[key]!r}: use 1/true/yes/on or 0/false/no/off")
    if problems:
        known = ", ".join(ENV_PREFIX + name for name in sorted(KNOWN_DEFECTS)) or "none"
        raise DefectFlagError(
            "Invalid seeded-defect flags: "
            + "; ".join(problems)
            + f". Known flags: {known}. Fix or remove them in .env."
        )
