"""
Combat Sports ELO Rating Engine

Modified ELO system for combat sports that factors in:
- Competition tier/prestige
- Belt rank difference
- Weight class difference
- Age class difference
- Experience difference
- Match outcome type (submission vs decision)
"""

from dataclasses import dataclass
from enum import Enum


class CompetitionTier(str, Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"
    ELITE = "elite"


class MatchOutcome(str, Enum):
    SUBMISSION = "submission"
    POINTS = "points"
    DECISION = "decision"
    ADVANTAGE = "advantage"
    PENALTY = "penalty"
    DQ = "dq"
    WALKOVER = "walkover"
    DRAW = "draw"


@dataclass
class PlayerInfo:
    rating: float
    belt_level: int = 0       # 0=white, 1=blue, 2=purple, 3=brown, 4=black
    weight_kg: float = 0.0
    age: int = 25
    years_experience: int = 0
    total_matches: int = 0


@dataclass
class MatchContext:
    competition_tier: CompetitionTier = CompetitionTier.LOCAL
    outcome: MatchOutcome = MatchOutcome.POINTS
    is_gi: bool = True
    round_name: str | None = None  # "Final", "Semi-Final", etc.
    k_factor_override: float | None = None


@dataclass
class EloResult:
    winner_new_rating: float
    loser_new_rating: float
    winner_change: float
    loser_change: float
    k_factor_used: float
    expected_score_winner: float
    expected_score_loser: float


class EloEngine:
    """Modified ELO engine for combat sports rankings."""

    # Base K-factor
    BASE_K = 32.0

    # Competition tier K-factor multipliers
    TIER_MULTIPLIERS = {
        CompetitionTier.LOCAL: 0.6,
        CompetitionTier.REGIONAL: 0.8,
        CompetitionTier.NATIONAL: 1.0,
        CompetitionTier.INTERNATIONAL: 1.3,
        CompetitionTier.ELITE: 1.6,
    }

    # Outcome type bonus multipliers (applied to winner's gain)
    OUTCOME_MULTIPLIERS = {
        MatchOutcome.SUBMISSION: 1.2,
        MatchOutcome.POINTS: 1.0,
        MatchOutcome.DECISION: 0.9,
        MatchOutcome.ADVANTAGE: 0.85,
        MatchOutcome.PENALTY: 0.7,
        MatchOutcome.DQ: 0.6,
        MatchOutcome.WALKOVER: 0.3,
        MatchOutcome.DRAW: 0.5,
    }

    # Round multipliers (winning in finals worth more)
    ROUND_MULTIPLIERS = {
        "final": 1.3,
        "semi-final": 1.15,
        "semi final": 1.15,
        "quarter-final": 1.05,
        "quarter final": 1.05,
    }

    # Minimum rating floor
    MIN_RATING = 100.0

    # New player K-factor boost (first N matches)
    NEW_PLAYER_THRESHOLD = 15
    NEW_PLAYER_K_BOOST = 1.5

    def calculate(
        self,
        winner: PlayerInfo,
        loser: PlayerInfo,
        context: MatchContext,
        is_draw: bool = False,
    ) -> EloResult:
        """
        Calculate ELO changes for a match.

        Args:
            winner: Winner's info (ignored if draw)
            loser: Loser's info (ignored if draw)
            context: Match context (competition tier, outcome type, etc.)
            is_draw: Whether the match was a draw

        Returns:
            EloResult with new ratings and changes
        """
        # Step 1: Calculate expected scores
        exp_winner = self._expected_score(winner.rating, loser.rating)
        exp_loser = 1.0 - exp_winner

        # Step 2: Actual scores
        if is_draw:
            actual_winner = 0.5
            actual_loser = 0.5
        else:
            actual_winner = 1.0
            actual_loser = 0.0

        # Step 3: Calculate effective K-factor
        k = self._calculate_k_factor(winner, loser, context)

        # Step 4: Apply outcome multiplier
        outcome_mult = self.OUTCOME_MULTIPLIERS.get(context.outcome, 1.0)

        # Step 5: Apply round multiplier
        round_mult = 1.0
        if context.round_name:
            round_mult = self.ROUND_MULTIPLIERS.get(context.round_name.lower(), 1.0)

        # Step 6: Calculate base rating changes
        winner_change = k * outcome_mult * round_mult * (actual_winner - exp_winner)
        loser_change = k * (actual_loser - exp_loser)

        # Step 7: Apply belt rank upset bonus
        belt_bonus = self._belt_upset_bonus(winner, loser)
        winner_change *= belt_bonus

        # Step 8: Apply experience factor
        exp_factor = self._experience_factor(winner, loser)
        winner_change *= exp_factor

        # Step 9: New player boost
        if winner.total_matches < self.NEW_PLAYER_THRESHOLD:
            winner_change *= self.NEW_PLAYER_K_BOOST
        if loser.total_matches < self.NEW_PLAYER_THRESHOLD:
            loser_change *= self.NEW_PLAYER_K_BOOST

        # Step 10: Calculate new ratings with floor
        winner_new = max(self.MIN_RATING, winner.rating + winner_change)
        loser_new = max(self.MIN_RATING, loser.rating + loser_change)

        return EloResult(
            winner_new_rating=round(winner_new, 1),
            loser_new_rating=round(loser_new, 1),
            winner_change=round(winner_new - winner.rating, 1),
            loser_change=round(loser_new - loser.rating, 1),
            k_factor_used=round(k, 2),
            expected_score_winner=round(exp_winner, 4),
            expected_score_loser=round(exp_loser, 4),
        )

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Standard ELO expected score formula."""
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    def _calculate_k_factor(
        self, winner: PlayerInfo, loser: PlayerInfo, context: MatchContext
    ) -> float:
        """Calculate the effective K-factor for this match."""
        if context.k_factor_override is not None:
            return context.k_factor_override

        k = self.BASE_K

        # Apply competition tier multiplier
        tier_mult = self.TIER_MULTIPLIERS.get(context.competition_tier, 1.0)
        k *= tier_mult

        # Higher-rated players have lower K (more stable ratings)
        avg_rating = (winner.rating + loser.rating) / 2.0
        if avg_rating > 2000:
            k *= 0.8
        elif avg_rating > 1800:
            k *= 0.9

        return k

    def _belt_upset_bonus(self, winner: PlayerInfo, loser: PlayerInfo) -> float:
        """
        Bonus multiplier when a lower-belt beats a higher-belt.
        Winning against a higher-ranked belt earns more points.
        """
        belt_diff = loser.belt_level - winner.belt_level
        if belt_diff > 0:
            # Lower belt won against higher belt — upset bonus
            return 1.0 + (belt_diff * 0.15)
        elif belt_diff < 0:
            # Higher belt won against lower belt — slightly reduced gain
            return max(0.7, 1.0 + (belt_diff * 0.05))
        return 1.0

    def _experience_factor(self, winner: PlayerInfo, loser: PlayerInfo) -> float:
        """
        Factor based on experience difference.
        Beating someone more experienced earns more.
        """
        exp_diff = loser.years_experience - winner.years_experience
        if exp_diff > 0:
            return 1.0 + min(exp_diff * 0.05, 0.3)
        return 1.0

    def calculate_cp(
        self,
        placement: int,
        total_competitors: int,
        tier: CompetitionTier,
    ) -> int:
        """
        Calculate Competitor Points (CP) based on placement.

        CP scales with competition tier and number of competitors.
        """
        tier_base = {
            CompetitionTier.LOCAL: 10,
            CompetitionTier.REGIONAL: 25,
            CompetitionTier.NATIONAL: 50,
            CompetitionTier.INTERNATIONAL: 100,
            CompetitionTier.ELITE: 200,
        }

        base = tier_base.get(tier, 10)

        # Size bonus: more competitors = more CP
        size_mult = 1.0 + min(total_competitors / 32.0, 1.0)

        # Placement multiplier
        if placement == 1:
            place_mult = 1.0
        elif placement == 2:
            place_mult = 0.7
        elif placement == 3:
            place_mult = 0.5
        elif placement <= 5:
            place_mult = 0.3
        elif placement <= 8:
            place_mult = 0.15
        else:
            place_mult = 0.05

        return int(base * size_mult * place_mult)

    def recalculate_all(
        self,
        matches: list[dict],
        initial_rating: float = 1200.0,
    ) -> dict[str, float]:
        """
        Recalculate all ratings from scratch given a list of matches in chronological order.

        Args:
            matches: List of dicts with keys: winner_id, loser_id, competition_tier, outcome, etc.
            initial_rating: Starting rating for all athletes

        Returns:
            Dict mapping athlete_id -> final rating
        """
        ratings: dict[str, float] = {}
        match_counts: dict[str, int] = {}

        for match in matches:
            w_id = match["winner_id"]
            l_id = match["loser_id"]

            if w_id not in ratings:
                ratings[w_id] = initial_rating
                match_counts[w_id] = 0
            if l_id not in ratings:
                ratings[l_id] = initial_rating
                match_counts[l_id] = 0

            winner_info = PlayerInfo(
                rating=ratings[w_id],
                belt_level=match.get("winner_belt_level", 0),
                years_experience=match.get("winner_experience", 0),
                total_matches=match_counts[w_id],
            )
            loser_info = PlayerInfo(
                rating=ratings[l_id],
                belt_level=match.get("loser_belt_level", 0),
                years_experience=match.get("loser_experience", 0),
                total_matches=match_counts[l_id],
            )

            ctx = MatchContext(
                competition_tier=CompetitionTier(match.get("competition_tier", "local")),
                outcome=MatchOutcome(match.get("outcome", "points")),
            )

            result = self.calculate(winner_info, loser_info, ctx, is_draw=match.get("is_draw", False))

            ratings[w_id] = result.winner_new_rating
            ratings[l_id] = result.loser_new_rating
            match_counts[w_id] += 1
            match_counts[l_id] += 1

        return ratings
