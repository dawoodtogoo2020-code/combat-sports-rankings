import uuid
from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    athlete_id: uuid.UUID
    display_name: str
    country: str | None = None
    country_code: str | None = None
    gender: str
    elo_rating: float
    total_matches: int
    wins: int
    losses: int
    win_rate: float
    photo_url: str | None = None
    gym_name: str | None = None
    belt_rank: str | None = None
    rating_change_7d: float | None = None
    rating_change_30d: float | None = None


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    total_count: int
    page: int
    page_size: int
    filters_applied: dict = {}
