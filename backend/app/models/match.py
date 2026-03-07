import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class MatchOutcome(str, enum.Enum):
    SUBMISSION = "submission"
    POINTS = "points"
    DECISION = "decision"
    ADVANTAGE = "advantage"
    PENALTY = "penalty"
    DQ = "dq"
    WALKOVER = "walkover"
    DRAW = "draw"
    OTHER = "other"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False, index=True)
    division_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("event_divisions.id"), nullable=True)

    # Competitors
    winner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False, index=True)
    loser_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False, index=True)

    # Outcome
    outcome: Mapped[MatchOutcome] = mapped_column(SAEnum(MatchOutcome), nullable=False)
    is_draw: Mapped[bool] = mapped_column(Boolean, default=False)
    submission_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    winner_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loser_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    match_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Match metadata
    round_name: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "Final", "Semi-Final", "Quarter"
    bracket_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_gi: Mapped[bool] = mapped_column(Boolean, default=True)
    match_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ELO changes (recorded after calculation)
    winner_elo_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    winner_elo_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    loser_elo_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    loser_elo_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    elo_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    k_factor_used: Mapped[float | None] = mapped_column(Float, nullable=True)

    # CP awarded
    winner_cp_earned: Mapped[int] = mapped_column(Integer, default=0)
    loser_cp_earned: Mapped[int] = mapped_column(Integer, default=0)

    # Source tracking
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    elo_calculated: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="matches")
    winner: Mapped["Athlete"] = relationship("Athlete", foreign_keys=[winner_id], back_populates="matches_as_winner")
    loser: Mapped["Athlete"] = relationship("Athlete", foreign_keys=[loser_id], back_populates="matches_as_loser")
