from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _create_engine():
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.app_debug,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )


def _create_session_factory(eng):
    return async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)


# Lazy init — created on first use
_engine = None
_async_session = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = _create_engine()
    return _engine


def get_session_factory():
    global _async_session
    if _async_session is None:
        _async_session = _create_session_factory(get_engine())
    return _async_session


# Keep these as module-level aliases for backward compat in seed.py etc.
@property
def engine():
    return get_engine()


@property
def async_session():
    return get_session_factory()


async def get_db() -> AsyncSession:
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
