import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False, default="male")
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Combat sport specifics
    sport_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=True)
    weight_class_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("weight_classes.id"), nullable=True)
    belt_rank_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("belt_ranks.id"), nullable=True)
    years_training: Mapped[int | None] = mapped_column(Integer, nullable=True)
    training_since: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Gym affiliation
    gym_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=True)

    # Ratings
    elo_rating: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False, index=True)
    peak_rating: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False)
    gi_rating: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False)
    nogi_rating: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False)

    # Stats
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    submissions: Mapped[int] = mapped_column(Integer, default=0)
    competitor_points: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="athlete")
    gym: Mapped["Gym"] = relationship("Gym", back_populates="athletes")
    rating_history: Mapped[list["RatingHistory"]] = relationship("RatingHistory", back_populates="athlete", order_by="RatingHistory.recorded_at")
    matches_as_winner: Mapped[list["Match"]] = relationship("Match", foreign_keys="Match.winner_id", back_populates="winner")
    matches_as_loser: Mapped[list["Match"]] = relationship("Match", foreign_keys="Match.loser_id", back_populates="loser")

    @property
    def win_rate(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return round(self.wins / self.total_matches * 100, 1)

    @property
    def age(self) -> int | None:
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
