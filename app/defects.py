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
    "TRACK_NO_IMAGE": "the 'order not found' page has no picture",
    "ORDER_HOVER_VULPTEX": "in Firefox the header Order button darkens on hover",
    "TRACK_WRONG_STATION": "the status page shows the next station instead of the ordered one",
    "TRACK_PERIOD_GROUP": "the status page shows Rental Period in the third group",
    "TRACK_DATE_MINUS_DAY": "the status page shows the delivery date one day early",
    "TRACK_EMPTY_COLOR": "the status page shows 'null' for an order without a colour",
    "TRACK_EMPTY_COMMENT": "the status page shows 'undefined' for an order without a comment",
    "TRACK_NO_WRAP": "long values on the status page do not wrap",
    "STATUS_ON_SITE_SKIPPED": "the 'on site' status never comes: 'heading' lasts until 'flying'",
    "CANCELED_MODAL_FULLSCREEN": "the 'Order canceled' window is full-screen",
    "DELAYED_ONE_DAY_LATE": "an order becomes 'delayed' a day late",
    "ENDED_STATUS_4_ACTIVE": "status 4 stays highlighted after the rental has ended",
    "FORM_NAME_DASH": "the order Name rejects a hyphen",
    "FORM_LAST_NAME_16": "the order Last Name accepts 16 characters",
    "FORM_ADDRESS_REQUIRED": "the order Address may be empty",
    "FORM_ADDRESS_50": "the order Address of exactly 50 characters is rejected",
    "FORM_PHONE_12": "the order Phone of 12 characters is rejected",
    "FORM_COMMENT_CHARSET": "the order Comment accepts any characters",
    "FORM_COMMENT_LENGTH": "the order Comment has no length limit",
    "FORM_DATE_TODAY": "today is accepted as the delivery date",
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
