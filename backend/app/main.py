import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.api.routes import api_router
from app.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)
settings = get_settings()


def _derive_sync_url():
    """Auto-derive DATABASE_URL_SYNC from DATABASE_URL for alembic."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not os.environ.get("DATABASE_URL_SYNC") and db_url:
        sync_url = db_url
        if sync_url.startswith("postgres://"):
            sync_url = sync_url.replace("postgres://", "postgresql://", 1)
        elif "asyncpg" in sync_url:
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        os.environ["DATABASE_URL_SYNC"] = sync_url
        logger.info("Auto-derived DATABASE_URL_SYNC")


def _run_migrations():
    """Run alembic migrations. Non-fatal if they fail."""
    try:
        _derive_sync_url()
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
        else:
            logger.warning(f"Migrations failed (non-fatal): {result.stderr[:300]}")
    except Exception as e:
        logger.warning(f"Could not run migrations (non-fatal): {e}")


async def _auto_seed():
    """Create tables and seed if database is empty (first deploy)."""
    import traceback
    try:
        from app.database import get_engine, get_session_factory, Base
        from sqlalchemy import text

        # Import ALL models so Base.metadata knows about them
        import app.models  # noqa — triggers model registration

        engine = get_engine()

        # Create all tables from ORM models
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

        # Check if already seeded by checking for any sport records
        session_factory = get_session_factory()
        async with session_factory() as db:
            try:
                result = await db.execute(text("SELECT COUNT(*) FROM sports"))
                count = result.scalar()
                if count and count > 0:
                    logger.info(f"Database already seeded ({count} sports found), skipping")
                    return
            except Exception:
                logger.info("Sports table empty or not queryable, will seed")

        # Run seed — import from the root-level seed.py
        logger.info("Empty database detected — running seed...")
        import importlib
        import sys
        seed_path = Path("/app/seed.py")
        if not seed_path.exists():
            seed_path = Path("seed.py")
        if seed_path.exists():
            spec = importlib.util.spec_from_file_location("seed_module", str(seed_path))
            seed_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(seed_mod)
            await seed_mod.seed()
            logger.info("Database seeded successfully!")
        else:
            logger.warning(f"seed.py not found at /app/seed.py or ./seed.py")
    except Exception as e:
        logger.error(f"Auto-seed failed: {e}\n{traceback.format_exc()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Combat Sports Rankings backend starting...")
    Path("uploads/media").mkdir(parents=True, exist_ok=True)
    _derive_sync_url()
    await _auto_seed()
    logger.info("Backend ready")
    yield
    # Shutdown
    logger.info("Backend shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Combat Sports Rankings Platform — ELO-based athlete ranking system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.app_debug:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Health check — must respond quickly, no DB dependency
@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


# API routes
app.include_router(api_router, prefix="/api/v1")

# Serve uploaded media files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
