import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field


class AthleteCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str | None = Field(None, max_length=200)
    date_of_birth: date | None = None
    gender: str = Field(default="male", pattern=r"^(male|female|other)$")
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=3)
    city: str | None = Field(None, max_length=100)
    sport_id: uuid.UUID | None = None
    weight_class_id: uuid.UUID | None = None
    belt_rank_id: uuid.UUID | None = None
    years_training: int | None = Field(None, ge=0, le=60)
    gym_id: uuid.UUID | None = None
    bio: str | None = Field(None, max_length=2000)


class AthleteRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    first_name: str
    last_name: str
    display_name: str
    date_of_birth: date | None = None
    gender: str
    country: str | None = None
    country_code: str | None = None
    city: str | None = None
    photo_url: str | None = None
    bio: str | None = None
    sport_id: uuid.UUID | None = None
    weight_class_id: uuid.UUID | None = None
    belt_rank_id: uuid.UUID | None = None
    years_training: int | None = None
    gym_id: uuid.UUID | None = None
    elo_rating: float
    peak_rating: float
    gi_rating: float
    nogi_rating: float
    total_matches: int
    wins: int
    losses: int
    draws: int
    submissions: int
    competitor_points: int
    is_active: bool
    is_verified: bool
    is_claimed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AthleteUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = Field(None, pattern=r"^(male|female|other)$")
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=3)
    city: str | None = Field(None, max_length=100)
    sport_id: uuid.UUID | None = None
    weight_class_id: uuid.UUID | None = None
    belt_rank_id: uuid.UUID | None = None
    years_training: int | None = Field(None, ge=0, le=60)
    gym_id: uuid.UUID | None = None
    bio: str | None = Field(None, max_length=2000)
    photo_url: str | None = Field(None, max_length=500)


class AthleteListItem(BaseModel):
    id: uuid.UUID
    display_name: str
    country: str | None = None
    country_code: str | None = None
    gender: str
    elo_rating: float
    total_matches: int
    wins: int
    losses: int
    photo_url: str | None = None
    is_verified: bool

    model_config = {"from_attributes": True}
