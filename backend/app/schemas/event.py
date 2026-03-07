import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    sport_id: uuid.UUID | None = None
    organizer: str | None = Field(None, max_length=255)
    tier: str = Field(default="local", pattern=r"^(local|regional|national|international|elite)$")
    event_date: date
    end_date: date | None = None
    venue: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=3)
    is_gi: bool = True
    is_nogi: bool = False
    cp_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)
    k_factor_multiplier: float = Field(default=1.0, ge=0.1, le=5.0)


class EventRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    sport_id: uuid.UUID | None = None
    organizer: str | None = None
    tier: str
    event_date: date
    end_date: date | None = None
    venue: str | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    is_gi: bool
    is_nogi: bool
    cp_multiplier: float
    k_factor_multiplier: float
    source: str | None = None
    is_published: bool
    matches_imported: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EventUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    organizer: str | None = Field(None, max_length=255)
    tier: str | None = Field(None, pattern=r"^(local|regional|national|international|elite)$")
    event_date: date | None = None
    end_date: date | None = None
    venue: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    is_gi: bool | None = None
    is_nogi: bool | None = None
    cp_multiplier: float | None = Field(None, ge=0.1, le=10.0)
    k_factor_multiplier: float | None = Field(None, ge=0.1, le=5.0)
    is_published: bool | None = None
