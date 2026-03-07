"""
CSV-based data ingestion for importing competition results from spreadsheets.

Expected CSV columns:
- event_name, event_date, event_tier, event_city, event_country
- winner_first_name, winner_last_name, winner_gender, winner_country, winner_belt
- loser_first_name, loser_last_name, loser_gender, loser_country, loser_belt
- outcome, submission_type, winner_score, loser_score
- is_gi (true/false), round_name, division_name
"""

import csv
import io
from datetime import date, datetime
from app.ingestion.base import (
    BaseIngester,
    ImportedEvent,
    ImportedMatch,
    ImportedAthlete,
)


class CsvIngester(BaseIngester):
    source_name = "csv"

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        raise NotImplementedError("CSV ingester requires direct file import")

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        raise NotImplementedError("CSV ingester requires direct file import")

    def parse_csv(self, csv_content: str) -> list[ImportedEvent]:
        """Parse a CSV string into ImportedEvent objects, grouped by event."""
        reader = csv.DictReader(io.StringIO(csv_content))
        events: dict[str, ImportedEvent] = {}

        for row in reader:
            event_key = row.get("event_name", "Unknown Event")

            if event_key not in events:
                event_date_str = row.get("event_date", "")
                try:
                    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                except ValueError:
                    event_date = date.today()

                events[event_key] = ImportedEvent(
                    name=event_key,
                    event_date=event_date,
                    organizer=row.get("organizer"),
                    tier=row.get("event_tier", "local"),
                    city=row.get("event_city"),
                    country=row.get("event_country"),
                    is_gi=row.get("is_gi", "true").lower() == "true",
                    is_nogi=row.get("is_gi", "true").lower() != "true",
                    source="csv",
                )

            winner = ImportedAthlete(
                first_name=row.get("winner_first_name", "Unknown"),
                last_name=row.get("winner_last_name", ""),
                gender=self.normalize_gender(row.get("winner_gender", "male")),
                country=row.get("winner_country"),
                belt_rank=self.normalize_belt(row.get("winner_belt", "")),
                gym_name=row.get("winner_gym"),
            )

            loser = ImportedAthlete(
                first_name=row.get("loser_first_name", "Unknown"),
                last_name=row.get("loser_last_name", ""),
                gender=self.normalize_gender(row.get("loser_gender", "male")),
                country=row.get("loser_country"),
                belt_rank=self.normalize_belt(row.get("loser_belt", "")),
                gym_name=row.get("loser_gym"),
            )

            outcome = self.normalize_outcome(row.get("outcome", "points"))

            winner_score = None
            loser_score = None
            try:
                winner_score = int(row.get("winner_score", ""))
            except (ValueError, TypeError):
                pass
            try:
                loser_score = int(row.get("loser_score", ""))
            except (ValueError, TypeError):
                pass

            match = ImportedMatch(
                winner=winner,
                loser=loser,
                outcome=outcome,
                submission_type=row.get("submission_type"),
                winner_score=winner_score,
                loser_score=loser_score,
                is_draw=outcome == "draw",
                is_gi=events[event_key].is_gi,
                round_name=row.get("round_name"),
                division_name=row.get("division_name"),
            )

            events[event_key].matches.append(match)

        return list(events.values())
