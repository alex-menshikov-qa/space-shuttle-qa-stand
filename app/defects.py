"""Seeded defects: intentional, switchable bugs for test-automation practice.

Every defect is registered in KNOWN_DEFECTS and switched on with the env
variable BUG_<NAME>=1 (also accepted: true / yes / on). All defects are off by
default. Each one is documented in the "Known defects" table in README.md.

Usage at the place where the bug lives:

    if defects.is_enabled("SOME_NAME"):
        ...  # buggy behaviour
"""

import os

ENV_PREFIX = "BUG_"
_TRUTHY = {"1", "true", "yes", "on"}

# name -> one-line description (keep in sync with README.md)
KNOWN_DEFECTS: dict[str, str] = {}


def is_enabled(name: str) -> bool:
    """Return True if the defect is switched on. Unknown names fail loudly."""
    if name not in KNOWN_DEFECTS:
        raise KeyError(f"Unknown seeded defect: {name!r}")
    return os.getenv(ENV_PREFIX + name, "").strip().lower() in _TRUTHY


def enabled_defects() -> list[str]:
    return sorted(name for name in KNOWN_DEFECTS if is_enabled(name))


def unknown_flags() -> list[str]:
    """BUG_* variables that match no registered defect (most likely typos)."""
    return sorted(
        key
        for key in os.environ
        if key.startswith(ENV_PREFIX) and key[len(ENV_PREFIX) :] not in KNOWN_DEFECTS
    )
