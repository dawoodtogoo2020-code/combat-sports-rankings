import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.event import Event
from app.models.match import Match
from app.models.athlete import Athlete
from app.schemas.event import EventCreate, EventRead, EventUpdate
from app.schemas.match import MatchRead
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)


@router.get("/", response_model=list[EventRead])
@limiter.limit("30/minute")
async def list_events(
    request,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, max_length=200),
    sport_id: uuid.UUID | None = None,
    tier: str | None = Query(None, pattern=r"^(local|regional|national|international|elite)$"),
    country: str | None = Query(None, max_length=100),
    is_gi: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(Event).where(Event.is_published == True)

    if search:
        query = query.where(Event.name.ilike(f"%{search}%"))
    if sport_id:
        query = query.where(Event.sport_id == sport_id)
    if tier:
        query = query.where(Event.tier == tier)
    if country:
        query = query.where(Event.country == country)
    if is_gi is not None:
        query = query.where(Event.is_gi == is_gi)

    query = query.order_by(Event.event_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventRead)
@limiter.limit("60/minute")
async def get_event(request, event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    slug = slugify(data.name)
    existing = await db.execute(select(Event).where(Event.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    event = Event(**data.model_dump(exclude_unset=True), slug=slug)
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: uuid.UUID,
    data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await db.flush()
    await db.refresh(event)
    return event


@router.get("/{event_id}/matches")
@limiter.limit("30/minute")
async def get_event_matches(
    request,
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    from sqlalchemy.orm import aliased

    Winner = aliased(Athlete)
    Loser = aliased(Athlete)

    query = (
        select(Match, Winner.display_name.label("winner_name"), Loser.display_name.label("loser_name"))
        .join(Winner, Match.winner_id == Winner.id)
        .join(Loser, Match.loser_id == Loser.id)
        .where(Match.event_id == event_id)
        .order_by(Match.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()

    matches = []
    for match, winner_name, loser_name in rows:
        match_dict = MatchRead.model_validate(match).model_dump()
        match_dict["winner_name"] = winner_name
        match_dict["loser_name"] = loser_name
        matches.append(match_dict)

    return matches
