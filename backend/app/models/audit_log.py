"""
Audit logging for admin actions — tracks who did what, when, and to what.
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class AuditAction(str, enum.Enum):
    ELO_ADJUST = "elo_adjust"
    ATHLETE_MERGE = "athlete_merge"
    ATHLETE_DELETE = "athlete_delete"
    ATHLETE_CREATE = "athlete_create"
    ATHLETE_UPDATE = "athlete_update"
    ROLE_CHANGE = "role_change"
    GYM_VERIFY = "gym_verify"
    POST_MODERATE = "post_moderate"
    MATCH_VERIFY = "match_verify"
    MATCH_REJECT = "match_reject"
    IMPORT_DATA = "import_data"
    RECALCULATE = "recalculate"
    USER_BAN = "user_ban"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # athlete, match, user, gym, post
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
