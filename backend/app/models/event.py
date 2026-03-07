import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Date, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class EventTier(str, enum.Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"
    ELITE = "elite"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sport_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=True)
    organizer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tier: Mapped[EventTier] = mapped_column(SAEnum(EventTier), default=EventTier.LOCAL, nullable=False)

    # When/where
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(3), nullable=True)

    # Type
    is_gi: Mapped[bool] = mapped_column(Boolean, default=True)
    is_nogi: Mapped[bool] = mapped_column(Boolean, default=False)

    # Competition points multiplier
    cp_multiplier: Mapped[float] = mapped_column(Float, default=1.0)

    # K-factor multiplier for ELO
    k_factor_multiplier: Mapped[float] = mapped_column(Float, default=1.0)

    # Source tracking
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "smoothcomp", "ajp", "manual"
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    matches_imported: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    divisions: Mapped[list["EventDivision"]] = relationship("EventDivision", back_populates="event")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="event")


class EventDivision(Base):
    __tablename__ = "event_divisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_class_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("weight_classes.id"), nullable=True)
    belt_rank_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("belt_ranks.id"), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), default="male")
    age_division: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_gi: Mapped[bool] = mapped_column(Boolean, default=True)
    competitor_count: Mapped[int] = mapped_column(Integer, default=0)

    event: Mapped["Event"] = relationship("Event", back_populates="divisions")
