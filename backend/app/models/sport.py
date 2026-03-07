import uuid
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    weight_classes: Mapped[list["WeightClass"]] = relationship("WeightClass", back_populates="sport")
    belt_ranks: Mapped[list["BeltRank"]] = relationship("BeltRank", back_populates="sport")


class WeightClass(Base):
    __tablename__ = "weight_classes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    min_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False, default="male")
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    sport: Mapped["Sport"] = relationship("Sport", back_populates="weight_classes")


class BeltRank(Base):
    __tablename__ = "belt_ranks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)

    sport: Mapped["Sport"] = relationship("Sport", back_populates="belt_ranks")
