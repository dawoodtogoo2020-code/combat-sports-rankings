import uuid
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.athlete import Athlete
from app.models.gym import Gym
from app.models.match import Match, VerificationStatus
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.get("/global", response_model=LeaderboardResponse)
@limiter.limit("30/minute")
async def global_leaderboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sport_id: uuid.UUID | None = None,
    weight_class_id: uuid.UUID | None = None,
    belt_rank_id: uuid.UUID | None = None,
    gender: str | None = Query(None, pattern=r"^(male|female|other)$"),
    country: str | None = Query(None, max_length=100),
    is_gi: bool | None = None,
    min_matches: int = Query(1, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(Athlete).where(
        Athlete.is_active == True,
        Athlete.total_matches >= min_matches,
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

    # Determine sort column based on gi/nogi filter
    if is_gi is True:
        sort_col = Athlete.gi_rating
    elif is_gi is False:
        sort_col = Athlete.nogi_rating
    else:
        sort_col = Athlete.elo_rating

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # Fetch page
    query = query.order_by(sort_col.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    athletes = result.scalars().all()

    # Build entries with rank
    start_rank = (page - 1) * page_size + 1
    entries = []
    for i, athlete in enumerate(athletes):
        rating = athlete.elo_rating
        if is_gi is True:
            rating = athlete.gi_rating
        elif is_gi is False:
            rating = athlete.nogi_rating

        win_rate = 0.0
        if athlete.total_matches > 0:
            win_rate = round(athlete.wins / athlete.total_matches * 100, 1)

        entries.append(
            LeaderboardEntry(
                rank=start_rank + i,
                athlete_id=athlete.id,
                display_name=athlete.display_name,
                country=athlete.country,
                country_code=athlete.country_code,
                gender=athlete.gender,
                elo_rating=rating,
                total_matches=athlete.total_matches,
                wins=athlete.wins,
                losses=athlete.losses,
                win_rate=win_rate,
                photo_url=athlete.photo_url,
            )
        )

    filters = {}
    if sport_id:
        filters["sport_id"] = str(sport_id)
    if weight_class_id:
        filters["weight_class_id"] = str(weight_class_id)
    if gender:
        filters["gender"] = gender
    if country:
        filters["country"] = country

    return LeaderboardResponse(
        entries=entries,
        total_count=total_count,
        page=page,
        page_size=page_size,
        filters_applied=filters,
    )


@router.get("/country/{country_code}", response_model=LeaderboardResponse)
@limiter.limit("30/minute")
async def country_leaderboard(
    request: Request,
    country_code: str,
    db: AsyncSession = Depends(get_db),
    gender: str | None = Query(None, pattern=r"^(male|female|other)$"),
    min_matches: int = Query(1, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(Athlete).where(
        Athlete.is_active == True,
        Athlete.country_code == country_code.upper(),
        Athlete.total_matches >= min_matches,
    )

    if gender:
        query = query.where(Athlete.gender == gender)

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    query = query.order_by(Athlete.elo_rating.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    athletes = result.scalars().all()

    start_rank = (page - 1) * page_size + 1
    entries = []
    for i, athlete in enumerate(athletes):
        win_rate = 0.0
        if athlete.total_matches > 0:
            win_rate = round(athlete.wins / athlete.total_matches * 100, 1)

        entries.append(
            LeaderboardEntry(
                rank=start_rank + i,
                athlete_id=athlete.id,
                display_name=athlete.display_name,
                country=athlete.country,
                country_code=athlete.country_code,
                gender=athlete.gender,
                elo_rating=athlete.elo_rating,
                total_matches=athlete.total_matches,
                wins=athlete.wins,
                losses=athlete.losses,
                win_rate=win_rate,
                photo_url=athlete.photo_url,
            )
        )

    return LeaderboardResponse(
        entries=entries,
        total_count=total_count,
        page=page,
        page_size=page_size,
        filters_applied={"country_code": country_code},
    )
