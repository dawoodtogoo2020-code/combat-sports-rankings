"""
AJP Tour scraper — Abu Dhabi Jiu-Jitsu Pro tour results.
Scrapes publicly available tournament results from ajptour.com.
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

BASE_URL = "https://ajptour.com"


class AjpIngester(BaseIngester):
    source_name = "ajp"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch events from AJP Tour."""
        events = []

        # Try API first — AJP may expose event data as JSON
        json_data = await self.http.get_json(f"{BASE_URL}/api/events?status=past")
        if json_data and isinstance(json_data, list):
            for item in json_data:
                try:
                    events.append(ImportedEvent(
                        name=item.get("name", ""),
                        event_date=parse_date(item.get("date", "")) or date.today(),
                        organizer="AJP",
                        tier=self._map_tier(item.get("category", "")),
                        city=item.get("city"),
                        country=item.get("country"),
                        is_gi=True,
                        is_nogi=True,
                        source="ajp",
                        source_id=str(item.get("id", "")),
                        source_url=f"{BASE_URL}/events/{item.get('slug', item.get('id', ''))}",
                    ))
                except Exception as e:
                    logger.error(f"Error parsing AJP event JSON: {e}")
            if events:
                return events

        # Fall back to HTML
        html = await self.http.get_html(f"{BASE_URL}/events")
        if not html:
            logger.warning("Could not fetch AJP events page")
            return events

        soup = BeautifulSoup(html, "lxml")
        for card in soup.select(".event-item, .event-card, article"):
            try:
                name_el = card.select_one("h2, h3, .title, .event-title")
                link_el = card.select_one("a[href*='event']")
                date_el = card.select_one(".date, time, .event-date")

                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                href = link_el.get("href", "") if link_el else ""
                source_id = re.search(r"/(\d+)", href)

                event_date = date.today()
                if date_el:
                    parsed = parse_date(date_el.get_text(strip=True))
                    if parsed:
                        event_date = parsed

                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="AJP",
                    tier="international",
                    source="ajp",
                    source_id=source_id.group(1) if source_id else "",
                    source_url=f"{BASE_URL}{href}" if href.startswith("/") else href,
                ))
            except Exception as e:
                logger.error(f"Error parsing AJP event card: {e}")

        logger.info(f"Found {len(events)} AJP events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch match results for an AJP event."""
        # Try JSON API
        json_data = await self.http.get_json(f"{BASE_URL}/api/events/{event_id}/results")
        if json_data:
            return self._parse_json_results(event_id, json_data)

        # HTML fallback
        html = await self.http.get_html(f"{BASE_URL}/events/{event_id}/results")
        if not html:
            return None

        return self._parse_html_results(event_id, html)

    def _parse_json_results(self, event_id: str, data: dict) -> ImportedEvent | None:
        try:
            event = ImportedEvent(
                name=data.get("event_name", f"AJP Event {event_id}"),
                event_date=parse_date(data.get("date", "")) or date.today(),
                organizer="AJP",
                tier=self._map_tier(data.get("category", "")),
                source="ajp",
                source_id=event_id,
            )

            for match in data.get("results", data.get("matches", [])):
                w_name = match.get("winner", match.get("winner_name", ""))
                l_name = match.get("loser", match.get("loser_name", ""))
                if not w_name or not l_name:
                    continue

                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)
                outcome, sub_type = parse_match_outcome(match.get("method", "points"))

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(
                        first_name=w_first, last_name=w_last,
                        country=match.get("winner_country"),
                    ),
                    loser=ImportedAthlete(
                        first_name=l_first, last_name=l_last,
                        country=match.get("loser_country"),
                    ),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=match.get("gi", True),
                    round_name=match.get("round"),
                    division_name=match.get("division"),
                ))

            return event
        except Exception as e:
            logger.error(f"Error parsing AJP JSON results: {e}")
            return None

    def _parse_html_results(self, event_id: str, html: str) -> ImportedEvent | None:
        soup = BeautifulSoup(html, "lxml")

        title_el = soup.select_one("h1, .event-title")
        event_name = title_el.get_text(strip=True) if title_el else f"AJP Event {event_id}"

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="AJP",
            tier="international",
            source="ajp",
            source_id=event_id,
        )

        for row in soup.select(".result-row, .match-result, tr.match, .bracket-match"):
            try:
                names = row.select(".athlete-name, .competitor, .name, td.name")
                if len(names) < 2:
                    continue

                winner_el = row.select_one(".winner, .highlighted, .gold")
                result_el = row.select_one(".method, .result, .outcome")

                name1 = names[0].get_text(strip=True)
                name2 = names[1].get_text(strip=True)

                if winner_el:
                    winner_text = winner_el.get_text(strip=True)
                    if winner_text in name1:
                        w_name, l_name = name1, name2
                    else:
                        w_name, l_name = name2, name1
                else:
                    w_name, l_name = name1, name2

                w_first, w_last = extract_name_parts(w_name)
                l_first, l_last = extract_name_parts(l_name)

                outcome, sub_type = "points", None
                if result_el:
                    outcome, sub_type = parse_match_outcome(result_el.get_text(strip=True))

                event.matches.append(ImportedMatch(
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                ))
            except Exception as e:
                logger.error(f"Error parsing AJP match row: {e}")

        logger.info(f"Parsed {len(event.matches)} matches from AJP event {event_id}")
        return event

    @staticmethod
    def _map_tier(category: str) -> str:
        category = category.lower()
        if "grand slam" in category or "world" in category:
            return "elite"
        if "continental" in category or "national" in category:
            return "national"
        if "international" in category:
            return "international"
        return "regional"
