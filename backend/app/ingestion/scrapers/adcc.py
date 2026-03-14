"""
ADCC scraper — Abu Dhabi Combat Club submission wrestling results.
ADCC events are infrequent (World Championships every 2 years) so this
scraper handles structured results pages from adcombat.com.
"""

import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from app.ingestion.base import BaseIngester, ImportedEvent, ImportedMatch, ImportedAthlete
from app.ingestion.http_client import ScraperHttpClient
from app.ingestion.scrapers.parsers import (
    extract_name_parts, parse_match_outcome, parse_date, normalize_country,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://adcombat.com"


class AdccIngester(BaseIngester):
    source_name = "adcc"

    def __init__(self, http_client: ScraperHttpClient):
        self.http = http_client

    async def fetch_events(self, **kwargs) -> list[ImportedEvent]:
        """Fetch ADCC events listing."""
        events = []

        html = await self.http.get_html(f"{BASE_URL}/adcc-results")
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/results")
        if not html:
            logger.warning("Could not fetch ADCC events page")
            return events

        soup = BeautifulSoup(html, "lxml")
        for card in soup.select("article, .event-item, .result-section, .entry"):
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

                # ADCC events are always elite tier, no-gi
                events.append(ImportedEvent(
                    name=name,
                    event_date=event_date,
                    organizer="ADCC",
                    tier="elite",
                    is_gi=False,
                    is_nogi=True,
                    source="adcc",
                    source_url=f"{BASE_URL}{href}" if href.startswith("/") else href,
                ))
            except Exception as e:
                logger.error(f"Error parsing ADCC event: {e}")

        logger.info(f"Found {len(events)} ADCC events")
        return events

    async def fetch_event_results(self, event_id: str) -> ImportedEvent | None:
        """Fetch results for an ADCC event page."""
        # ADCC results are often on article pages rather than structured data
        html = await self.http.get_html(f"{BASE_URL}/adcc-results/{event_id}")
        if not html:
            html = await self.http.get_html(f"{BASE_URL}/{event_id}")
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        title_el = soup.select_one("h1, .entry-title, .post-title")
        event_name = title_el.get_text(strip=True) if title_el else f"ADCC {event_id}"

        event = ImportedEvent(
            name=event_name,
            event_date=date.today(),
            organizer="ADCC",
            tier="elite",
            is_gi=False,
            is_nogi=True,
            source="adcc",
            source_id=event_id,
        )

        # ADCC results are often in table format or structured text
        # Try tables first
        for table in soup.select("table"):
            for row in table.select("tr")[1:]:  # skip header
                try:
                    cells = row.select("td")
                    if len(cells) < 3:
                        continue

                    # Common patterns: Winner | Method | Loser or Winner vs Loser | Method
                    texts = [c.get_text(strip=True) for c in cells]

                    # Try to identify winner/loser/method
                    w_name, l_name, method = None, None, None
                    if len(texts) >= 3:
                        w_name = texts[0]
                        method = texts[1]
                        l_name = texts[2]

                    if not w_name or not l_name or "vs" in w_name.lower():
                        continue

                    w_first, w_last = extract_name_parts(w_name)
                    l_first, l_last = extract_name_parts(l_name)
                    outcome, sub_type = parse_match_outcome(method or "points")

                    event.matches.append(ImportedMatch(
                        winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                        loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                        outcome=outcome,
                        submission_type=sub_type,
                        is_gi=False,
                    ))
                except Exception as e:
                    logger.error(f"Error parsing ADCC table row: {e}")

        # Also try structured match blocks
        for match_el in soup.select(".match, .result, .fight"):
            try:
                names = match_el.select(".athlete, .fighter, .name")
                if len(names) < 2:
                    continue

                winner_el = match_el.select_one(".winner, .gold")
                result_el = match_el.select_one(".method, .result-method")

                name1 = names[0].get_text(strip=True)
                name2 = names[1].get_text(strip=True)

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
                    winner=ImportedAthlete(first_name=w_first, last_name=w_last),
                    loser=ImportedAthlete(first_name=l_first, last_name=l_last),
                    outcome=outcome,
                    submission_type=sub_type,
                    is_gi=False,
                ))
            except Exception as e:
                logger.error(f"Error parsing ADCC match block: {e}")

        logger.info(f"Parsed {len(event.matches)} matches from ADCC event {event_id}")
        return event
