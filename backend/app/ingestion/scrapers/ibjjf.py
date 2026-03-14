"""
IBJJF scraper — International Brazilian Jiu-Jitsu Federation results.
IBJJF is known to be restrictive with data access.
This scraper strictly respects robots.txt and will not proceed if disallowed.
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

BASE_URL = "https://ibjjf.com"


class IbjjfIngester(BaseIngester):
    source_name = "ibjjf"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch events from IBJJF. Respects robots.txt strictly."""
        events = []

        # Check compliance first — IBJJF may block bots
        status = await self.http.compliance.get_robots_status(f"{BASE_URL}/results")
        if status == "disallowed":
            logger.info("IBJJF robots.txt disallows scraping results — skipping")
            return events

        html = await self.http.get_html(f"{BASE_URL}/results")
        if not html:
            logger.warning("Could not fetch IBJJF results page")
            return events

        soup = BeautifulSoup(html, "lxml")
        for card in soup.select(".event-card, .championship-item, .result-event, article"):
            try:
                name_el = card.select_one("h2, h3, .event-name, .title")
                link_el = card.select_one("a[href*='championship'], a[href*='result']")
                date_el = card.select_one(".date, time")

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

                tier = "elite" if "world" in name.lower() else "national" if "pan" in name.lower() or "european" in name.lower() else "regional"

                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="IBJJF",
                    tier=tier,
                    is_gi=True,
                    source="ibjjf",
                    source_id=source_id.group(1) if source_id else "",
                    source_url=f"{BASE_URL}{href}" if href.startswith("/") else href,
                ))
            except Exception as e:
                logger.error(f"Error parsing IBJJF event: {e}")

        logger.info(f"Found {len(events)} IBJJF events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch match results for an IBJJF event."""
        html = await self.http.get_html(f"{BASE_URL}/results/{event_id}")
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        title_el = soup.select_one("h1, .event-title")
        event_name = title_el.get_text(strip=True) if title_el else f"IBJJF Event {event_id}"

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="IBJJF",
            tier="elite",
            is_gi=True,
            source="ibjjf",
            source_id=event_id,
        )

        # IBJJF typically shows brackets per division
        for bracket in soup.select(".bracket, .division-results, .category-bracket"):
            div_el = bracket.select_one(".division-name, .category-name, h3, h4")
            div_info = {}
            if div_el:
                div_info = parse_division(div_el.get_text(strip=True))

            for match_el in bracket.select(".match, .fight, tr"):
                try:
                    names = match_el.select(".athlete, .competitor, .name, td.name")
                    if len(names) < 2:
                        continue

                    winner_el = match_el.select_one(".winner, .gold, .highlighted")
                    result_el = match_el.select_one(".result, .method, .score")

                    name1 = names[0].get_text(strip=True)
                    name2 = names[1].get_text(strip=True)

                    if winner_el:
                        wt = winner_el.get_text(strip=True)
                        if wt in name1:
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
                    logger.error(f"Error parsing IBJJF match: {e}")

        logger.info(f"Parsed {len(event.matches)} matches from IBJJF event {event_id}")
        return event
