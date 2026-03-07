import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class GymCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    website: str | None = Field(None, max_length=500)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=3)


class GymRead(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID | None = None
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    country_code: str | None = None
    member_count: int
    avg_rating: float
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GymUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    website: str | None = Field(None, max_length=500)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=3)
    logo_url: str | None = Field(None, max_length=500)
