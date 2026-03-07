import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.athlete import Athlete
from app.models.gym import Gym
from app.models.event import Event
from app.models.match import Match
from app.models.social import Post
from app.models.rating import RatingHistory
from app.middleware.auth import require_admin
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome
from pydantic import BaseModel, Field

router = APIRouter()
elo_engine = EloEngine()


class DashboardStats(BaseModel):
    total_athletes: int
    total_gyms: int
    total_events: int
    total_matches: int
    total_users: int
    total_posts: int


class EloAdjustment(BaseModel):
    athlete_id: uuid.UUID
    new_rating: float = Field(ge=100, le=3000)
    reason: str = Field(min_length=1, max_length=500)


class MergeAthletes(BaseModel):
    primary_id: uuid.UUID
    duplicate_id: uuid.UUID


@router.get("/dashboard", response_model=DashboardStats)
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    athletes = await db.execute(select(func.count()).select_from(Athlete))
    gyms = await db.execute(select(func.count()).select_from(Gym))
    events = await db.execute(select(func.count()).select_from(Event))
    matches = await db.execute(select(func.count()).select_from(Match))
    users = await db.execute(select(func.count()).select_from(User))
    posts = await db.execute(select(func.count()).select_from(Post))

    return DashboardStats(
        total_athletes=athletes.scalar(),
        total_gyms=gyms.scalar(),
        total_events=events.scalar(),
        total_matches=matches.scalar(),
        total_users=users.scalar(),
        total_posts=posts.scalar(),
    )


