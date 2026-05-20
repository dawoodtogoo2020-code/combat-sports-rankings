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

    # JWT (our own — issued on /auth/login and /auth/supabase)
    jwt_secret_key: str = "change-me-to-a-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24h — long-lived since Supabase handles re-auth
    jwt_refresh_token_expire_days: int = 7

    # Supabase — set both to enable token-exchange auth (Google/GitHub/email sign-in)
    # SUPABASE_URL is your project URL (e.g. https://xyz.supabase.co)
    # SUPABASE_JWT_SECRET is the project's JWT secret (Settings → API → JWT Settings)
    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def fix_database_urls(self):
        """Normalize DATABASE_URL across hosts.
        Hosts give us postgresql:// (or the legacy postgres://). We need
        postgresql+asyncpg:// for async and postgresql:// for sync (alembic).
        Supabase requires sslmode=require — we add it if missing.
        """
        url = self.database_url
        # Legacy postgres:// form (older Railway, older Heroku)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        # Derive sync variant first (plain postgresql://)
        sync_url = url if "+asyncpg" not in url else url.replace("postgresql+asyncpg://", "postgresql://", 1)

        # Supabase + most managed Postgres hosts require SSL
        if ("supabase.co" in sync_url or "supabase.com" in sync_url) and "sslmode=" not in sync_url:
            sep = "&" if "?" in sync_url else "?"
            sync_url = f"{sync_url}{sep}sslmode=require"

        self.database_url_sync = sync_url
        # Async variant for SQLAlchemy + asyncpg
        async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg uses `ssl=require` not `sslmode=require` in the URL
        async_url = async_url.replace("sslmode=require", "ssl=require")
        self.database_url = async_url
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
