from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration shared by the API and Alembic.

    The aliases retain compatibility with the earlier environment names while
    making the documented Phase 0 contract the source of truth.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_name: str = Field(default="ecommerce-system-design", validation_alias="APP_NAME")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+psycopg2://labadmin:root123@localhost:5432/ecommerce",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(
        default="development-only-secret-change-before-production",
        validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"),
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias=AliasChoices("ACCESS_TOKEN_TTL_MINUTES", "ACCESS_TOKEN_EXPIRE_MINUTES"),
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"], validation_alias="CORS_ORIGINS")

    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production() and settings.jwt_secret == "development-only-secret-change-before-production":
        raise RuntimeError("JWT_SECRET must be set to a non-default value in production")
    return settings
