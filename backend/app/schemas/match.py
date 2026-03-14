import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MatchCreate(BaseModel):
    event_id: uuid.UUID
    division_id: uuid.UUID | None = None
    winner_id: uuid.UUID
    loser_id: uuid.UUID
    outcome: str = Field(pattern=r"^(submission|points|decision|advantage|penalty|dq|walkover|draw|other)$")
    is_draw: bool = False
    submission_type: str | None = Field(None, max_length=100)
    winner_score: int | None = Field(None, ge=0)
    loser_score: int | None = Field(None, ge=0)
    match_duration_seconds: int | None = Field(None, ge=0)
    round_name: str | None = Field(None, max_length=50)
    bracket_position: int | None = None
    is_gi: bool = True
    match_date: datetime | None = None


class MatchRead(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    division_id: uuid.UUID | None = None
    winner_id: uuid.UUID
    loser_id: uuid.UUID
    winner_name: str | None = None
    loser_name: str | None = None
    outcome: str
    is_draw: bool
    submission_type: str | None = None
    winner_score: int | None = None
    loser_score: int | None = None
    match_duration_seconds: int | None = None
    round_name: str | None = None
    bracket_position: int | None = None
    is_gi: bool
    match_date: datetime | None = None
    winner_elo_before: float | None = None
    winner_elo_after: float | None = None
    loser_elo_before: float | None = None
    loser_elo_after: float | None = None
    elo_change: float | None = None
    k_factor_used: float | None = None
    winner_cp_earned: int
    loser_cp_earned: int
    is_verified: bool
    verification_status: str = "pending"
    elo_calculated: bool
    created_at: datetime

    model_config = {"from_attributes": True}
