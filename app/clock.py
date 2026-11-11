"""The stand's clock.

Days are counted in STAND_TZ. Every order also has its own clock
(now + the order's offset), which the testing hook can move forward so that
time-dependent statuses are reachable without waiting.
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.config import get_settings


def tz() -> ZoneInfo:
    return ZoneInfo(get_settings().stand_tz)


def now() -> datetime:
    return datetime.now(UTC)


def today() -> date:
    return now().astimezone(tz()).date()


def tomorrow() -> date:
    return today() + timedelta(days=1)


def end_of_day(day: date) -> datetime:
    """The first moment after `day` in STAND_TZ (i.e. 23:59:59 has passed)."""
    return datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz())
