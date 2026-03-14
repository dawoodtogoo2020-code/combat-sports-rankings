import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.match import Match
from app.models.athlete import Athlete
from app.models.event import Event
from app.models.rating import RatingHistory
from app.schemas.match import MatchCreate, MatchRead
from app.middleware.auth import require_admin
from app.models.user import User
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome
from app.middleware.rate_limit import limiter

router = APIRouter()
elo_engine = EloEngine()


@router.get("/", response_model=list[MatchRead])
@limiter.limit("30/minute")
async def list_matches(
    request: Request,
    db: AsyncSession = Depends(get_db),
    athlete_id: uuid.UUID | None = None,
    event_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(Match)

    if athlete_id:
        query = query.where(
            (Match.winner_id == athlete_id) | (Match.loser_id == athlete_id)
        )
    if event_id:
        query = query.where(Match.event_id == event_id)

    query = query.order_by(Match.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{match_id}", response_model=MatchRead)
@limiter.limit("60/minute")
async def get_match(request: Request, match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.post("/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(
    data: MatchCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    # Validate athletes exist
    winner_result = await db.execute(select(Athlete).where(Athlete.id == data.winner_id))
    winner = winner_result.scalar_one_or_none()
    if not winner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Winner athlete not found")

    loser_result = await db.execute(select(Athlete).where(Athlete.id == data.loser_id))
    loser = loser_result.scalar_one_or_none()
    if not loser:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loser athlete not found")

    # Validate event exists
    event_result = await db.execute(select(Event).where(Event.id == data.event_id))
    event = event_result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Calculate ELO
    winner_info = PlayerInfo(
        rating=winner.gi_rating if data.is_gi else winner.nogi_rating,
        total_matches=winner.total_matches,
        years_experience=winner.years_training or 0,
    )
    loser_info = PlayerInfo(
        rating=loser.gi_rating if data.is_gi else loser.nogi_rating,
        total_matches=loser.total_matches,
        years_experience=loser.years_training or 0,
    )

    try:
        outcome_enum = EloMatchOutcome(data.outcome)
    except ValueError:
        outcome_enum = EloMatchOutcome.POINTS

    match_context = MatchContext(
        competition_tier=CompetitionTier(event.tier.value),
        outcome=outcome_enum,
        is_gi=data.is_gi,
        round_name=data.round_name,
    )

    elo_result = elo_engine.calculate(winner_info, loser_info, match_context, is_draw=data.is_draw)

    # Create match record
    match = Match(
        **data.model_dump(exclude_unset=True),
        winner_elo_before=winner_info.rating,
        winner_elo_after=elo_result.winner_new_rating,
        loser_elo_before=loser_info.rating,
        loser_elo_after=elo_result.loser_new_rating,
        elo_change=elo_result.winner_change,
        k_factor_used=elo_result.k_factor_used,
        elo_calculated=True,
    )
    db.add(match)

    # Update athlete ratings
    rating_type = "gi" if data.is_gi else "nogi"
    if data.is_gi:
        winner.gi_rating = elo_result.winner_new_rating
        loser.gi_rating = elo_result.loser_new_rating
    else:
        winner.nogi_rating = elo_result.winner_new_rating
        loser.nogi_rating = elo_result.loser_new_rating

    # Update overall rating (average of gi and nogi)
    winner.elo_rating = round((winner.gi_rating + winner.nogi_rating) / 2, 1)
    loser.elo_rating = round((loser.gi_rating + loser.nogi_rating) / 2, 1)

    # Update peak ratings
    winner.peak_rating = max(winner.peak_rating, winner.elo_rating)
    loser.peak_rating = max(loser.peak_rating, loser.elo_rating)

    # Update stats
    if data.is_draw:
        winner.draws += 1
        loser.draws += 1
    else:
        winner.wins += 1
        loser.losses += 1
    winner.total_matches += 1
    loser.total_matches += 1

    if data.outcome == "submission":
        winner.submissions += 1

    # Create rating history entries
    for athlete, before, after in [
        (winner, winner_info.rating, elo_result.winner_new_rating),
        (loser, loser_info.rating, elo_result.loser_new_rating),
    ]:
        history = RatingHistory(
            athlete_id=athlete.id,
            match_id=match.id,
            rating_before=before,
            rating_after=after,
            rating_change=round(after - before, 1),
            rating_type=rating_type,
        )
        db.add(history)

    await db.flush()
    await db.refresh(match)
    return match
