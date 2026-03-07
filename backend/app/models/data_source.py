"""
Source registry for tracking ingestion data sources and their compliance status.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ingestion method
    ingestion_method: Mapped[str] = mapped_column(String(50), default="csv")  # api, csv, manual, html

    # Compliance tracking
    robots_txt_status: Mapped[str] = mapped_column(String(20), default="unknown")  # allowed, disallowed, unknown
    robots_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tos_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    tos_allows_scraping: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tos_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    compliance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Parser
    parser_module: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parser_version: Mapped[str] = mapped_column(String(20), default="1.0.0")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
