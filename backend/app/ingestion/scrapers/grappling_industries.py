"""
Grappling Industries scraper — tournament results.
May provide CSV downloads; falls back to HTML scraping.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedMatch, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    extract_name_parts, parse_match_outcome, parse_division, parse_date,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://grapplingindustries.com"


class GrapplingIndustriesIngester(BaseIngester):
    source_name = "grappling-industries"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch past Grappling Industries events."""
        events = []

        html = await self.http.get_html(f"{BASE_URL}/results")
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/past-events")
        if not html:
            logger.warning("Could not fetch Grappling Industries events")
            return events

        soup = BeautifulSoup(html, "lxml")
        for card in soup.select(".event-card, .event, article, .result-item"):
            try:
                name_el = card.select_one("h2, h3, .title, a")
                link_el = card.select_one("a[href]")
                date_el = card.select_one(".date, time")

                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                href = link_el.get("href", "") if link_el else ""

                event_date = date.today()
                if date_el:
                    parsed = parse_date(date_el.get_text(strip=True))
                    if parsed:
                        event_date = parsed

                # Extract city from name ("Grappling Industries NYC")
                city = None
                city_match = re.search(r"(?:Grappling\s+Industries)\s+(.+?)(?:\s+\d{4})?$", name, re.IGNORECASE)
                if city_match:
                    city = city_match.group(1).strip()

                source_id = re.search(r"/(\d+|[\w-]+)/?$", href)

                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="Grappling Industries",
                    tier="local",
                    city=city,
                    is_gi=True,
                    is_nogi=True,
                    source="grappling-industries",
                    source_id=source_id.group(1) if source_id else "",
                    source_url=f"{BASE_URL}{href}" if href.startswith("/") else href,
                ))
            except Exception as e:
                logger.error(f"Error parsing GI event: {e}")

        logger.info(f"Found {len(events)} Grappling Industries events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch results for a Grappling Industries event."""
        html = await self.http.get_html(f"{BASE_URL}/results/{event_id}")
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        title_el = soup.select_one("h1, .event-title")
        event_name = title_el.get_text(strip=True) if title_el else f"Grappling Industries {event_id}"

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="Grappling Industries",
            tier="local",
            is_gi=True,
            is_nogi=True,
            source="grappling-industries",
            source_id=event_id,
        )

        # GI uses round-robin format — parse division results
        for division in soup.select(".division, .category, .bracket, section"):
            div_el = division.select_one("h3, h4, .division-name")
            div_info = {}
            if div_el:
                div_info = parse_division(div_el.get_text(strip=True))

            for row in division.select(".match, .result-row, tr"):
                try:
                    names = row.select(".name, .athlete, td")
                    if len(names) < 2:
                        continue

                    winner_el = row.select_one(".winner, .gold")
                    result_el = row.select_one(".result, .method")

                    name1 = names[0].get_text(strip=True)
                    name2 = names[1].get_text(strip=True)
                    if not name1 or not name2:
                        continue

                    if winner_el:
                        wt = winner_el.get_text(strip=True)
                        w_name, l_name = (name1, name2) if wt in name1 else (name2, name1)
                    else:
                        w_name, l_name = name1, name2

                    w_first, w_last = extract_name_parts(w_name)
                    l_first, l_last = extract_name_parts(l_name)

                    outcome, sub_type = "points", None
                    if result_el:
                        outcome, sub_type = parse_match_outcome(result_el.get_text(strip=True))

                    event.matches.append(ImportedMatch(
                        winner=ImportedAthlete(
                            first_name=w_first, last_name=w_last,
                            belt_rank=div_info.get("belt"),
                            gender=div_info.get("gender", "male"),
                        ),
                        loser=ImportedAthlete(
                            first_name=l_first, last_name=l_last,
                            belt_rank=div_info.get("belt"),
                            gender=div_info.get("gender", "male"),
                        ),
                        outcome=outcome,
                        submission_type=sub_type,
                        is_gi=div_info.get("is_gi", True),
                        division_name=div_el.get_text(strip=True) if div_el else None,
                    ))
                except Exception as e:
                    logger.error(f"Error parsing GI match: {e}")

        logger.info(f"Parsed {len(event.matches)} matches from GI event {event_id}")
        return event
