"""Application settings, read from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Assembled in docker-compose.yml from the POSTGRES_* variables.
    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
