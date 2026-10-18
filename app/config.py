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


@lru_cache
def get_settings() -> Settings:
    return Settings()
