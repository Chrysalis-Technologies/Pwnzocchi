from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    adapter_id: str = Field(..., env="ADAPTER_ID")
    data_dir: str = Field("./captures", env="DATA_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
