"""
SmoothComp scraper — many BJJ/grappling tournaments use SmoothComp for registration and results.
Scrapes publicly available tournament results from smoothcomp.com.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedMatch, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    extract_name_parts, parse_match_outcome, parse_division, normalize_country, parse_date,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://smoothcomp.com"


class SmoothCompIngester(BaseIngester):
    source_name = "smoothcomp"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch recent events from SmoothComp's public event listing."""
        events = []
        # SmoothComp lists events at /en/events or similar
        html = await self.http.get_html(f"{BASE_URL}/en/events?status=past&discipline=bjj")
        if not html:
            logger.warning("Could not fetch SmoothComp events listing")
            return events

        soup = BeautifulSoup(html, "lxml")

        # Parse event cards from the listing page
        for card in soup.select(".event-card, .card, [data-event-id]"):
            try:
                name_el = card.select_one("h3, h4, .event-name, .card-title")
                link_el = card.select_one("a[href*='/event/']")
                date_el = card.select_one(".event-date, .date, time")

                if not name_el or not link_el:
                    continue

                name = name_el.get_text(strip=True)
                href = link_el.get("href", "")
                event_id = re.search(r"/event/(\d+)", href)
                if not event_id:
                    continue

                event_date = date.today()
                if date_el:
                    parsed = parse_date(date_el.get_text(strip=True))
                    if parsed:
                        event_date = parsed

                location_el = card.select_one(".event-location, .location, .venue")
                city, country = None, None
                if location_el:
                    loc_text = location_el.get_text(strip=True)
                    parts = [p.strip() for p in loc_text.split(",")]
                    if len(parts) >= 2:
                        city = parts[0]
                        country = parts[-1]

                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="SmoothComp",
                    tier="regional",
                    city=city,
                    country=country,
                    source="smoothcomp",
                    source_id=event_id.group(1),
                    source_url=f"{BASE_URL}{href}",
                ))
            except Exception as e:
                logger.error(f"Error parsing SmoothComp event card: {e}")
                continue

        logger.info(f"Found {len(events)} events on SmoothComp")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch match results for a specific SmoothComp event."""
        # Try JSON API first (some SmoothComp events expose this)
        json_data = await self.http.get_json(f"{BASE_URL}/api/event/{event_id}/results")
        if json_data:
            return self._parse_json_results(event_id, json_data)

        # Fall back to HTML scraping
        html = await self.http.get_html(f"{BASE_URL}/en/event/{event_id}/results")
        if not html:
            logger.warning(f"Could not fetch SmoothComp event {event_id}")
            return None

        return self._parse_html_results(event_id, html)

    def _parse_json_results(self, event_id: str, data: dict) -> ImportedEvent | None:
        """Parse results from SmoothComp JSON API if available."""
        try:
            event = ImportedEvent(
                name=data.get("name", f"SmoothComp Event {event_id}"),
                event_date=parse_date(data.get("date", "")) or date.today(),
                organizer="SmoothComp",
                source="smoothcomp",
                source_id=event_id,
            )

            for match_data in data.get("matches", []):
                winner_name = match_data.get("winner", {}).get("name", "")
                loser_name = match_data.get("loser", {}).get("name", "")
                if not winner_name or not loser_name:
                    continue

                w_first, w_last = extract_name_parts(winner_name)
                l_first, l_last = extract_name_parts(loser_name)

                outcome, sub_type = parse_match_outcome(match_data.get("result", "points"))

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=match_data.get("gi", True),
                    round_name=match_data.get("round"),
                ))

            return event
        except Exception as e:
            logger.error(f"Error parsing SmoothComp JSON for event {event_id}: {e}")
            return None

    def _parse_html_results(self, event_id: str, html: str) -> ImportedEvent | None:
        """Parse results from SmoothComp HTML results page."""
        soup = BeautifulSoup(html, "lxml")

        # Get event name
        title_el = soup.select_one("h1, .event-title, .event-name")
        event_name = title_el.get_text(strip=True) if title_el else f"SmoothComp Event {event_id}"

        # Get event date
        date_el = soup.select_one(".event-date, time[datetime]")
        event_date = date.today()
        if date_el:
            dt_attr = date_el.get("datetime")
            parsed = parse_date(dt_attr or date_el.get_text(strip=True))
            if parsed:
                event_date = parsed

        event = ImportedEvent(
            name=event_name,
            event_date=event_date,
            organizer="SmoothComp",
            source="smoothcomp",
            source_id=event_id,
            source_url=f"{BASE_URL}/en/event/{event_id}/results",
        )

        # Parse bracket/match results
        # SmoothComp uses bracket tables with match rows
        for match_row in soup.select(".match-result, .bracket-match, tr.match"):
            try:
                athletes = match_row.select(".athlete-name, .competitor-name, .fighter-name, td.name")
                if len(athletes) < 2:
                    continue

                winner_el = match_row.select_one(".winner, .match-winner, .highlighted")
                result_el = match_row.select_one(".match-outcome, .result, .method")

                # Determine winner/loser
                name1 = athletes[0].get_text(strip=True)
                name2 = athletes[1].get_text(strip=True)

                if winner_el:
                    winner_text = winner_el.get_text(strip=True)
                    if winner_text in name1:
                        winner_name, loser_name = name1, name2
                    else:
                        winner_name, loser_name = name2, name1
                else:
                    winner_name, loser_name = name1, name2

                w_first, w_last = extract_name_parts(winner_name)
                l_first, l_last = extract_name_parts(loser_name)

                outcome = "points"
                sub_type = None
                if result_el:
                    outcome, sub_type = parse_match_outcome(result_el.get_text(strip=True))

                # Check division info
                div_el = match_row.select_one(".division, .category")
                is_gi = True
                if div_el:
                    div_info = parse_division(div_el.get_text(strip=True))
                    is_gi = div_info["is_gi"]

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=is_gi,
                ))
            except Exception as e:
                logger.error(f"Error parsing SmoothComp match row: {e}")
                continue

        logger.info(f"Parsed {len(event.matches)} matches from SmoothComp event {event_id}")
        return event
