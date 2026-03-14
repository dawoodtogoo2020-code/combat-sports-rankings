import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.athlete import Athlete
from app.models.rating import RatingHistory
from app.schemas.athlete import AthleteCreate, AthleteRead, AthleteUpdate, AthleteListItem
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.get("/", response_model=list[AthleteListItem])
@limiter.limit("30/minute")
async def list_athletes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, max_length=200),
    sport_id: uuid.UUID | None = None,
    weight_class_id: uuid.UUID | None = None,
    belt_rank_id: uuid.UUID | None = None,
    gender: str | None = Query(None, pattern=r"^(male|female|other)$"),
    country: str | None = Query(None, max_length=100),
    gym_id: uuid.UUID | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    sort_by: str = Query("elo_rating", pattern=r"^(elo_rating|total_matches|wins|display_name|created_at)$"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$"),
):
    query = select(Athlete).where(Athlete.is_active == True)

    if search:
        query = query.where(
            or_(
                Athlete.display_name.ilike(f"%{search}%"),
                Athlete.first_name.ilike(f"%{search}%"),
                Athlete.last_name.ilike(f"%{search}%"),
            )
        )
    if sport_id:
        query = query.where(Athlete.sport_id == sport_id)
    if weight_class_id:
        query = query.where(Athlete.weight_class_id == weight_class_id)
    if belt_rank_id:
        query = query.where(Athlete.belt_rank_id == belt_rank_id)
    if gender:
        query = query.where(Athlete.gender == gender)
    if country:
        query = query.where(Athlete.country == country)
    if gym_id:
        query = query.where(Athlete.gym_id == gym_id)
    if min_rating is not None:
        query = query.where(Athlete.elo_rating >= min_rating)
    if max_rating is not None:
        query = query.where(Athlete.elo_rating <= max_rating)

    # Sort
    sort_col = getattr(Athlete, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{athlete_id}", response_model=AthleteRead)
@limiter.limit("60/minute")
async def get_athlete(request: Request, athlete_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Athlete).options(selectinload(Athlete.gym)).where(Athlete.id == athlete_id)
    )
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")
    athlete.gym_name = athlete.gym.name if athlete.gym else None
    return athlete


@router.post("/", response_model=AthleteRead, status_code=status.HTTP_201_CREATED)
async def create_athlete(
    data: AthleteCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    athlete = Athlete(
        **data.model_dump(exclude_unset=True),
        display_name=data.display_name or f"{data.first_name} {data.last_name}",
    )
    db.add(athlete)
    await db.flush()
    await db.refresh(athlete)
    return athlete


@router.patch("/{athlete_id}", response_model=AthleteRead)
async def update_athlete(
    athlete_id: uuid.UUID,
    data: AthleteUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(athlete, field, value)

    await db.flush()
    await db.refresh(athlete)
    return athlete


@router.get("/{athlete_id}/matches")
@limiter.limit("30/minute")
async def get_athlete_matches(
    request: Request,
    athlete_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    """Get an athlete's match history with opponent details and event info."""
    from sqlalchemy.orm import selectinload
    from app.models.match import Match
    from app.models.event import Event

    query = (
        select(Match)
        .options(
            selectinload(Match.winner),
            selectinload(Match.loser),
            selectinload(Match.event),
        )
        .where(
            or_(Match.winner_id == athlete_id, Match.loser_id == athlete_id)
        )
        .order_by(Match.match_date.desc().nullslast())
        .limit(limit)
    )
    result = await db.execute(query)
    matches = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "event_name": m.event.name if m.event else None,
            "event_id": str(m.event_id),
            "match_date": m.match_date.isoformat() if m.match_date else None,
            "is_winner": m.winner_id == athlete_id,
            "opponent_name": m.loser.display_name if m.winner_id == athlete_id else m.winner.display_name,
            "opponent_id": str(m.loser_id) if m.winner_id == athlete_id else str(m.winner_id),
            "outcome": m.outcome.value,
            "submission_type": m.submission_type,
            "round_name": m.round_name,
            "is_gi": m.is_gi,
            "elo_change": m.elo_change if m.winner_id == athlete_id else (-m.elo_change if m.elo_change else None),
        }
        for m in matches
    ]


@router.get("/{athlete_id}/rating-history")
@limiter.limit("30/minute")
async def get_rating_history(
    request: Request,
    athlete_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    rating_type: str = Query("overall", pattern=r"^(overall|gi|nogi)$"),
    limit: int = Query(100, ge=1, le=500),
):
    result = await db.execute(
        select(RatingHistory)
        .where(
            RatingHistory.athlete_id == athlete_id,
            RatingHistory.rating_type == rating_type,
        )
        .order_by(RatingHistory.recorded_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    return [
        {
            "rating_before": h.rating_before,
            "rating_after": h.rating_after,
            "rating_change": h.rating_change,
            "recorded_at": h.recorded_at.isoformat(),
        }
        for h in reversed(history)
    ]
