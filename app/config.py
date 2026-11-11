"""Application settings, read from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Assembled in docker-compose.yml from the POSTGRES_* variables.
    database_url: str

    jwt_secret: str
    access_token_expire_minutes: int = 60

    # Test user seeded on every start; the test suites read the same variables.
    test_name: str = "Test User"
    test_email: str
    test_password: str

    # Password of every seeded fleet autopilot (app/data/fleet.json).
    fleet_password: str = "0101"

    # Time zone in which the stand counts days: "tomorrow" for a delivery date,
    # the end of the delivery day, the dates shown on pages.
    stand_tz: str = "UTC"
    # Minutes between "Autopilot is on site" (finish) and "Okay, let's fly now".
    pickup_minutes: int = 10
    # Switches on /api/v1/testing/* (per-order time shift). Off by default.
    test_hooks: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
