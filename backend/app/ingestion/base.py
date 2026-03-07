"""
Base data ingestion interface for importing competition data from external sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class ImportedAthlete:
    first_name: str
    last_name: str
    gender: str = "male"
    country: str | None = None
    weight_class: str | None = None
    belt_rank: str | None = None
    gym_name: str | None = None
    source_id: str | None = None


@dataclass
class ImportedMatch:
    winner: ImportedAthlete
    loser: ImportedAthlete
    outcome: str = "points"  # submission, points, decision, advantage, dq, walkover, draw
    submission_type: str | None = None
    winner_score: int | None = None
    loser_score: int | None = None
    is_draw: bool = False
    is_gi: bool = True
    round_name: str | None = None
    division_name: str | None = None
    match_date: datetime | None = None
    source_id: str | None = None


@dataclass
class ImportedEvent:
    name: str
    event_date: date
    end_date: date | None = None
    organizer: str | None = None
    tier: str = "local"
    venue: str | None = None
    city: str | None = None
    country: str | None = None
    is_gi: bool = True
    is_nogi: bool = False
    source: str = "manual"
    source_id: str | None = None
    source_url: str | None = None
    matches: list[ImportedMatch] = field(default_factory=list)


class BaseIngester(ABC):
    """Abstract base for all data ingesters."""

    source_name: str = "unknown"

    @abstractmethod
    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch events from the source."""
        ...

    @abstractmethod
    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch full results for a specific event."""
        ...

    def normalize_outcome(self, raw: str) -> str:
        """Normalize match outcome strings to standard values."""
        raw = raw.lower().strip()
        if any(word in raw for word in ["sub", "submission", "tap", "armbar", "choke", "lock"]):
            return "submission"
        if any(word in raw for word in ["pts", "points", "score"]):
            return "points"
        if any(word in raw for word in ["decision", "ref", "referee"]):
            return "decision"
        if any(word in raw for word in ["adv", "advantage"]):
            return "advantage"
        if any(word in raw for word in ["dq", "disqualif"]):
            return "dq"
        if any(word in raw for word in ["wo", "walkover", "w.o", "bye"]):
            return "walkover"
        if any(word in raw for word in ["draw", "tie"]):
            return "draw"
        return "points"

    def normalize_belt(self, raw: str) -> str:
        """Normalize belt rank strings."""
        raw = raw.lower().strip()
        belt_map = {
            "white": "white",
            "blue": "blue",
            "purple": "purple",
            "brown": "brown",
            "black": "black",
        }
        for key, val in belt_map.items():
            if key in raw:
                return val
        return raw

    def normalize_gender(self, raw: str) -> str:
        """Normalize gender strings."""
        raw = raw.lower().strip()
        if raw in ("m", "male", "men", "man"):
            return "male"
        if raw in ("f", "female", "women", "woman"):
            return "female"
        return "other"
