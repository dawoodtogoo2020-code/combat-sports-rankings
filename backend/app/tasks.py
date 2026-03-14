"""
Celery tasks for background data ingestion.
"""

import asyncio
import logging

from app.celery_app import celery_app
from app.database import get_session_factory
from app.ingestion.orchestrator import ScrapeOrchestrator

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.scrape_all_sources", bind=True, max_retries=2)
def scrape_all_sources(self):
    """Scrape all active data sources."""
    logger.info("Starting scheduled scrape of all sources")

    async def _run():
        session_factory = get_session_factory()
        async with session_factory() as db:
            orchestrator = ScrapeOrchestrator(db)
            return await orchestrator.run_all()

    try:
        result = _run_async(_run())
        logger.info(f"Scrape completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Scrape all sources failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.scrape_source", bind=True, max_retries=2)
def scrape_source(self, source_slug: str):
    """Scrape a single data source."""
    logger.info(f"Starting scrape for source: {source_slug}")

    async def _run():
        session_factory = get_session_factory()
        async with session_factory() as db:
            orchestrator = ScrapeOrchestrator(db)
            return await orchestrator.run_source(source_slug)

    try:
        result = _run_async(_run())
        logger.info(f"Scrape for {source_slug} completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Scrape for {source_slug} failed: {exc}")
        raise self.retry(exc=exc, countdown=300)
