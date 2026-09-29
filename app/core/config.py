"""Load application and SMTP settings from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App + default SMTP credentials (can be overridden via API)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SMTP Test Server"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_from_email: str = ""
    smtp_from_name: str = "SMTP Test Server"


@lru_cache
def get_settings() -> Settings:
    return Settings()