@router.post("/athletes/{athlete_id}/adjust-elo")
async def adjust_elo(
    athlete_id: uuid.UUID,
    data: EloAdjustment,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    old_rating = athlete.elo_rating
    athlete.elo_rating = data.new_rating
    athlete.gi_rating = data.new_rating
    athlete.nogi_rating = data.new_rating
    athlete.peak_rating = max(athlete.peak_rating, data.new_rating)

    # Record adjustment in history
    history = RatingHistory(
        athlete_id=athlete.id,
        rating_before=old_rating,
        rating_after=data.new_rating,
        rating_change=round(data.new_rating - old_rating, 1),
        rating_type="overall",
    )
    db.add(history)

    return {"message": f"Rating adjusted from {old_rating} to {data.new_rating}", "reason": data.reason}


@router.delete("/athletes/{athlete_id}")
async def delete_athlete(
    athlete_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    athlete.is_active = False
    return {"message": "Athlete deactivated"}


@router.post("/athletes/merge")
async def merge_athletes(
    data: MergeAthletes,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    primary = await db.execute(select(Athlete).where(Athlete.id == data.primary_id))
    primary_athlete = primary.scalar_one_or_none()
    if not primary_athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Primary athlete not found")

    duplicate = await db.execute(select(Athlete).where(Athlete.id == data.duplicate_id))
    dup_athlete = duplicate.scalar_one_or_none()
    if not dup_athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Duplicate athlete not found")

    # Move matches from duplicate to primary
    await db.execute(
        update(Match).where(Match.winner_id == data.duplicate_id).values(winner_id=data.primary_id)
    )
    await db.execute(
        update(Match).where(Match.loser_id == data.duplicate_id).values(loser_id=data.primary_id)
    )

    # Move rating history
    await db.execute(
        update(RatingHistory).where(RatingHistory.athlete_id == data.duplicate_id).values(athlete_id=data.primary_id)
    )

    # Merge stats
    primary_athlete.total_matches += dup_athlete.total_matches
    primary_athlete.wins += dup_athlete.wins
    primary_athlete.losses += dup_athlete.losses
    primary_athlete.draws += dup_athlete.draws
    primary_athlete.submissions += dup_athlete.submissions

    # Deactivate duplicate
    dup_athlete.is_active = False

    return {"message": f"Merged {dup_athlete.display_name} into {primary_athlete.display_name}"}


@router.post("/recalculate-rankings")
async def recalculate_rankings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Recalculate all ELO ratings from scratch based on match history."""
    # Reset all athletes to base rating
    await db.execute(
        update(Athlete).values(
            elo_rating=1200.0,
            gi_rating=1200.0,
            nogi_rating=1200.0,
            peak_rating=1200.0,
            wins=0,
            losses=0,
            draws=0,
            submissions=0,
            total_matches=0,
        )
    )

    # Clear rating history
    await db.execute(select(func.count()).select_from(RatingHistory))

    # Get all matches in chronological order
    result = await db.execute(select(Match).order_by(Match.created_at.asc()))
    matches = result.scalars().all()

    processed = 0
    for match in matches:
        winner_result = await db.execute(select(Athlete).where(Athlete.id == match.winner_id))
        winner = winner_result.scalar_one_or_none()
        loser_result = await db.execute(select(Athlete).where(Athlete.id == match.loser_id))
        loser = loser_result.scalar_one_or_none()

        if not winner or not loser:
            continue

        winner_info = PlayerInfo(
            rating=winner.gi_rating if match.is_gi else winner.nogi_rating,
            total_matches=winner.total_matches,
            years_experience=winner.years_training or 0,
        )
        loser_info = PlayerInfo(
            rating=loser.gi_rating if match.is_gi else loser.nogi_rating,
            total_matches=loser.total_matches,
            years_experience=loser.years_training or 0,
        )

        event_result = await db.execute(select(Event).where(Event.id == match.event_id))
        event = event_result.scalar_one_or_none()
        tier = CompetitionTier(event.tier.value) if event else CompetitionTier.LOCAL

        try:
            outcome = EloMatchOutcome(match.outcome.value)
        except (ValueError, AttributeError):
            outcome = EloMatchOutcome.POINTS

        ctx = MatchContext(
            competition_tier=tier,
            outcome=outcome,
            is_gi=match.is_gi,
            round_name=match.round_name,
        )

        elo_result = elo_engine.calculate(winner_info, loser_info, ctx, is_draw=match.is_draw)

        # Update ratings
        if match.is_gi:
            winner.gi_rating = elo_result.winner_new_rating
            loser.gi_rating = elo_result.loser_new_rating
        else:
            winner.nogi_rating = elo_result.winner_new_rating
            loser.nogi_rating = elo_result.loser_new_rating

        winner.elo_rating = round((winner.gi_rating + winner.nogi_rating) / 2, 1)
        loser.elo_rating = round((loser.gi_rating + loser.nogi_rating) / 2, 1)
        winner.peak_rating = max(winner.peak_rating, winner.elo_rating)
        loser.peak_rating = max(loser.peak_rating, loser.elo_rating)

        # Update stats
        if match.is_draw:
            winner.draws += 1
            loser.draws += 1
        else:
            winner.wins += 1
            loser.losses += 1
        winner.total_matches += 1
        loser.total_matches += 1

        if match.outcome and match.outcome.value == "submission":
            winner.submissions += 1

        # Update match record
        match.winner_elo_before = winner_info.rating
        match.winner_elo_after = elo_result.winner_new_rating
        match.loser_elo_before = loser_info.rating
        match.loser_elo_after = elo_result.loser_new_rating
        match.elo_change = elo_result.winner_change
        match.k_factor_used = elo_result.k_factor_used
        match.elo_calculated = True

        processed += 1

    return {"message": f"Recalculated {processed} matches"}


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    query = select(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    role: str = Query(pattern=r"^(user|athlete|gym_owner|admin)$"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target.role = UserRole(role)
    return {"message": f"Role updated to {role}"}


@router.post("/gyms/{gym_id}/verify")
async def verify_gym(
    gym_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Gym).where(Gym.id == gym_id))
    gym = result.scalar_one_or_none()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    gym.is_verified = True
    return {"message": f"Gym '{gym.name}' verified"}


@router.delete("/posts/{post_id}")
async def moderate_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post.is_published = False
    return {"message": "Post hidden"}
