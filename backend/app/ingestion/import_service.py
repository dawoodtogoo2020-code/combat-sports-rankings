"""
Service to import normalized event/match data into the database.
"""

import uuid
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.athlete import Athlete
from app.models.event import Event
from app.models.match import Match as MatchModel
from app.models.match import MatchOutcome
from app.models.rating import RatingHistory
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome
from app.ingestion.base import ImportedEvent, ImportedAthlete


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)


class ImportService:
    def __init__(self):
        self.elo_engine = EloEngine()

    async def import_event(self, db: AsyncSession, event_data: ImportedEvent) -> dict:
        """Import an event and all its matches into the database."""
        stats = {"athletes_created": 0, "matches_created": 0, "elo_calculated": 0}

        # Create event
        slug = slugify(event_data.name)
        existing = await db.execute(select(Event).where(Event.slug == slug))
        if existing.scalar_one_or_none():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        event = Event(
            name=event_data.name,
            slug=slug,
            event_date=event_data.event_date,
            end_date=event_data.end_date,
            organizer=event_data.organizer,
            tier=event_data.tier,
            venue=event_data.venue,
            city=event_data.city,
            country=event_data.country,
            is_gi=event_data.is_gi,
            is_nogi=event_data.is_nogi,
            source=event_data.source,
            source_id=event_data.source_id,
            source_url=event_data.source_url,
        )
        db.add(event)
        await db.flush()

        # Process matches
        for match_data in event_data.matches:
            winner = await self._find_or_create_athlete(db, match_data.winner)
            if isinstance(winner, Athlete) and winner.id is None:
                stats["athletes_created"] += 1

            loser = await self._find_or_create_athlete(db, match_data.loser)
            if isinstance(loser, Athlete) and loser.id is None:
                stats["athletes_created"] += 1

            await db.flush()

            # Calculate ELO
            winner_info = PlayerInfo(
                rating=winner.gi_rating if match_data.is_gi else winner.nogi_rating,
                total_matches=winner.total_matches,
                years_experience=winner.years_training or 0,
            )
            loser_info = PlayerInfo(
                rating=loser.gi_rating if match_data.is_gi else loser.nogi_rating,
                total_matches=loser.total_matches,
                years_experience=loser.years_training or 0,
            )

            try:
                outcome_enum = EloMatchOutcome(match_data.outcome)
            except ValueError:
                outcome_enum = EloMatchOutcome.POINTS

            ctx = MatchContext(
                competition_tier=CompetitionTier(event_data.tier),
                outcome=outcome_enum,
                is_gi=match_data.is_gi,
                round_name=match_data.round_name,
            )

            elo_result = self.elo_engine.calculate(
                winner_info, loser_info, ctx, is_draw=match_data.is_draw
            )

            # Create match record
            try:
                db_outcome = MatchOutcome(match_data.outcome)
            except ValueError:
                db_outcome = MatchOutcome.POINTS

            match = MatchModel(
                event_id=event.id,
                winner_id=winner.id,
                loser_id=loser.id,
                outcome=db_outcome,
                is_draw=match_data.is_draw,
                submission_type=match_data.submission_type,
                winner_score=match_data.winner_score,
                loser_score=match_data.loser_score,
                is_gi=match_data.is_gi,
                round_name=match_data.round_name,
                match_date=match_data.match_date,
                winner_elo_before=winner_info.rating,
                winner_elo_after=elo_result.winner_new_rating,
                loser_elo_before=loser_info.rating,
                loser_elo_after=elo_result.loser_new_rating,
                elo_change=elo_result.winner_change,
                k_factor_used=elo_result.k_factor_used,
                elo_calculated=True,
                source=event_data.source,
                source_id=match_data.source_id,
            )
            db.add(match)

            # Update athlete ratings and stats
            if match_data.is_gi:
                winner.gi_rating = elo_result.winner_new_rating
                loser.gi_rating = elo_result.loser_new_rating
            else:
                winner.nogi_rating = elo_result.winner_new_rating
                loser.nogi_rating = elo_result.loser_new_rating

            winner.elo_rating = round((winner.gi_rating + winner.nogi_rating) / 2, 1)
            loser.elo_rating = round((loser.gi_rating + loser.nogi_rating) / 2, 1)
            winner.peak_rating = max(winner.peak_rating, winner.elo_rating)
            loser.peak_rating = max(loser.peak_rating, loser.elo_rating)

            if match_data.is_draw:
                winner.draws += 1
                loser.draws += 1
            else:
                winner.wins += 1
                loser.losses += 1
            winner.total_matches += 1
            loser.total_matches += 1

            if match_data.outcome == "submission":
                winner.submissions += 1

            stats["matches_created"] += 1
            stats["elo_calculated"] += 1

        event.matches_imported = True
        return stats

    async def _find_or_create_athlete(
        self, db: AsyncSession, data: ImportedAthlete
    ) -> Athlete:
        """Find existing athlete or create a new one."""
        # Try to find by name match
        result = await db.execute(
            select(Athlete).where(
                Athlete.first_name == data.first_name,
                Athlete.last_name == data.last_name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        # Create new
        athlete = Athlete(
            first_name=data.first_name,
            last_name=data.last_name,
            display_name=f"{data.first_name} {data.last_name}",
            gender=data.gender,
            country=data.country,
        )
        db.add(athlete)
        return athlete
