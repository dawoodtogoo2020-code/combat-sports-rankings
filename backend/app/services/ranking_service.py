"""
Service layer for ranking calculations and leaderboard queries.
"""

from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.athlete import Athlete
from app.models.rating import RatingHistory


async def get_rating_change(
    db: AsyncSession, athlete_id, days: int = 7
) -> float | None:
    """Get the rating change for an athlete over the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(RatingHistory)
        .where(
            RatingHistory.athlete_id == athlete_id,
            RatingHistory.recorded_at >= cutoff,
        )
        .order_by(RatingHistory.recorded_at.asc())
        .limit(1)
    )
    oldest = result.scalar_one_or_none()
    if not oldest:
        return None

    athlete_result = await db.execute(
        select(Athlete.elo_rating).where(Athlete.id == athlete_id)
    )
    current = athlete_result.scalar_one_or_none()
    if current is None:
        return None

    return round(current - oldest.rating_before, 1)


async def get_top_athletes_by_country(
    db: AsyncSession, country_code: str, limit: int = 10
) -> list:
    """Get top ranked athletes for a country."""
    result = await db.execute(
        select(Athlete)
        .where(
            Athlete.country_code == country_code.upper(),
            Athlete.is_active == True,
            Athlete.total_matches >= 1,
        )
        .order_by(Athlete.elo_rating.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_gym_ranking(db: AsyncSession, gym_id, limit: int = 50) -> list:
    """Get ranked athletes within a gym."""
    result = await db.execute(
        select(Athlete)
        .where(Athlete.gym_id == gym_id, Athlete.is_active == True)
        .order_by(Athlete.elo_rating.desc())
        .limit(limit)
    )
    return result.scalars().all()
