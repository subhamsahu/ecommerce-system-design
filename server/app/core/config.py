from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://ecommerce:ecommerce_dev_only@localhost:5432/ecommerce"
    secret_key: str = "replace-me-in-local-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str, info):
        if info.data.get("app_env", "").lower() == "production" and (
            value == "replace-me-in-local-env" or len(value) < 32
        ):
            raise ValueError("SECRET_KEY must be a unique value of at least 32 characters in production.")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
