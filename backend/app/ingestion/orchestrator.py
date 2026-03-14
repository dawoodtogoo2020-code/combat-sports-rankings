"""
Scrape orchestrator — coordinates scraping across all sources.
Handles logging, error recovery, and import pipeline.
"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.import_service import ImportService
from app.ingestion.scrapers import (
    SmoothCompIngester,
    AjpIngester,
    IbjjfIngester,
    NagaIngester,
    GrapplingIndustriesIngester,
    AdccIngester,
)
from app.models.data_source import DataSource
from app.models.scrape_log import ScrapeLog

logger = logging.getLogger(__name__)

INGESTER_MAP = {
    "smoothcomp": SmoothCompIngester,
    "ajp": AjpIngester,
    "ibjjf": IbjjfIngester,
    "naga": NagaIngester,
    "grappling-industries": GrapplingIndustriesIngester,
    "adcc": AdccIngester,
}


class ScrapeOrchestrator:
    """Coordinates scraping runs across multiple sources."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.import_service = ImportService()

    async def run_all(self) -> dict:
        """Run scraping for all active data sources."""
        result = await self.db.execute(
            select(DataSource).where(DataSource.is_active == True)
        )
        sources = result.scalars().all()

        summary = {
            "sources_attempted": 0,
            "sources_succeeded": 0,
            "sources_failed": 0,
            "total_events": 0,
            "total_matches": 0,
            "total_athletes_created": 0,
            "errors": [],
        }

        for source in sources:
            source_result = await self.run_source(source.slug)
            summary["sources_attempted"] += 1
            if source_result.get("status") == "completed":
                summary["sources_succeeded"] += 1
                summary["total_events"] += source_result.get("events_found", 0)
                summary["total_matches"] += source_result.get("matches_imported", 0)
                summary["total_athletes_created"] += source_result.get("athletes_created", 0)
            else:
                summary["sources_failed"] += 1
                summary["errors"].append({
                    "source": source.slug,
                    "error": source_result.get("error", "unknown"),
                })

        return summary

    async def run_source(self, source_slug: str) -> dict:
        """Run scraping for a single source."""
        ingester_cls = INGESTER_MAP.get(source_slug)
        if not ingester_cls:
            return {"status": "failed", "error": f"Unknown source: {source_slug}"}

        # Find data source record
        result = await self.db.execute(
            select(DataSource).where(DataSource.slug == source_slug)
        )
        data_source = result.scalar_one_or_none()

        # Create scrape log
        log = ScrapeLog(
            data_source_id=data_source.id if data_source else None,
            status="running",
        )
        self.db.add(log)
        await self.db.flush()

        try:
            async with ScraperHttpClient() as http:
                ingester = ingester_cls(http)

                # Fetch events
                events = await ingester.fetch_events()
                log.events_found = len(events)
                logger.info(f"[{source_slug}] Found {len(events)} events")

                total_matches = 0
                total_athletes = 0

                for event in events:
                    # If event has no matches yet, fetch results
                    if not event.matches and event.source_id:
                        detailed = await ingester.fetch_event_results(event.source_id)
                        if detailed:
                            event = detailed

                    if not event.matches:
                        continue

                    # Import into database
                    try:
                        stats = await self.import_service.import_event(self.db, event)
                        total_matches += stats.get("matches_created", 0)
                        total_athletes += stats.get("athletes_created", 0)
                    except Exception as e:
                        logger.error(f"[{source_slug}] Failed to import event '{event.name}': {e}")

                log.matches_imported = total_matches
                log.athletes_created = total_athletes
                log.status = "completed"
                log.completed_at = datetime.utcnow()

                # Update data source last sync
                if data_source:
                    data_source.last_sync_at = datetime.utcnow()

                await self.db.commit()

                return {
                    "status": "completed",
                    "source": source_slug,
                    "events_found": len(events),
                    "matches_imported": total_matches,
                    "athletes_created": total_athletes,
                }

        except Exception as e:
            log.status = "failed"
            log.completed_at = datetime.utcnow()
            log.errors = {"message": str(e)}
            await self.db.commit()

            logger.error(f"[{source_slug}] Scraping failed: {e}")
            return {"status": "failed", "source": source_slug, "error": str(e)}
