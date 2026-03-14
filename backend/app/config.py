from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "CS Rankings"
    app_env: str = "development"
    app_debug: bool = False
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    port: int = 8000

    # Database — Railway provides DATABASE_URL as postgresql://
    # We auto-derive the asyncpg and sync variants
    database_url: str = "postgresql+asyncpg://csrankings:csrankings@localhost:5432/csrankings"
    database_url_sync: str = "postgresql://csrankings:csrankings@localhost:5432/csrankings"

    # Redis (optional in production — scraping works without it)
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def fix_database_urls(self):
        """Auto-convert DATABASE_URL from Railway format.
        Railway gives postgresql://, we need postgresql+asyncpg:// for async
        and postgresql:// for sync (alembic).
        """
        url = self.database_url
        # If Railway gave us a plain postgresql:// URL, derive both variants
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            self.database_url_sync = url
            self.database_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            # Older Railway format
            self.database_url_sync = url.replace("postgres://", "postgresql://", 1)
            self.database_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
