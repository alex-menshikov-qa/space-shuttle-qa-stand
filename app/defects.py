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
KNOWN_DEFECTS: dict[str, str] = {}


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
