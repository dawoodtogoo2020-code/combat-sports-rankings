"""
Celery application for background tasks.
"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "csrankings",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Beat schedule for periodic scraping
    beat_schedule={
        "scrape-all-sources-daily": {
            "task": "app.tasks.scrape_all_sources",
            "schedule": 86400.0,  # 24 hours
        },
    },
)
