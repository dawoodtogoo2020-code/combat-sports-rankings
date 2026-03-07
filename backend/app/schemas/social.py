import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    post_type: str = Field(default="general", pattern=r"^(result|medal|video|tournament|training|general)$")
    content: str = Field(min_length=1, max_length=5000)
    media_urls: list[str] | None = None
    hashtags: list[str] | None = None
    event_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None


class PostRead(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str | None = None
    author_avatar: str | None = None
    post_type: str
    content: str
    media_urls: list[str] | None = None
    hashtags: list[str] | None = None
    event_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    like_count: int
    comment_count: int
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    parent_id: uuid.UUID | None = None


class CommentRead(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str | None = None
    author_avatar: str | None = None
    parent_id: uuid.UUID | None = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
